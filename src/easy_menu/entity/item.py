from __future__ import division, print_function, absolute_import, unicode_literals

from abc import ABCMeta, abstractmethod
import six
from mog_commons.case_class import CaseClass
from mog_commons.collection import get_single_item
from mog_commons.types import *
from easy_menu.entity.meta import Meta
from easy_menu.setting.loader import Loader


@six.add_metaclass(ABCMeta)
class Item(CaseClass):
    """
    Abstract item class
    """

    @staticmethod
    def _is_command_like(content):
        """
        We assume the data is command when it is a string or one-element dict which contains string key and dict value
        :param content: object to parse
        :return: true when the data is command-like
        """
        if isinstance(content, six.string_types):
            return True

        if isinstance(content, list):
            for item in content:
                ok = False
                if isinstance(item, six.string_types):
                    ok = True
                if isinstance(item, dict) and len(item) == 1:
                    cmd, attr = get_single_item(item)
                    ok = isinstance(cmd, six.string_types) and isinstance(attr, dict)
                if not ok:
                    return False
            return True

        return False

    @staticmethod
    @types(data=dict, meta=Meta, loader=Loader)
    def parse(data, meta, loader, encoding='utf-8', depth=0):
        """
        :param data:
        :param meta:
        :param loader:
        :param encoding:
        :param depth: indicator for the nesting level
        :return:
        """
        from easy_menu.entity import Menu, Command, KEYWORD_META, KEYWORD_INCLUDE, KEYWORD_EVAL

        # avoid for inclusion loops and stack overflow
        assert depth < 50, 'Nesting level too deep.'

        # if the data has meta key, it should be a menu.
        if KEYWORD_META in data:
            return Menu.parse(data, meta, loader, encoding, depth)

        # parse eval cache setting
        eval_expire = None
        if KEYWORD_EVAL in data:
            if 'cache' in data:
                eval_expire = data['cache']
                del data['cache']

        assert len(data) == 1, 'Item should have only one element, not %s.' % len(data)

        title, content = get_single_item(data)

        if title == KEYWORD_INCLUDE:
            assert isinstance(content, six.string_types), \
                '"include" section must have string content, not %s.' % type(content).__name__
            return Menu.parse(loader.load(False, content), meta, loader, encoding, depth)
        elif title == KEYWORD_EVAL:
            assert isinstance(content, six.string_types), \
                '"eval" section must have string content, not %s.' % type(content).__name__
            return Menu.parse(loader.load(True, content, eval_expire), meta, loader, encoding, depth)
        elif Item._is_command_like(content):
            return Command.parse(data, meta, loader, encoding, depth)
        else:
            return Menu.parse(data, meta, loader, encoding, depth)

    @abstractmethod
    def formatted(self):
        """abstract method"""
