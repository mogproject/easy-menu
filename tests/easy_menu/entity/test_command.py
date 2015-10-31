# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from mog_commons.unittest import TestCase
from easy_menu.entity import Command, CommandLine, Meta


class TestCommand(TestCase):
    def test_parse(self):
        self.assertEqual(Command.parse({'label 1': 'cmd 1'}, Meta()),
                         Command('label 1', [CommandLine('cmd 1', Meta())]))
        self.assertEqual(Command.parse(
            {'label 2': [
                {'cmd 2': {'env': {'xxx': '123', 'yyy': '234'}, 'work_dir': '/work'}},
                {'cmd 3': {'env': {'xxx': '123', 'zzz': '345'}, 'work_dir': '/work2'}},
            ]}, Meta()
        ), Command('label 2', [
            CommandLine('cmd 2', Meta('/work', {'xxx': '123', 'yyy': '234'})),
            CommandLine('cmd 3', Meta('/work2', {'xxx': '123', 'zzz': '345'})),
        ]))

    def test_parse_error(self):
        self.assertRaisesMessage(
            ValueError, 'Command should have only one element, not 2.',
            Command.parse, {'label 1': 'cmd 1', 'label 2': 'cmd 2'}, Meta()
        )

        self.assertRaisesMessage(
            ValueError, 'Invalid command content type: dict',
            Command.parse, {'label 1': {'a': 'b'}}, Meta()
        )
