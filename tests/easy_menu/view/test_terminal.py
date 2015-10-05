# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

from easy_menu.view import Terminal
from easy_menu.controller import CommandExecutor
from easy_menu.exceptions import SettingError, EncodingError
from tests.universal import TestCase
from tests.easy_menu.logger.mock_logger import MockLogger
from tests.fake_io import FakeInput


class TestTerminal(TestCase):
    def get_exec(self):
        return CommandExecutor(logger=MockLogger())

    def test_init(self):
        t = Terminal({'': []}, 'host', 'user', self.get_exec())
        self.assertEqual(t.root_menu, {'': []})
        self.assertEqual(t.host, 'host')
        self.assertEqual(t.user, 'user')

    def test_init_error(self):
        self.assertRaises(SettingError, lambda: Terminal({'': []}, 'host', 'user', self.get_exec(), 0))
        self.assertRaises(SettingError, lambda: Terminal({'': []}, 'host', 'user', self.get_exec(), 39))
        self.assertRaises(SettingError, lambda: Terminal({'': []}, 'host', 'user', self.get_exec(), -1))
        self.assertRaises(SettingError, lambda: Terminal({'': []}, 'host', 'user', self.get_exec(), page_size=0))
        self.assertRaises(SettingError, lambda: Terminal({'': []}, 'host', 'user', self.get_exec(), page_size=-1))
        self.assertRaises(SettingError, lambda: Terminal({'': []}, 'host', 'user', self.get_exec(), page_size=10))

    def test_print_error(self):
        t = Terminal({'': []}, 'hose', 'user', self.get_exec(), encoding='ascii', lang='ja')

        with self.withAssertOutput('', '') as (out, err):
            self.assertRaisesRegexp(
                EncodingError,
                '^Failed to print menu: lang=ja, encoding=ascii$',
                lambda: t._print('\n'.join(t._get_header('Header')))
            )

    def test_get_page(self):
        self.maxDiff = None

        t = Terminal({'': []}, 'host', 'user', self.get_exec(), encoding='utf-8', lang='C', width=80)
        self.assertEqual(t.get_page(['title'], [], 0, 1), '\n'.join([
            'Host: host                                                            User: user',
            '================================================================================',
            '  title',
            '--------------------------------------------------------------------------------',
            '------+-------------------------------------------------------------------------',
            '  [0] | Quit',
            '================================================================================',
            'Press menu number (0-0): '
        ]))

        self.assertEqual(t.get_page(['Main Menu', 'title'], [
            {'menu a': 'command a'},
            {'menu b': 'command b'},
            {'menu c': 'command c'},
        ], 0, 1), '\n'.join([
            'Host: host                                                            User: user',
            '================================================================================',
            '  Main Menu > title',
            '--------------------------------------------------------------------------------',
            '  [1] | menu a',
            '  [2] | menu b',
            '  [3] | menu c',
            '------+-------------------------------------------------------------------------',
            '  [0] | Return to Main Menu',
            '================================================================================',
            'Press menu number (0-3): '
        ]))

        self.assertEqual(t.get_page(['title'], [
            {'menu a': 'command a'},
            {'menu b': 'command b'},
            {'menu c': 'command c'},
            {'menu d': 'command d'},
            {'menu e': 'command e'},
            {'menu f': 'command f'},
            {'menu g': 'command g'},
            {'menu h': 'command h'},
            {'menu i': 'command i'},
        ], 0, 100), '\n'.join([
            'Host: host                                                            User: user',
            '================================================================================',
            '  title',
            '--------------------------------------------------------------------------------',
            '                                  Page 1 / 100                            [N] =>',
            '--------------------------------------------------------------------------------',
            '  [1] | menu a',
            '  [2] | menu b',
            '  [3] | menu c',
            '  [4] | menu d',
            '  [5] | menu e',
            '  [6] | menu f',
            '  [7] | menu g',
            '  [8] | menu h',
            '  [9] | menu i',
            '------+-------------------------------------------------------------------------',
            '  [0] | Quit',
            '================================================================================',
            'Press menu number (0-9): '
        ]))

        self.assertEqual(t.get_page(['title'], [
            {'menu a': 'command a'},
            {'menu b': 'command b'},
            {'menu c': 'command c'},
            {'menu d': 'command d'},
            {'menu e': 'command e'},
            {'menu f': 'command f'},
            {'menu g': 'command g'},
            {'menu h': 'command h'},
            {'menu i': 'command i'},
        ], 8, 100), '\n'.join([
            'Host: host                                                            User: user',
            '================================================================================',
            '  title',
            '--------------------------------------------------------------------------------',
            '<= [P]                            Page 9 / 100                            [N] =>',
            '--------------------------------------------------------------------------------',
            '  [1] | menu a',
            '  [2] | menu b',
            '  [3] | menu c',
            '  [4] | menu d',
            '  [5] | menu e',
            '  [6] | menu f',
            '  [7] | menu g',
            '  [8] | menu h',
            '  [9] | menu i',
            '------+-------------------------------------------------------------------------',
            '  [0] | Quit',
            '================================================================================',
            'Press menu number (0-9): '
        ]))

        self.assertEqual(t.get_page(['title'], [
            {'menu a': 'command a'},
        ], 99, 100), '\n'.join([
            'Host: host                                                            User: user',
            '================================================================================',
            '  title',
            '--------------------------------------------------------------------------------',
            '<= [P]                           Page 100 / 100                                 ',
            '--------------------------------------------------------------------------------',
            '  [1] | menu a',
            '------+-------------------------------------------------------------------------',
            '  [0] | Quit',
            '================================================================================',
            'Press menu number (0-1): '
        ]))

    def test_get_page_ja(self):
        self.maxDiff = None

        t = Terminal({'': []}, 'ホスト', 'ユーザ', self.get_exec(), encoding='utf-8', lang='ja_JP', width=80)
        self.assertEqual(t.get_page(['タイトル'], [], 0, 1), '\n'.join([
            'ホスト名: ホスト                                              実行ユーザ: ユーザ',
            '================================================================================',
            '  タイトル',
            '--------------------------------------------------------------------------------',
            '------+-------------------------------------------------------------------------',
            '  [0] | 終了',
            '================================================================================',
            '番号を入力してください (0-0): '
        ]))

        self.assertEqual(t.get_page(['メインメニュー', 'タイトル'], [
            {'メニュー a': 'コマンド a'},
            {'メニュー b': 'コマンド b'},
            {'メニュー c': 'コマンド c'},
        ], 0, 1), '\n'.join([
            'ホスト名: ホスト                                              実行ユーザ: ユーザ',
            '================================================================================',
            '  メインメニュー > タイトル',
            '--------------------------------------------------------------------------------',
            '  [1] | メニュー a',
            '  [2] | メニュー b',
            '  [3] | メニュー c',
            '------+-------------------------------------------------------------------------',
            '  [0] | メインメニュー に戻る',
            '================================================================================',
            '番号を入力してください (0-3): '
        ]))

        self.assertEqual(t.get_page([
            'メインメニュー', 'タイトル1', 'タイトル2', 'タイトル3', 'タイトル4',
            'タイトル5', 'タイトル6', 'タイトル7', 'タイトル8',
        ], [
            {'メニュー a': 'コマンド a'},
            {'メニュー b': 'コマンド b'},
            {'メニュー c': 'コマンド c'},
        ], 0, 1), '\n'.join([
            'ホスト名: ホスト                                              実行ユーザ: ユーザ',
            '================================================================================',
            '  ル2 > タイトル3 > タイトル4 > タイトル5 > タイトル6 > タイトル7 > タイトル8',
            '--------------------------------------------------------------------------------',
            '  [1] | メニュー a',
            '  [2] | メニュー b',
            '  [3] | メニュー c',
            '------+-------------------------------------------------------------------------',
            '  [0] | タイトル7 に戻る',
            '================================================================================',
            '番号を入力してください (0-3): '
        ]))

        self.assertEqual(t.get_page(['タイトル'], [
            {'メニュー a': 'コマンド a'},
            {'メニュー b': 'コマンド b'},
            {'メニュー c': 'コマンド c'},
            {'メニュー d': 'コマンド d'},
            {'メニュー e': 'コマンド e'},
            {'メニュー f': 'コマンド f'},
            {'メニュー g': 'コマンド g'},
            {'メニュー h': 'コマンド h'},
            {'メニュー i': 'コマンド i'},
        ], 0, 100), '\n'.join([
            'ホスト名: ホスト                                              実行ユーザ: ユーザ',
            '================================================================================',
            '  タイトル',
            '--------------------------------------------------------------------------------',
            '                                  Page 1 / 100                            [N] =>',
            '--------------------------------------------------------------------------------',
            '  [1] | メニュー a',
            '  [2] | メニュー b',
            '  [3] | メニュー c',
            '  [4] | メニュー d',
            '  [5] | メニュー e',
            '  [6] | メニュー f',
            '  [7] | メニュー g',
            '  [8] | メニュー h',
            '  [9] | メニュー i',
            '------+-------------------------------------------------------------------------',
            '  [0] | 終了',
            '================================================================================',
            '番号を入力してください (0-9): '
        ]))

        self.assertEqual(t.get_page(['タイトル'], [
            {'メニュー a': 'コマンド a'},
            {'メニュー b': 'コマンド b'},
            {'メニュー c': 'コマンド c'},
            {'メニュー d': 'コマンド d'},
            {'メニュー e': 'コマンド e'},
            {'メニュー f': 'コマンド f'},
            {'メニュー g': 'コマンド g'},
            {'メニュー h': 'コマンド h'},
            {'メニュー i': 'コマンド i'},
        ], 8, 100), '\n'.join([
            'ホスト名: ホスト                                              実行ユーザ: ユーザ',
            '================================================================================',
            '  タイトル',
            '--------------------------------------------------------------------------------',
            '<= [P]                            Page 9 / 100                            [N] =>',
            '--------------------------------------------------------------------------------',
            '  [1] | メニュー a',
            '  [2] | メニュー b',
            '  [3] | メニュー c',
            '  [4] | メニュー d',
            '  [5] | メニュー e',
            '  [6] | メニュー f',
            '  [7] | メニュー g',
            '  [8] | メニュー h',
            '  [9] | メニュー i',
            '------+-------------------------------------------------------------------------',
            '  [0] | 終了',
            '================================================================================',
            '番号を入力してください (0-9): '
        ]))

        self.assertEqual(t.get_page(['タイトル'], [
            {'メニュー a': 'コマンド a'},
        ], 99, 100), '\n'.join([
            'ホスト名: ホスト                                              実行ユーザ: ユーザ',
            '================================================================================',
            '  タイトル',
            '--------------------------------------------------------------------------------',
            '<= [P]                           Page 100 / 100                                 ',
            '--------------------------------------------------------------------------------',
            '  [1] | メニュー a',
            '------+-------------------------------------------------------------------------',
            '  [0] | 終了',
            '================================================================================',
            '番号を入力してください (0-1): '
        ]))

    def test_get_confirm(self):
        self.maxDiff = None

        t = Terminal({'': []}, 'host', 'user', self.get_exec(), encoding='utf-8', lang='C', width=80)
        self.assertEqual(t.get_confirm('description'), '\n'.join([
            'Host: host                                                            User: user',
            '================================================================================',
            '  Confirmation',
            '--------------------------------------------------------------------------------',
            '  Would execute: description',
            '================================================================================',
            'Do you really want to execute? (y/n) [n]: '
        ]))

    def test_get_confirm_ja(self):
        self.maxDiff = None

        t = Terminal({'': []}, 'ホスト', 'ユーザ', self.get_exec(), encoding='utf-8', lang='ja_JP', width=80)
        self.assertEqual(t.get_confirm('メニュー 1'), '\n'.join([
            'ホスト名: ホスト                                              実行ユーザ: ユーザ',
            '================================================================================',
            '  実行確認',
            '--------------------------------------------------------------------------------',
            '  メニュー 1 を行います。',
            '================================================================================',
            'よろしいですか? (y/n) [n]: '
        ]))

    def test_get_before_execute(self):
        self.maxDiff = None

        t = Terminal({'': []}, 'host', 'user', self.get_exec(), encoding='utf-8', lang='C', width=80)
        self.assertEqual(t.get_before_execute('description'), '\n'.join([
            'Host: host                                                            User: user',
            '================================================================================',
            '  Executing: description',
            '--------------------------------------------------------------------------------',
            ''
        ]))

    def test_get_before_execute_ja(self):
        self.maxDiff = None

        t = Terminal({'': []}, 'ホスト', 'ユーザ', self.get_exec(), encoding='utf-8', lang='ja_JP', width=80)
        self.assertEqual(t.get_before_execute('メニュー 1'), '\n'.join([
            'ホスト名: ホスト                                              実行ユーザ: ユーザ',
            '================================================================================',
            '  実行: メニュー 1',
            '--------------------------------------------------------------------------------',
            ''
        ]))

    def test_get_before_after(self):
        self.maxDiff = None

        t = Terminal({'': []}, 'host', 'user', self.get_exec(), encoding='utf-8', lang='C', width=80)
        self.assertEqual(t.get_after_execute(123), '\n'.join([
            '--------------------------------------------------------------------------------',
            'Return code: 123',
            '================================================================================',
            'Press any key to continue...'
        ]))

    def test_get_before_after_ja(self):
        self.maxDiff = None

        t = Terminal({'': []}, 'ホスト', 'ユーザ', self.get_exec(), encoding='utf-8', lang='ja_JP', width=80)
        self.assertEqual(t.get_after_execute(123), '\n'.join([
            '--------------------------------------------------------------------------------',
            'Return code: 123',
            '================================================================================',
            '何かキーを押すとメニューに戻ります...'
        ]))

    def test_wait_input_char(self):
        _in = FakeInput('xyz\x03\n\x04')
        t = Terminal({'': []}, 'host', 'user', self.get_exec(), _input=_in)
        self.assertEqual(t.wait_input_char(), 'x')
        self.assertEqual(t.wait_input_char(), 'y')
        self.assertEqual(t.wait_input_char(), 'z')
        self.assertRaises(KeyboardInterrupt, t.wait_input_char)
        self.assertEqual(t.wait_input_char(), '\n')
        self.assertRaises(KeyboardInterrupt, t.wait_input_char)

    def test_loop(self):
        self.maxDiff = None

        root_menu = {
            'Main menu': [
                {'Menu a': 'echo executing a'},
                {'Menu b': 'echo executing b && exit 130'},
                {'Sub Menu 1': [
                    {'Menu 1': 'echo executing 1'},
                    {'Menu 2': 'echo executing 2'},
                    {'Menu 3': 'echo executing 3'},
                    {'Menu 4': 'echo executing 4'},
                    {'Menu 5': 'echo executing 5'},
                    {'Menu 6': 'echo executing 6'},
                    {'Menu 7': 'echo executing 7'},
                    {'Menu 8': 'echo executing 8'},
                    {'Menu 9': 'echo executing 9'},
                    {'Menu 10': 'echo executing 10'},
                ]},
            ]
        }

        _in = FakeInput(''.join(['1n', '1N', '1\n', '1yx', '2Yx', '3n', '1yx', 'p', '9yx', '0', '-0']))

        # We use a temporary file due to capture the output of subprocess#call.
        with self.withAssertOutputFile('tests/resources/expect/terminal_test_loop.txt') as out:
            t = Terminal(
                root_menu, 'host', 'user', self.get_exec(), _input=_in, _output=out, encoding='utf-8', lang='en_US',
                width=80)
            t.loop()

        self.assertEqual(t.executor.logger.buffer, [
            (6, '[INFO] Command started: echo executing a'),
            (6, '[INFO] Command ended with return code: 0'),
            (6, '[INFO] Command started: echo executing b && exit 130'),
            (6, '[INFO] Command ended with return code: 130'),
            (6, '[INFO] Command started: echo executing 10'),
            (6, '[INFO] Command ended with return code: 0'),
            (6, '[INFO] Command started: echo executing 9'),
            (6, '[INFO] Command ended with return code: 0'),
        ])

    def test_loop_sjis(self):
        self.maxDiff = None

        root_menu = {'メインメニュー': [{'メニュー 1': "echo 'あいうえお'"}]}

        _in = FakeInput(''.join(['1yx', '0']))

        # We use a temporary file due to capture the output of subprocess#call.
        with self.withAssertOutputFile('tests/resources/expect/terminal_test_loop_sjis.txt', encoding='sjis') as out:
            t = Terminal(
                root_menu, 'ホスト', 'ユーザ', self.get_exec(), _input=_in, _output=out, encoding='sjis', lang='ja_JP',
                width=80)
            t.loop()
        self.assertEqual(t.executor.logger.buffer, [
            (6, "[INFO] Command started: echo 'あいうえお'"),
            (6, "[INFO] Command ended with return code: 0"),
        ])

    def test_loop_multiple_commands(self):
        self.maxDiff = None

        root_menu = {'Main Menu': [
            {'Sub Menu 1': [
                {'Menu 1': ['echo 1', 'echo 2']},
            ]},
            {'Sub Menu 2': [
                {'Sub Menu 3': [
                    {'Menu 3': 'echo 3'},
                    {'Menu 4': 'echo 4'}
                ]}, {'Menu 5': 'echo 5'}
            ]},
            {'Menu 6': ['echo 6', 'echo 7', 'false', 'echo 8']}]
        }

        _in = FakeInput(''.join(['1', '.1yx', '0', '21.1yx', '0.0', '3yx', '0']))

        # We use a temporary file due to capture the output of subprocess#call.
        with self.withAssertOutputFile('tests/resources/expect/terminal_test_loop_multiple_commands.txt') as out:
            t = Terminal(
                root_menu,
                'host', 'user', self.get_exec(), _input=_in, _output=out, encoding='utf-8', lang='en_US', width=80)
            t.loop()

        self.assertEqual(t.executor.logger.buffer, [
            (6, '[INFO] Command started: echo 1'),
            (6, '[INFO] Command ended with return code: 0'),
            (6, '[INFO] Command started: echo 2'),
            (6, '[INFO] Command ended with return code: 0'),
            (6, '[INFO] Command started: echo 3'),
            (6, '[INFO] Command ended with return code: 0'),
            (6, '[INFO] Command started: echo 6'),
            (6, '[INFO] Command ended with return code: 0'),
            (6, '[INFO] Command started: echo 7'),
            (6, '[INFO] Command ended with return code: 0'),
            (6, '[INFO] Command started: false'),
            (6, '[INFO] Command ended with return code: 1'),
        ])
