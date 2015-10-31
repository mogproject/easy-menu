from __future__ import division, print_function, absolute_import, unicode_literals

from mog_commons.unittest import TestCase
from easy_menu.entity import *
from easy_menu.setting.loader import Loader


class TestMenu(TestCase):
    def test_parse(self):
        data = {
            'Main menu': [
                {'label 1': 'command 1'},
                {'label 2': 'command 2'},
                {'label 3': [
                    {'command 3': {
                        'work_dir': '/path/to/work2',
                        'env': {'ENV1': 'VAL9', 'ENV3': 'VAL3'}
                    }},
                    'command 4'
                ]},
                {
                    'sub menu': [
                        {'label s1': 'command 5'}
                    ],
                    'meta': {'work_dir': '/tmp2'}
                },
                {'label 9': 'command 9'},
            ],
            'meta': {
                'work_dir': '/path/to/work',
                'env': {'ENV1': 'VAL1', 'ENV2': 'VAL2'}
            }
        }

        root_meta = Meta('/path/to/work', {'ENV1': 'VAL1', 'ENV2': 'VAL2'})
        sub_meta = Meta('/tmp2', {'ENV1': 'VAL1', 'ENV2': 'VAL2'})
        special_meta = Meta('/path/to/work2', {'ENV1': 'VAL9', 'ENV2': 'VAL2', 'ENV3': 'VAL3'})

        expect = Menu('Main menu', [
            Command('label 1', [CommandLine('command 1', root_meta)]),
            Command('label 2', [CommandLine('command 2', root_meta)]),
            Command('label 3', [CommandLine('command 3', special_meta), CommandLine('command 4', root_meta)]),
            Menu('sub menu', [
                Command('label s1', [CommandLine('command 5', sub_meta)])
            ], sub_meta),
            Command('label 9', [CommandLine('command 9', root_meta)]),
        ], root_meta)

        loader = Loader('/tmp')
        self.assertEqual(Menu.parse(data, Meta('/tmp'), loader), expect)
