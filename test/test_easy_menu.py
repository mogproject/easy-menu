#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Easy Menu Tests."""

import sys
import os
import unittest
import re

# Version settings.
PROGRAM_VERSION = '0.0.2'

# Path settings.
SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')

sys.path[0:0] = [ROOT_DIR, ]
import easy_menu


# Functions.
def remove_file(path):
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            print('Cannot remove: %s' % path)


def read_file(path):
    file_object = open(path)
    try:
        data = file_object.read()
    finally:
        file_object.close()
    return data


def customized_exit(code):
    raise ExitException(code)


class CustomizedTestCase(unittest.TestCase):
    """Extension for TestCase class"""
    def assertExceptionMessage(self, exception_class, message, callable_obj):
        """Test exception and its message without context manager"""
        try:
            callable_obj()
        except exception_class, e:
            self.assertEqual(e.args[0], message)
        except Exception, e:
            self.fail('Unexpected exception raised: %s' % e)
        else:
            self.fail('%s not raised' % exception_class.__name__)


class ExitException(Exception):
    def __init__(self, code):
        self.code = code


class Output(object):
    """Emulate file output"""
    def __init__(self):
        self._buf = []

    def fileno(self):
        return 1

    def write(self, text):
        self._buf.append(text)

    def flush(self):
        pass

    def read(self):
        return ''.join(self._buf)


class TestPrompt(unittest.TestCase):
    """Test Prompt class."""
    def setUp(self):
        unittest.TestCase.setUp(self)

        def unicode_width(s):
            from unicodedata import east_asian_width
            width = {'F': 2, 'H': 1, 'W': 2, 'Na': 1, 'A': 2, 'N': 1}
            return sum(width[east_asian_width(c)] for c in s)

        import socket
        import getpass

        host = u'ホスト名: ' + socket.gethostname()
        user = u'実行ユーザ: ' + getpass.getuser()
        padding = max(1, 80 - unicode_width(host + user))
        self._header = host + ' ' * padding + user

    def test_prompt(self):
        prompt = easy_menu.Prompt()

        self.assertEqual(
            prompt.make_menu([{'name': u'名前', 'item': [u'アイテム', {}]}]),
            '\n'.join([
                self._header,
                '=' * 80,
                u'  名前',
                '-' * 80,
                u'  1 | アイテム',
                '----+' + '-' * 75,
                u'  0 | 終了',
                '=' * 80,
                u'番号を入力してください (0-1): '
            ])
        )
        print('Prompt: Make root menu string ... OK')

        self.assertEqual(
            prompt.make_menu([
                {'name': u'ルートメニュー'},
                {'name': u'名前', 'item': [u'アイテム', {}]}
            ]),
            '\n'.join([
                self._header,
                '=' * 80,
                u'  名前',
                '-' * 80,
                u'  1 | アイテム',
                '----+' + '-' * 75,
                u'  0 | ルートメニュー に戻る',
                '=' * 80,
                u'番号を入力してください (0-1): '
            ])
        )
        print('Prompt: Make sub menu string ... OK')

        self.assertEqual(
            prompt.make_confirm(u'説明'),
            '\n'.join([
                self._header,
                '=' * 80,
                u'  実行確認',
                '-' * 80,
                u'  説明 を行います。',
                '=' * 80,
                u'よろしいですか? (y/n) [n]: '
            ])
        )
        print('Prompt: Make confirmation string ... OK')

        self.assertEqual(
            prompt.make_command_start(u'コマンド'),
            '\n'.join([
                self._header,
                '=' * 80,
                u'  実行: コマンド',
                '-' * 80,
                ''
            ])
        )
        print('Prompt: Make command-start string ... OK')

        self.assertEqual(
            prompt.make_command_end(9),
            '\n'.join([
                '-' * 80,
                'Return code: 9',
                '=' * 80,
                u'Enterキーを入力するとメニューに戻ります...'
            ])
        )
        print('Prompt: Make command-end string ... OK')


