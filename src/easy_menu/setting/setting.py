import os
import re
import yaml
from urllib2 import urlopen
import arg_parser
from easy_menu.exceptions import SettingError, ConfigError
from easy_menu.util import CaseClass, cmd_util

DEFAULT_CONFIG_NAME = 'easy-menu.yml'
URL_PATTERN = re.compile(r'^http[s]?://')


class Setting(CaseClass):
    """
    Manages all settings.
    """

    def __init__(self, config_path=None, work_dir=None, root_menu=None, encoding=None, cache=None):
        is_url = self._is_url(config_path)
        super(Setting, self).__init__(
            ('config_path', config_path),
            ('work_dir', self._search_work_dir(work_dir, config_path, is_url)),
            ('root_menu', {} if root_menu is None else root_menu),
            ('encoding', encoding),
            ('cache', {} if cache is None else cache)
        )

    def copy(self, **args):
        return Setting(
            config_path=args.get('config_path', self.config_path),
            work_dir=args.get('work_dir', self.work_dir),
            root_menu=args.get('root_menu', self.root_menu),
            encoding=args.get('encoding', self.encoding),
            cache=args.get('cache', self.cache),
        )

    @staticmethod
    def _is_url(path):
        return path is not None and bool(URL_PATTERN.match(path))

    @staticmethod
    def _search_work_dir(work_dir, config_path, is_url):
        if work_dir is None:
            if config_path is not None:
                if not is_url:
                    return os.path.dirname(config_path)
        return work_dir

    def parse_args(self, argv):
        option, args = arg_parser.parser.parse_args(argv[1:])
        path = None

        if not args:
            pass
        elif len(args) == 1:
            path = args[0]
            if not self._is_url(path):
                path = os.path.abspath(path)
        else:
            arg_parser.parser.print_help()
            arg_parser.parser.exit(2)

        return self.copy(config_path=path, work_dir=option.work_dir, encoding=option.encoding)

    def lookup_config(self):
        if self.config_path is None:
            d = os.path.abspath(self.work_dir) if self.work_dir else os.getcwd()

            while True:
                path = os.path.join(d, DEFAULT_CONFIG_NAME)
                if os.path.exists(path):
                    return self.copy(config_path=path)
                nd = os.path.dirname(d)
                if d == nd:
                    break
                d = nd
        return self

    def _load_data(self, is_command, path_or_url_or_cmdline):
        """
        Load data from one file, url or command line, then store to a dict.

        :param is_command: True if using command line output
        :param path_or_url_or_cmdline:
        :return: dict representation of data
        """

        if path_or_url_or_cmdline is None:
            raise SettingError('Not found configuration file.')

        # if already loaded, use cache data
        c = self.cache.get((is_command, path_or_url_or_cmdline))
        if c is not None:
            return c

        try:
            if is_command:
                # execute command
                print('Executing: %s' % path_or_url_or_cmdline)

                # ignore return code and stderr
                data = cmd_util.capture_command(path_or_url_or_cmdline, self.work_dir)[1]
            elif self._is_url(path_or_url_or_cmdline):
                # read from URL
                print('Reading from URL: %s' % path_or_url_or_cmdline)
                data = urlopen(path_or_url_or_cmdline)
            else:
                # read from file
                p = path_or_url_or_cmdline
                if self.work_dir is not None and not os.path.isabs(p):
                    p = os.path.join(self.work_dir, path_or_url_or_cmdline)
                print('Reading file: %s' % p)
                data = open(p)
            menu = yaml.load(data)

            # update cache data
            self.cache[(is_command, path_or_url_or_cmdline)] = menu
        except IOError:
            raise ConfigError('Failed to open: %s' % path_or_url_or_cmdline)
        except yaml.YAMLError as e:
            raise ConfigError('YAML format error: %s: %s' % (path_or_url_or_cmdline, e))
        return menu

    def load_meta(self):
        root_menu = self._load_data(False, self.config_path)

        # overwrite working directory
        work_dir = root_menu.get('meta', {}).get('work_dir')
        return self.copy(work_dir=work_dir)

    def load_config(self):
        """
        Load the configuration file or url.

        If it contains 'include' sections, load them recursively.
        :return: updated Setting instance
        """
        root_menu = self._load_data(False, self.config_path)

        # TODO: verify and evaluate includes
        return self.copy(root_menu=root_menu)
