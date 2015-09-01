# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from easy_menu.util import string_util
from tests.universal import TestCase


class TestStringUtil(TestCase):
    def test_unicode_width(self):
        self.assertEqual(string_util.unicode_width(b'abc'), 3)
        self.assertEqual(string_util.unicode_width('あいう'.encode('utf-8')), 9)
        self.assertEqual(string_util.unicode_width('あいう'), 6)

    def test_to_unicode(self):
        self.assertEqual(string_util.to_unicode(b'abc'), 'abc')
        self.assertEqual(string_util.to_unicode('あいう'), 'あいう')
        self.assertEqual(string_util.to_unicode(1.23), '1.23')

    def test_edge_just(self):
        self.assertEqual(string_util.edge_just('', '', 0), ' ')
        self.assertEqual(string_util.edge_just('', '', -1), ' ')
        self.assertEqual(string_util.edge_just('', '', 10), '          ')
        self.assertEqual(string_util.edge_just('', 'abcde', 10), '     abcde')
        self.assertEqual(string_util.edge_just('abc', 'de', 10), 'abc     de')
        self.assertEqual(string_util.edge_just('abcde', 'fghij', 10), 'abcde fghij')

    def test_edge_just_unicode(self):
        self.assertEqual(string_util.edge_just('', '', 0), ' ')
        self.assertEqual(string_util.edge_just('', '', -1), ' ')
        self.assertEqual(string_util.edge_just('', '', 10), '          ')
        self.assertEqual(string_util.edge_just('', 'あいう', 10), '    あいう')
        self.assertEqual(string_util.edge_just('あいu', 'えo', 10), 'あいu  えo')
        self.assertEqual(string_util.edge_just('あいう', 'えお', 10), 'あいう えお')
