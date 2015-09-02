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

    def test_unicode_left(self):
        self.assertEqual(string_util.unicode_left('', 3), '')
        self.assertEqual(string_util.unicode_left('abcde', 3), 'abc')
        self.assertEqual(string_util.unicode_left('abcde', -3), '')
        self.assertEqual(string_util.unicode_left('あいうえお', 0), '')
        self.assertEqual(string_util.unicode_left('あいうえお', 1), '')
        self.assertEqual(string_util.unicode_left('あいうえお', 2), 'あ')
        self.assertEqual(string_util.unicode_left('あいうえお', 3), 'あ')
        self.assertEqual(string_util.unicode_left('あいうえお', 4), 'あい')
        self.assertEqual(string_util.unicode_left('あいうえお', 5), 'あい')
        self.assertEqual(string_util.unicode_left('あいうえお', 9), 'あいうえ')
        self.assertEqual(string_util.unicode_left('あいうえお', 10), 'あいうえお')
        self.assertEqual(string_util.unicode_left('あいうえお', 11), 'あいうえお')
        self.assertEqual(string_util.unicode_left('あxいxうxえxお', 4), 'あx')
        self.assertEqual(string_util.unicode_left('あxいxうxえxお', 5), 'あxい')

    def test_unicode_right(self):
        self.assertEqual(string_util.unicode_right('', 3), '')
        self.assertEqual(string_util.unicode_right('abcde', 3), 'cde')
        self.assertEqual(string_util.unicode_right('abcde', -3), '')
        self.assertEqual(string_util.unicode_right('あいうえお', 0), '')
        self.assertEqual(string_util.unicode_right('あいうえお', 1), '')
        self.assertEqual(string_util.unicode_right('あいうえお', 2), 'お')
        self.assertEqual(string_util.unicode_right('あいうえお', 3), 'お')
        self.assertEqual(string_util.unicode_right('あいうえお', 4), 'えお')
        self.assertEqual(string_util.unicode_right('あいうえお', 5), 'えお')
        self.assertEqual(string_util.unicode_right('あいうえお', 9), 'いうえお')
        self.assertEqual(string_util.unicode_right('あいうえお', 10), 'あいうえお')
        self.assertEqual(string_util.unicode_right('あいうえお', 11), 'あいうえお')
        self.assertEqual(string_util.unicode_right('あxいxうxえxお', 4), 'xお')
        self.assertEqual(string_util.unicode_right('あxいxうxえxお', 5), 'えxお')
