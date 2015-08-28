import os
import yaml
from urllib2 import urlopen
import arg_parser
from easy_menu.exceptions import SettingError


class Setting(object):
    """
    Manages all settings.
    """

    def __init__(self, config_path=None, work_dir=None, root_menu=None):
        self.config_path = config_path
        self.work_dir = work_dir
        self.root_menu = {} if root_menu is None else root_menu

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

        return Setting(path, self.work_dir, self.root_menu)

    @staticmethod
    def _search_config():
        d = os.getcwd()
        while True:
            path = os.path.join(d, 'easy-menu.yml')
            if os.path.exists(path):
                return path
            nd = os.path.dirname(d)
            if d == nd:
                break
            d = nd
        return None

    @staticmethod
    def _load_url_or_file(path):
        try:
            f = urlopen(path)
        except ValueError:  # invalid URL
            f = open(path)
        return yaml.safe_load(f)

    def load_config(self):
        if self.config_path is None:
            raise SettingError('Not found configuration file.')

        menu = self._load_url_or_file(self.config_path)

        # TODO: verify and evaluate includes
        return Setting(self.config_path, self.work_dir, menu)
