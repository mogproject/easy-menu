from __future__ import division, print_function, absolute_import, unicode_literals

import os
import sys
import locale
from mog_commons.case_class import CaseClass
from mog_commons.functional import omap, oget
from mog_commons.string import to_unicode

from easy_menu.setting import arg_parser
from easy_menu.setting.loader import Loader
from easy_menu.entity import Menu, Meta
from easy_menu.exceptions import SettingError, ConfigError

DEFAULT_CONFIG_NAME = os.environ.get('EASY_MENU_CONFIG', 'easy-menu.yml')
EVAL_CACHE_DIR = os.path.join(os.path.expanduser('~'), '.easy-menu', 'eval')


class Setting(CaseClass):
    """
    Manages all settings.
    """

    def __init__(self, config_path=None, work_dir=None, root_menu=None, encoding=None, lang=None, width=None,
                 clear_cache=False, cache_dir=EVAL_CACHE_DIR, stdin=None, stdout=None, stderr=None):
        is_url = Loader.is_url(config_path)
        work_dir = omap(lambda s: to_unicode(s, encoding), self._search_work_dir(work_dir, config_path, is_url))

        CaseClass.__init__(self,
                           ('config_path', config_path),
                           ('work_dir', work_dir),
                           ('root_menu', oget(root_menu, {})),
                           ('encoding', encoding),
                           ('lang', self._find_lang(lang)),
                           ('width', width),
                           ('clear_cache', clear_cache),
                           ('cache_dir', cache_dir),
                           ('stdin', oget(stdin, sys.stdin)),
                           ('stdout', oget(stdout, sys.stdout)),
                           ('stderr', oget(stderr, sys.stderr)))

    @staticmethod
    def _find_lang(lang):
        if not lang:
            # environment LANG is the first priority
            lang = os.environ.get('LANG')
        if not lang:
            lang = locale.getdefaultlocale()[0]
        return lang

    @staticmethod
    def _search_work_dir(work_dir, config_path, is_url):
        if work_dir is None:
            if config_path is not None:
                if not is_url:
                    return os.path.dirname(config_path)
        return work_dir

    def resolve_encoding(self):
        encoding = self.encoding
        if not encoding:
            if hasattr(self.stdout, 'encoding'):
                encoding = self.stdout.encoding
        if not encoding:
            encoding = locale.getpreferredencoding() or 'utf-8'
        return self.copy(encoding=encoding)

    def parse_args(self, argv):
        option, args = arg_parser.parser.parse_args(argv[1:])
        path = None

        if not args:
            pass
        elif len(args) == 1:
            path = args[0]
            if not Loader.is_url(path):
                path = os.path.abspath(path)
        else:
            arg_parser.parser.print_help()
            arg_parser.parser.exit(2)

        return self.copy(config_path=path, work_dir=option.work_dir, encoding=option.encoding, lang=option.lang,
                         width=option.width, clear_cache=option.clear_cache)

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

    def load_config(self):
        """
        Load the configuration file or url.

        If it contains 'include' sections, load them recursively.
        :return: updated Setting instance
        """
        if self.config_path is None:
            raise SettingError('Not found configuration file.')

        loader = Loader(self.work_dir, self.cache_dir, self.encoding, self.stdout, self.clear_cache)
        data = loader.load(False, self.config_path)
        try:
            root_menu = Menu.parse(data, Meta(self.work_dir), loader, self.encoding, 0)
        except (AssertionError, ValueError, TypeError) as e:
            raise ConfigError(self.config_path, e)
        return self.copy(root_menu=root_menu)
