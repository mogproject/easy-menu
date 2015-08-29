import os
import re
import yaml
from urllib2 import urlopen
import arg_parser
from easy_menu.exceptions import SettingError, ConfigError

DEFAULT_CONFIG_NAME = 'easy-menu.yml'
URL_PATTERN = re.compile(r'^http[s]?://')


class Setting(object):
    """
    Manages all settings.
    """

    def __init__(self, config_path=None, is_url=False, work_dir=None, root_menu=None, encoding=None):
        self.config_path = config_path
        self.is_url = is_url
        self.work_dir = self._search_work_dir(work_dir, config_path, self.is_url)
        self.root_menu = {} if root_menu is None else root_menu
        self.encoding = encoding

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
            path = self._search_config()
        elif len(args) == 1:
            path = args[0]
        else:
            arg_parser.parser.print_help()
            arg_parser.parser.exit(2)

        return Setting(path, bool(URL_PATTERN.match(path)), self.work_dir, self.root_menu, option.encoding)

    @staticmethod
    def _search_config():
        d = os.getcwd()
        while True:
            path = os.path.join(d, DEFAULT_CONFIG_NAME)
            if os.path.exists(path):
                return path
            nd = os.path.dirname(d)
            if d == nd:
                break
            d = nd
        return None

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
        if self.config_path is None:
            raise SettingError('Not found configuration file.')

        root_menu = self._load_url_or_file(self.config_path)

        # TODO: verify and evaluate includes
        return Setting(self.config_path, self.is_url, self.work_dir, root_menu, self.encoding)
