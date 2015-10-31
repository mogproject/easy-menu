# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from mog_commons.unittest import TestCase
from easy_menu.entity import CommandLine, Meta


class TestCommandLine(TestCase):
    def test_parse(self):
        self.assertEqual(CommandLine.parse('cmd 1', Meta()), CommandLine('cmd 1', Meta()))
        self.assertEqual(CommandLine.parse({'cmd 2': {'work_dir': '/path/to/work_dir'}}, Meta()),
                         CommandLine('cmd 2', Meta('/path/to/work_dir')))
        self.assertEqual(CommandLine.parse({'cmd 3': {'env': {'xxx': '123', 'yyy': '234'}}}, Meta()),
                         CommandLine('cmd 3', Meta(env={'xxx': '123', 'yyy': '234'})))
        self.assertEqual(CommandLine.parse({'cmd 3': {'env': {'xxx': '123', 'yyy': '234'}, 'work_dir': '/work'}},
                                           Meta()),
                         CommandLine('cmd 3', Meta('/work', {'xxx': '123', 'yyy': '234'})))

    def test_parse_utf8(self):
        self.assertEqual(CommandLine.parse('あいうえお', Meta()), CommandLine('あいうえお', Meta()))
        self.assertEqual(CommandLine.parse({'あいうえお': {
            'env': {'かきく': 'けこ', 'さしす': 'せそ'},
            'work_dir': 'たちつてと'}
        }, Meta()), CommandLine('あいうえお', Meta('たちつてと', {'かきく': 'けこ', 'さしす': 'せそ'})))

    def test_parse_sjis(self):
        self.assertEqual(CommandLine.parse('あいうえお'.encode('sjis'), Meta(), 'sjis'), CommandLine('あいうえお', Meta()))
        self.assertEqual(CommandLine.parse({'あいうえお'.encode('sjis'): {
            'env': {'かきく'.encode('sjis'): 'けこ'.encode('sjis'), 'さしす'.encode('sjis'): 'せそ'.encode('sjis')},
            'work_dir': 'たちつてと'.encode('sjis')}
        }, Meta(), 'sjis'), CommandLine('あいうえお', Meta('たちつてと', {'かきく': 'けこ', 'さしす': 'せそ'})))

    def test_parse_error(self):
        self.assertRaisesMessage(
            ValueError, "CommandLine must be string or dict, not list.",
            CommandLine.parse, [], Meta()
        )
