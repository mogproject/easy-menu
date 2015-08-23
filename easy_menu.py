#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Yosuke Mizutani
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Easy Menu - The Simplest Terminal User Interface

Make the text based menu from your JSON formatted configuration file.
"""

from optparse import OptionParser
import sys
import os
import locale
import getpass
import re
import subprocess
try:
    import json
except ImportError:
    print('You need python 2.6 or later to run this script.')
    sys.exit(1)

# Version settings.
PROGRAM_NAME = 'Easy Menu'
PROGRAM_VERSION = '0.0.3'

# Path settings.
SCRIPT_DIR = os.path.dirname(__file__)
SCRIPT_BASE_NAME = os.path.basename(__file__)
DEFAULT_CONFIG_FILE = SCRIPT_DIR + '/config.json'
DEFAULT_LOG_FILE = '%s/%s.log' % (
    SCRIPT_DIR, os.path.splitext(SCRIPT_BASE_NAME)[0]
)

# Log settings.
LOG_BACKUP_COUNT = 1
LOG_MAX_BYTES = 1 * (1024 ** 2)
LOG_FORMAT = '[%(asctime)s] %(levelname)s %(message)s'

# JSON format settings.
KEY_NAME, KEY_ITEM = 'name', 'item'


class Error(Exception):
    """Basic error class of this script."""
    pass


class ConfigError(Error):
    """Configuration file error."""
    pass


class InterruptError(Error):
    """Interruption error."""
    pass


class EncodeError(Error):
    """Encode error."""
    pass


class Prompt(object):
    """Manages output string."""
    MAX_WIDTH = 80
    LINE_THICK = '=' * MAX_WIDTH
    LINE_THIN = '-' * MAX_WIDTH
    LINE_MENU = '%s+%s' % ('-' * 4, '-' * (MAX_WIDTH - 5))
    MSG_HOST = u'ホスト名: %s'
    MSG_USER = u'実行ユーザ: %s'
    MSG_ITEM = '%3d | %s'
    MSG_QUIT = u'終了'
    MSG_RETURN = u'%s に戻る'
    MSG_INPUT_NUM = u'番号を入力してください (%d-%d): '
    MSG_INPUT_ANY = u'Enterキーを入力するとメニューに戻ります...'
    MSG_CONFIRM_TITLE = u'実行確認'
    MSG_CONFIRM = u'  %s を行います。'
    MSG_CONFIRM_QUESTION = u'よろしいですか? (y/n) [n]: '
    MSG_RUN_TITLE = u'実行: %s'
    CONFIRM_YES = re.compile(r'^\s*(y|yes)\s*$', re.IGNORECASE)

    def __init__(self):
        import socket

        # Prepare page header and footer.
        host = self.MSG_HOST % socket.gethostname()
        user = self.MSG_USER % getpass.getuser()
        padding = max(1, self.MAX_WIDTH - self._unicode_width(host + user))

        buf = []
        buf.append(host + ' ' * padding + user)
        buf.append(self.LINE_THICK)
        buf.append('  %s')
        buf.append(self.LINE_THIN)

        self._head = '\n'.join(buf)
        self._foot = self.LINE_THICK + '\n%s'

    def make_menu(self, menu_stack):
        """Make menu page string."""
        buf = []
        descriptions = menu_stack[-1][KEY_ITEM][::2]

        buf.append(self._head % menu_stack[-1][KEY_NAME])
        for index, description in enumerate(descriptions):
            buf.append(self.MSG_ITEM % (index + 1, description))
        buf.append(self.LINE_MENU)

        if len(menu_stack) == 1:
            return_msg = self.MSG_QUIT
        else:
            return_msg = self.MSG_RETURN % menu_stack[-2][KEY_NAME]
        buf.append(self.MSG_ITEM % (0, return_msg))
        buf.append(self._foot % self.MSG_INPUT_NUM % (0, len(descriptions)))
        return '\n'.join(buf)

    def make_confirm(self, description):
        """Make confirmation page string"""
        buf = []
        buf.append(self._head % self.MSG_CONFIRM_TITLE)
        buf.append(self.MSG_CONFIRM % description)
        buf.append(self._foot % self.MSG_CONFIRM_QUESTION)
        return '\n'.join(buf)

    def make_command_start(self, command):
        """Make string before running command."""
        return self._head % self.MSG_RUN_TITLE % command + '\n'

    def make_command_end(self, return_code):
        """Make string after running command."""
        buf = []
        buf.append(self.LINE_THIN)
        buf.append('Return code: %d' % return_code)
        buf.append(self._foot % self.MSG_INPUT_ANY)
        return '\n'.join(buf)

    def _unicode_width(self, s):
        from unicodedata import east_asian_width
        width = {'F': 2, 'H': 1, 'W': 2, 'Na': 1, 'A': 2, 'N': 1}
        return sum(width[east_asian_width(c)] for c in s)


class EasyMenu(object):
    """Manages configuration, input and output."""

    MAX_ITEM_LENGTH = 16

    def __init__(
        self, config_path=None, log_path=None, encoding=None,
        in_stream=sys.stdin, out_stream=sys.stdout
    ):
        self._input = in_stream
        self._output = out_stream
        if not encoding:
            if hasattr(self._output, 'encoding'):
                encoding = self._output.encoding
        if not encoding:
            encoding = locale.getpreferredencoding()
        self._encoding = encoding
        self._prompt = Prompt()
        self._config = self._load_config(config_path or DEFAULT_CONFIG_FILE)
        self._logger = self._get_logger(log_path or DEFAULT_LOG_FILE)

    def start(self):
        """Start main process."""
        self._logger.info('Script started.')

        try:
            self._main_loop()
            self._logger.info('Script ended normally.')
        except (KeyboardInterrupt, EOFError, InterruptError):
            self._logger.warn('Script was interrupted.')
        except Error, e:
            self._logger.warn('Script ended with error: %s' % e)
            raise e
        finally:
            self._logger.handlers[0].close()

    def _clear(self):
        """Clear terminal."""
        if not self._input.isatty():
            return
        subprocess.call(
            'cls' if os.name == 'nt' else 'clear', shell=True,
            stdin=self._input, stdout=self._output, stderr=self._output
        )

    def _print(self, unicode_text):
        try:
            self._output.write(unicode_text.encode(self._encoding))
        except LookupError, e:
            raise EncodeError('Encode error: %s' % e)

    def _read_input(self):
        ret = self._input.readline()
        if ret == '':
            raise InterruptError()  # To break out of EOF loop.
        return ret

    def _load_config(self, path):
        # Load JSON data.
        try:
            file_object = open(path)
            try:
                data = file_object.read()
            finally:
                file_object.close()
            config = json.loads(data)
        except IOError:
            raise ConfigError('Failed to open file: %s' % path)
        except ValueError:
            raise ConfigError('JSON format error: %s' % path)

        # Verify menu recursively.
        def verify_menu(menu):
            for key in KEY_NAME, KEY_ITEM:
                if menu.get(key) is None:
                    raise ConfigError('Menu must have "%s" key.' % key)

            if not isinstance(menu[KEY_NAME], basestring):
                raise ConfigError('Menu name must be string.')

            if not isinstance(menu[KEY_ITEM], list):
                raise ConfigError('Menu item must be list.')

            if len(menu[KEY_ITEM]) % 2 == 1:
                raise ConfigError('Menu must have even number items.')

            if not 1 <= len(menu[KEY_ITEM]) <= self.MAX_ITEM_LENGTH * 2:
                raise ConfigError(
                    'Menu item length must be between 1 and %d.'
                    % self.MAX_ITEM_LENGTH
                )

            for index, item in enumerate(menu[KEY_ITEM]):
                if index % 2 == 0:
                    if not isinstance(item, basestring):
                        raise ConfigError(
                            'Command description must be string.'
                        )
                else:
                    if isinstance(item, dict):
                        verify_menu(item)
                    elif not isinstance(item, basestring):
                        raise ConfigError('Command must be string.')

        verify_menu(config)
        return config

    def _get_logger(self, path):
        import logging.handlers
        logger = logging.getLogger(path)
        logger.setLevel(logging.DEBUG)

        handler = logging.handlers.RotatingFileHandler(
            filename=path, maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT)

        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _main_loop(self):
        menu_stack = [self._config]
        while menu_stack:
            # Print menu.
            self._clear()
            self._print(self._prompt.make_menu(menu_stack))

            # Get items.
            item_list = menu_stack[-1][KEY_ITEM]
            items = zip(item_list[::2], item_list[1::2])

            # Wait for input of the item number.
            try:
                selected = int(self._read_input())
            except ValueError:
                continue
            if not 0 <= selected <= len(items):
                continue
            if selected == 0:  # Return or quit.
                menu_stack.pop()
                continue

            # Get selected item.
            description, command = items[selected - 1]

            # Jump to next menu if the item is menu object.
            if isinstance(command, dict):
                menu_stack.append(command)
                continue

            # Confirmation.
            self._clear()
            self._print(self._prompt.make_confirm(description))
            if not self._prompt.CONFIRM_YES.match(self._read_input()):
                continue

            # Run command.
            self._clear()
            self._print(self._prompt.make_command_start(description))
            self._logger.info('Command started: %s' % command)
            self._output.flush()
            ret_code = subprocess.call(
                command.encode(self._encoding), shell=True,
                stdin=self._input, stdout=self._output, stderr=self._output
            )
            self._logger.info('Command ended with return code: %d' % ret_code)
            self._print(self._prompt.make_command_end(ret_code))
            self._read_input()  # Wait for any input.

        # Quit menu.
        self._clear()


def main():
    # Get command line argument.
    parser = OptionParser(version='%s %s' % (PROGRAM_NAME, PROGRAM_VERSION))
    parser.add_option(
        '-c', '--config', dest='config_path',
        help='config file path (default: config.json)', metavar='PATH'
    )
    parser.add_option(
        '-l', '--log', dest='log_path',
        help='log file path (default: easy_menu.log)', metavar='PATH'
    )
    parser.add_option(
        '-e', '--encode', dest='encoding',
        help='output text encoding', metavar='ENCODING'
    )

    options = parser.parse_args()[0]

    # Set locale
    locale.setlocale(locale.LC_ALL, (''))

    # Launch Easy Menu.
    try:
        em = EasyMenu(**options.__dict__)
        em.start()
    except Error, e:
        print(e)
        return 3
    return 0

if __name__ == '__main__':
    sys.exit(main())
