from __future__ import division, print_function, absolute_import, unicode_literals

import six
from mog_commons.case_class import CaseClass
from mog_commons.string import to_unicode, is_unicode
from mog_commons.collection import get_single_item
from easy_menu.entity import Command, Meta


class Menu(CaseClass):
    """
    Menu is built from an one-element dict having title string as key and item list element as value
    """

    def __init__(self, title, items, meta):
        """
        :param title:
        :param items:
        :param meta:
        :return:
        """
        assert is_unicode(title)
        assert isinstance(items, list) and all(isinstance(x, Menu) or isinstance(x, Command) for x in items)
        assert isinstance(meta, Meta)

        CaseClass.__init__(self,
                           ('title', title),
                           ('items', items),
                           ('meta', meta))

    @staticmethod
    def parse(data, meta, loader, encoding='utf-8', depth=0):
        """

        :param data:
        :param meta:
        :param loader:
        :param encoding:
        :param depth:
        :return:
        """
        from easy_menu.entity import KEYWORD_META, Item

        assert isinstance(data, dict), 'Menu must be dict, not %s.' % type(data).__name__
        assert isinstance(meta, Meta)

        # read meta configurations
        if KEYWORD_META in data:
            meta = meta.updated(data[KEYWORD_META], encoding)
            del data[KEYWORD_META]

        assert len(data) == 1, 'Menu should have only one item, not %s.' % len(data)

        title, content = get_single_item(data)
        assert isinstance(title, six.string_types), 'Menu title must be string, not %s.' % type(title).__name__
        assert isinstance(content, list), 'Menu content must be list, not %s.' % type(content).__name__
        title = to_unicode(title, encoding)

        items = [Item.parse(item, meta, loader, encoding, depth + 1) for item in content]
        return Menu(title, items, meta)
