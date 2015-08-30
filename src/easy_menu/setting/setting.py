import os
import re
import yaml
from urllib2 import urlopen
import arg_parser
from easy_menu.exceptions import SettingError, ConfigError
from easy_menu.util import CaseClass

DEFAULT_CONFIG_NAME = 'easy-menu.yml'
URL_PATTERN = re.compile(r'^http[s]?://')


class Setting(CaseClass):
    """
    Manages all settings.
    """

    def __init__(self, config_path=None, work_dir=None, root_menu=None, encoding=None):
        is_url = self._is_url(config_path)
        super(Setting, self).__init__(
            ('config_path', config_path),
            ('is_url', is_url),
            ('work_dir', self._search_work_dir(work_dir, config_path, is_url)),
            ('root_menu', {} if root_menu is None else root_menu),
            ('encoding', encoding),
        )

    def copy(self, **args):
        return Setting(
            config_path=args.get('config_path', self.config_path),
            work_dir=args.get('work_dir', self.work_dir),
            root_menu=args.get('root_menu', self.root_menu),
            encoding=args.get('encoding', self.encoding),
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
                    print(path)
                    return self.copy(config_path=path)
                nd = os.path.dirname(d)
                if d == nd:
                    break
                d = nd
        return self

    def _load_url_or_file(self, path):
        try:
            if self.is_url:
                f = urlopen(path)
            else:
                f = open(path)
            config = yaml.load(f)
        except IOError:
            raise ConfigError('Failed to open file: %s' % path)
        except yaml.YAMLError as e:
            raise ConfigError('YAML format error: %s: %s' % (path, e))
        return config

    def load_config(self):
        """
        Load the configuration file or url.

        If it contains 'include' sections, load them recursively.
        :return: updated Setting instance
        """
        if self.config_path is None:
            raise SettingError('Not found configuration file.')

        root_menu = self._load_url_or_file(self.config_path)

        # TODO: verify and evaluate includes
        return self.copy(root_menu=root_menu)