class TestEasyMenu(CustomizedTestCase):
    """Test EasyMenu class."""
    def _check_operation(
        self, description, dir_name, encoding, expected_output, expected_log
    ):
        base_dir = SCRIPT_DIR + '/' + dir_name
        config_path = base_dir + '/config.json'
        input_path = base_dir + '/input.txt'
        output_path = base_dir + '/output.log'
        log_path = base_dir + '/easy_menu.log'

        sys.stdout.write('%s: Output ... ' % description)

        # Clear files.
        remove_file(output_path)
        remove_file(log_path)

        # Start menu.
        in_file = open(input_path)
        out_file = open(output_path, 'w')

        try:
            em = easy_menu.EasyMenu(
                config_path, log_path, encoding, in_file, out_file)
            em.start()
        except Exception, e:
            raise e
        finally:
            in_file.close()
            out_file.close()

            # Check output.
            out_text = read_file(output_path)
            self.assertEqual(expected_output, out_text)
            print('OK')

            # Check log.
            sys.stdout.write('%s: Log ... ' % description)
            self._check_log(log_path, expected_log)
            print('OK')

            # Clear files.
            remove_file(output_path)
            remove_file(log_path)

    def _check_log(self, log_path, expected):
        datetime_format = '\d{4|-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}'
        log_format = '^\[%s\] %%s$' % datetime_format
        expected.append('')

        log_data = read_file(log_path).split('\n')
        self.assertEqual(
            len(expected), len(log_data),
            'Unexpected log length.'
        )
        for i, line in enumerate(expected):
            if line == '':
                self.assertEqual(line, log_data[i], 'Unexpected log entry.')
            else:
                self.assertTrue(
                    re.search(log_format % line, log_data[i]),
                    'Unexpected log entry.'
                )

    def test_logger_error(self):
        log_path = SCRIPT_DIR + '/i/n/v/a/l/i/d/'
        self.assertFalse(os.path.exists(log_path))
        self.assertExceptionMessage(
            IOError, 2,
            lambda: easy_menu.EasyMenu(log_path=log_path).start()
        )
        print('Logger: Invalid file path ... OK')

    def test_encode_error(self):
        def f():
            self._check_operation(
                'EncodeError', 'encode_error', 'UNKNOWN', '', [
                    'INFO Script started\.',
                    'WARNING Script ended with error: ' +
                    'Encode error: unknown encoding: UNKNOWN'
                ]
            )

        self.assertExceptionMessage(
            easy_menu.EncodeError, 'Encode error: unknown encoding: UNKNOWN', f
        )

    def test_interrupt_error(self):
        # Make expected output.
        prompt = easy_menu.Prompt()
        menu = prompt.make_menu([{'name': '', 'item': ['', '']}])
        expected_output = (menu * 2).encode('utf-8')

        self._check_operation(
            'InterruptError', 'interrupt_error', 'utf-8',
            expected_output, [
                'INFO Script started\.',
                'WARNING Script was interrupted\.'
            ]
        )

    def test_skelton(self):
        # Make expected output.
        prompt = easy_menu.Prompt()
        menu = prompt.make_menu([{'name': '', 'item': ['', '']}])
        confirm = prompt.make_confirm('')
        command = prompt.make_command_start('') + prompt.make_command_end(0)
        expected_output = (
            menu * 10 + (confirm + menu) * 8 + (confirm + command + menu) * 6
        ).encode('utf-8')

        # Make expected log.
        expected_log = [
            'INFO Script started\.'
        ] + [
            'INFO Command started: ',
            'INFO Command ended with return code: 0',
        ] * 6 + [
            'INFO Script ended normally.'
        ]

        self._check_operation(
            'Skeleton', 'skeleton', 'utf-8', expected_output, expected_log
        )

    def test_nested_menu(self):
        # Make expected output.
        prompt = easy_menu.Prompt()
        menu1 = prompt.make_menu([{'name': 'menu1', 'item': ['item1', {}]}])
        menu2 = prompt.make_menu([
            {'name': 'menu1', 'item': ['item1', {}]},
            {'name': 'menu2', 'item': ['item2', {}]}
        ])
        menu3 = prompt.make_menu([
            {'name': 'menu2', 'item': ['item2', {}]},
            {'name': 'menu3', 'item': ['item3', '']}
        ])
        confirm = prompt.make_confirm('item3')
        command = (
            prompt.make_command_start('item3') + prompt.make_command_end(0)
        )
        expected_output = (
            menu1 + menu2 + menu3 + confirm + command + menu3 + menu2 + menu1
        ).encode('utf-8')

        self._check_operation(
            'NestedMenu', 'nested_menu', 'utf-8',
            expected_output, [
                'INFO Script started\.',
                'INFO Command started: ',
                'INFO Command ended with return code: 0',
                'INFO Script ended normally.'
            ]
        )

    def test_command_output(self):
        # Make expected output.
        prompt = easy_menu.Prompt()
        menu = prompt.make_menu([
            {"name": "NAME", "item": ["a", "echo x", "b", "exit 2"]}
        ])
        expected_output = u''.join([
            menu,
            prompt.make_confirm('a'),
            prompt.make_command_start('a'),
            'x\n',
            prompt.make_command_end(0),
            menu,
            prompt.make_confirm('b'),
            prompt.make_command_start('b'),
            prompt.make_command_end(2),
            menu
        ]).encode('utf-8')

        # Make expected log.
        expected_log = [
            'INFO Script started\.',
            'INFO Command started: echo x',
            'INFO Command ended with return code: 0',
            'INFO Command started: exit 2',
            'INFO Command ended with return code: 2',
            'INFO Script ended normally.'
        ]

        self._check_operation(
            'CommandOutput', 'command_output', 'utf-8',
            expected_output, expected_log
        )

    def test_config_error(self):
        """Test configuration file error."""
        expected_messages = {  # Case name: (filename, exception message)
            'File open error': (
                'INVALID_FILE_NAME',
                'Failed to open file: %s/config_error/INVALID_FILE_NAME'
                % SCRIPT_DIR),
            'JSON format error': (
                'invalid_format_config.json',
                'JSON format error: %s/config_error/invalid_format_config.json'
                % SCRIPT_DIR),
            'No name key': (
                'no_name_config.json',
                'Menu must have "name" key.'),
            'No item key': (
                'no_item_config.json',
                'Menu must have "item" key.'),
            'Name value type error': (
                'invalid_name_type_config.json',
                'Menu name must be string.'),
            'Item value type error': (
                'invalid_item_type_config.json',
                'Menu item must be list.'),
            'Odd number items': (
                'odd_number_items_config.json',
                'Menu must have even number items.'),
            'Empty items': (
                'empty_items_config.json',
                'Menu item length must be between 1 and 16.'),
            'Too many items': (
                'too_many_items_config.json',
                'Menu item length must be between 1 and 16.'),
            'Command description type error': (
                'command_desc_type_error_config.json',
                'Command description must be string.'),
            'Command type error': (
                'command_type_error_config.json',
                'Command must be string.'),
            'Nested two level with error': (
                'nested_two_levels_config.json',
                'Command must be string.'),
            'Nested ten level with error': (
                'nested_ten_levels_config.json',
                'Command must be string.'),
        }

        self.assertFalse(os.path.exists('INVALID_FILE_NAME'))

        for case in expected_messages:
            sys.stdout.write('ConfigError: %s ... ' % case)
            self.assertExceptionMessage(
                easy_menu.ConfigError, expected_messages[case][1],
                lambda: easy_menu.EasyMenu(
                    SCRIPT_DIR + '/config_error/' + expected_messages[case][0]
                )
            )
            print('OK')


