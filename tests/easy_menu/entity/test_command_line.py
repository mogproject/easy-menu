# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import os
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
        self.assertEqual(CommandLine.parse('cmd 4', Meta(lock=True)), CommandLine('cmd 4', Meta(lock=True)))

    def test_parse_utf8(self):
        self.assertEqual(CommandLine.parse('あいうえお', Meta()), CommandLine('あいうえお', Meta()))
        self.assertEqual(CommandLine.parse({'あいうえお': {
            'env': {'かきく': 'けこ', 'さしす': 'せそ'},
            'work_dir': 'たちつてと'}
        }, Meta()), CommandLine('あいうえお', Meta('たちつてと', {'かきく': 'けこ', 'さしす': 'せそ'})))

    def test_parse_sjis(self):
        self.assertEqual(CommandLine.parse('あいうえお'.encode('sjis'), Meta(), 'sjis'),
                         CommandLine('あいうえお', Meta(), 'sjis'))
        self.assertEqual(CommandLine.parse({'あいうえお'.encode('sjis'): {
            'env': {'かきく'.encode('sjis'): 'けこ'.encode('sjis'), 'さしす'.encode('sjis'): 'せそ'.encode('sjis')},
            'work_dir': 'たちつてと'.encode('sjis'),
        }
        }, Meta(), 'sjis'), CommandLine('あいうえお', Meta('たちつてと', {'かきく': 'けこ', 'さしす': 'せそ'}), 'sjis'))

    def test_parse_error(self):
        self.assertRaisesMessage(
            ValueError, "CommandLine must be string or dict, not list.",
            CommandLine.parse, [], Meta()
        )

    def test_formatted(self):
        self.assertEqual(
            CommandLine('cmd 1', Meta()).formatted(),
            '- cmd: cmd 1\n  cwd: %s' % os.path.abspath(os.path.curdir)
        )
        self.assertEqual(
            CommandLine('cmd 1', Meta('/path/to/work', {'xxx': '111', 'yyy': '222', 'zzz': '333'}, True)).formatted(),
            '- cmd: cmd 1\n  cwd: /path/to/work\n  env: {xxx: 111, yyy: 222, zzz: 333}\n  lock: True'
        )

    def test_to_hash_string(self):
        self.assertEqual(len(CommandLine('cmd 1', Meta(), 'utf-8').to_hash_string()), 32)

        self.assertEqual(CommandLine('cmd 1', Meta(), 'utf-8').to_hash_string(),
                         CommandLine('cmd 1', Meta(), 'sjis').to_hash_string())
        self.assertNotEqual(CommandLine('cmd 1', Meta(), 'utf-8').to_hash_string(),
                            CommandLine('cmd 2', Meta(), 'utf-8').to_hash_string())
        self.assertEqual(CommandLine('cmd 1', Meta('/path/to/work1'), 'utf-8').to_hash_string(),
                         CommandLine('cmd 1', Meta('/path/to/work2'), 'sjis').to_hash_string())
        self.assertEqual(CommandLine('cmd 1', Meta('/path/to/work1', lock=True), 'utf-8').to_hash_string(),
                         CommandLine('cmd 1', Meta('/path/to/work2', lock=False), 'sjis').to_hash_string())
        self.assertNotEqual(CommandLine('cmd 1', Meta(env={'ABC': '123'}), 'utf-8').to_hash_string(),
                            CommandLine('cmd 1', Meta(), 'utf-8').to_hash_string())
        self.assertNotEqual(CommandLine('cmd 1', Meta(env={'ABC': '123'}), 'utf-8').to_hash_string(),
                            CommandLine('cmd 1', Meta(env={'ABC': '123', '': ''}), 'utf-8').to_hash_string())
        self.assertNotEqual(CommandLine('cmd 1', Meta(env={'ABC': '123'}), 'utf-8').to_hash_string(),
                            CommandLine('cmd 1', Meta(env={'ABC': '1234'}), 'utf-8').to_hash_string())
        self.assertEqual(CommandLine('cmd 1', Meta(env={'ABC': '123'}), 'utf-8').to_hash_string(),
                         CommandLine('cmd 1', Meta(env={'ABC': '123'}), 'utf-8').to_hash_string())
