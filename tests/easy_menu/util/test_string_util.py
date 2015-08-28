# -*- coding: utf-8 -*-

import sys
from easy_menu.util import string_util
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestStringUtil(unittest.TestCase):
    def test_edge_just(self):
        self.assertEqual(string_util.edge_just('', '', 0), ' ')
        self.assertEqual(string_util.edge_just('', '', -1), ' ')
        self.assertEqual(string_util.edge_just('', '', 10), '          ')
        self.assertEqual(string_util.edge_just('', 'abcde', 10), '     abcde')
        self.assertEqual(string_util.edge_just('abc', 'de', 10), 'abc     de')
        self.assertEqual(string_util.edge_just('abcde', 'fghij', 10), 'abcde fghij')

    def test_edge_just_unicode(self):
        self.assertEqual(string_util.edge_just('', u'', 0), ' ')
        self.assertEqual(string_util.edge_just('', u'', -1), ' ')
        self.assertEqual(string_util.edge_just('', u'', 10), '          ')
        self.assertEqual(string_util.edge_just('', u'あいう', 10), u'    あいう')
        self.assertEqual(string_util.edge_just(u'あいu', u'えo', 10), u'あいu  えo')
        self.assertEqual(string_util.edge_just(u'あいう', u'えお', 10), u'あいう えお')