class TestMainFunction(unittest.TestCase):
    """Test main function."""
    HELP_MESSAGE = """Usage: easy_menu.py [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -c CONFIG_PATH, --config=CONFIG_PATH
                        set configuration file path to CONFIG_PATH
  -l LOG_PATH, --log=LOG_PATH
                        set log file path to LOG_PATH
  -e ENCODING, --encode=ENCODING
                        set output encoding to ENCODING
"""
    OPTION_ERROR_MESSAGE = """Usage: easy_menu.py [options]

easy_menu.py: error: no such option: -x
"""

    def test_command_line_options(self):
        self.assertFalse(os.path.exists('INVALID_FILE_NAME'))

        expected = {
            ('--version',): ('Easy Menu %s\n' % PROGRAM_VERSION, 0),
            ('-h',): (self.HELP_MESSAGE, 0),
            ('--help',): (self.HELP_MESSAGE, 0),
            ('-x',): (self.OPTION_ERROR_MESSAGE, 2),
            ('-c', 'INVALID_FILE_NAME'): (
                'Failed to open file: INVALID_FILE_NAME\n', 3)
        }

        orig_exit = sys.exit
        sys.exit = customized_exit
        for case in expected:
            sys.stdout.write(
                'CommandLineOption: %s ... ' % list(case))

            out = Output()
            sys.stdout = out
            sys.stderr = out
            sys.argv = ['easy_menu.py'] + list(case)

            ret = 0
            try:
                ret = easy_menu.main()
            except ExitException, e:
                ret = e.code

            self.assertEqual(expected[case][1], ret)

            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            self.assertEqual(
                expected[case][0], out.read(), 'Unexpected output message.')
            print('OK')
        sys.exit = orig_exit


if __name__ == "__main__":
    unittest.main()
