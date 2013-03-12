#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Easy Menu Tests."""

import sys
import os
import unittest
import re

sys.path[0:0] = [os.path.join(os.path.dirname(__file__), '..'), ]
import easy_menu

# Path settings.
SCRIPT_DIR = os.path.dirname(__file__)


# Functions.
def remove_file(path):
    if os.path.exists(path):
        try:
            os.remove(path)
            print('Removed: %s' % path)
        except OSError:
            print('Cannot remove: %s' % path)


def read_file(path):
    file_object = open(path)
    try:
        data = file_object.read()
    finally:
        file_object.close()
    return data


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


class Output(object):
    """Emulate file output"""
    def __init__(self):
        self._buf = []

    def fileno(self):
        return 0

    def write(self, text):
        self._buf.append(text)

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
    def _check_log(self, description, log_path, expected):
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
        print('%s: Log ... OK' % description)

        # Remove log.
        remove_file(log_path)

    def test_encode_error(self):
        log_path = SCRIPT_DIR + '/encode_error/encode_error.log'

        # Clear log.
        remove_file(log_path)

        self.assertExceptionMessage(
            easy_menu.EncodeError, 'Encode error: unknown encoding: UNKNOWN',
            lambda: easy_menu.EasyMenu(
                log_path=log_path,
                encoding='UNKNOWN'
            ).start()
        )
        print('EncodeError: Unknown encoding ... OK')

        # Check log.
        self._check_log('EncodeError', log_path, [
            'INFO Script started\.',
            'WARNING Script ended with error: ' +
            'Encode error: unknown encoding: UNKNOWN'
        ])

    def test_logger_error(self):
        log_path = SCRIPT_DIR + '/i/n/v/a/l/i/d/'
        self.assertFalse(os.path.exists(log_path))
        self.assertExceptionMessage(
            IOError, 2,
            lambda: easy_menu.EasyMenu(log_path=log_path).start()
        )
        print('Logger: Invalid file path ... OK')

    def test_interrupt_error(self):
        base_dir = SCRIPT_DIR + '/interrupt_error'
        config_path = base_dir + '/config.json'
        input_path = base_dir + '/input.txt'
        log_path = base_dir + '/interrupt.log'

        # Clear log.
        remove_file(log_path)

        # Start menu.
        in_file = open(input_path)
        out = Output()
        em = easy_menu.EasyMenu(config_path, log_path, 'utf-8', in_file, out)
        em.start()
        in_file.close()

        # Check log.
        self._check_log('Interrupt', log_path, [
            'INFO Script started\.',
            'WARNING Script was interrupted\.'
        ])

    def test_skelton(self):
        base_dir = SCRIPT_DIR + '/skeleton'
        config_path = base_dir + '/config.json'
        input_path = base_dir + '/input.txt'
        log_path = base_dir + '/skeleton.log'

        # Clear log.
        remove_file(log_path)

        # Start menu.
        in_file = open(input_path)
        out = Output()
        em = easy_menu.EasyMenu(config_path, log_path, 'utf-8', in_file, out)
        em.start()
        in_file.close()

        # Check log.
        self._check_log('Skeleton', log_path, [
            'INFO Script started\.'
        ] + [
            'INFO Command started: ',
            'INFO Command ended with return code: 0',
        ] * 6 + [
            'INFO Script ended normally.'
        ])

        # Check output.
        prompt = easy_menu.Prompt()
        menu = prompt.make_menu([{'name': '', 'item': ['', '']}])
        confirm = prompt.make_confirm('')
        command = prompt.make_command_start('') + prompt.make_command_end(0)
        expected = (
            menu * 10 + (confirm + menu) * 8 + (confirm + command + menu) * 6
        )
        self.assertEqual(expected.encode('utf-8'), out.read())
        print('Skeleton: Output ... OK')

    def test_command_output(self):
        base_dir = SCRIPT_DIR + '/command_output'
        config_path = base_dir + '/config.json'
        input_path = base_dir + '/input.txt'
        log_path = base_dir + '/command_output.log'

        # Clear log.
        remove_file(log_path)

        # Start menu.
        in_file = open(input_path)
        out = Output()
        em = easy_menu.EasyMenu(config_path, log_path, 'utf-8', in_file, out)
        em.start()
        in_file.close()

        # Check log.
        self._check_log('CommandOutput', log_path, [
            'INFO Script started\.',
            'INFO Command started: echo x',
            'INFO Command ended with return code: 0',
            'INFO Command started: exit 2',
            'INFO Command ended with return code: 2',
            'INFO Script ended normally.'
        ])

        # Check output.
        prompt = easy_menu.Prompt()
        menu = prompt.make_menu([
            {"name": "NAME", "item": ["a", "echo x", "b", "exit 2"]}
        ])
        expected = u''.join([
            menu,
            prompt.make_confirm('a'),
            prompt.make_command_start('a'),
            prompt.make_command_end(0),
            menu,
            prompt.make_confirm('b'),
            prompt.make_command_start('b'),
            prompt.make_command_end(2),
            menu
        ])
        self.assertEqual(expected.encode('utf-8'), out.read())
        print('CommandOutput: Output ... OK')

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


if __name__ == "__main__":
    unittest.main()
