# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import six
from mog_commons.unittest import TestCase
from easy_menu.entity import Item, Meta
from easy_menu.setting.loader import Loader


class TestItem(TestCase):
    def test_parse_error(self):
        self.assertRaisesMessage(
            AssertionError, "Item must be dict, not %s." % ('unicode' if six.PY2 else 'str'),
            Item.parse, {'a': ['b', {}]}, Meta(), Loader('.')
        )
