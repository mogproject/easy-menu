# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
from easy_menu.util import term_util
from tests.universal import TestCase, unittest
from tests.fake_io import FakeBytesInput


class TestTermUtil(TestCase):

    @unittest.skipUnless(os.name != 'nt', 'requires POSIX compatible')
    def test_getch(self):
        self.assertEqual(term_util.getch(FakeBytesInput(b'')), '')
        self.assertEqual(term_util.getch(FakeBytesInput(b'\x03')), '\x03')
        self.assertEqual(term_util.getch(FakeBytesInput(b'abc')), 'a')
        self.assertEqual(term_util.getch(FakeBytesInput('あ'.encode('utf-8'))), '')
        self.assertEqual(term_util.getch(FakeBytesInput('あ'.encode('sjis'))), '')
