# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from mog_commons.unittest import TestCase
from easy_menu.entity import Meta


class TestMeta(TestCase):
    def test_updated(self):
        m1 = Meta()
        m2 = m1.updated({'work_dir': '/path/to/work_dir', 'env': {'xxx': '123', 'yyy': '234'}, 'lock': True}, 'utf-8')
        m3 = m2.updated({'work_dir': '/tmp2', 'env': {'xxx': '789', 'zzz': '345'}, 'lock': False}, 'utf-8')
        self.assertEqual(m1, Meta(None, {}))
        self.assertEqual(m2, Meta('/path/to/work_dir', {'xxx': '123', 'yyy': '234'}, True))
        self.assertEqual(m3, Meta('/tmp2', {'xxx': '789', 'yyy': '234', 'zzz': '345'}, False))

    def test_updated_error(self):
        self.assertRaisesMessage(
            ValueError, "Unknown field: a",
            Meta().updated, {'a': 'b'}, 'utf-8'
        )
