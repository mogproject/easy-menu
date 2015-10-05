from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import six

from easy_menu.util import string_util, term_util
from easy_menu.util.collection_util import get_single_item, get_single_key, get_single_value
from easy_menu.exceptions import EncodingError, SettingError
from easy_menu.view import i18n

DEFAULT_WINDOW_WIDTH = 78
DEFAULT_PAGE_SIZE = 9


class Terminal(object):
    def __init__(self, root_menu, host, user, executor, width=None, page_size=None, _input=sys.stdin,
                 _output=sys.stdout, encoding=None, lang=None):
        """
        :param root_menu: dict of root menu
        :param host: host name string
        :param user: user name string
        :param executor: Executor instance
        :param width:
        :param page_size:
        :param _input:
        :param _output:
        :param encoding:
        :param lang: language setting
        :return:
        """
        # fields
        self.root_menu = root_menu
        self.host = host
        self.user = user
        self.executor = executor
        self.width = DEFAULT_WINDOW_WIDTH if width is None else width
        self.page_size = DEFAULT_PAGE_SIZE if page_size is None else page_size
        self._input = _input
        self._output = _output
        self.encoding = encoding
        self.lang = lang
        self.i18n = self._find_i18n(lang)

        if self.width < 40:
            raise SettingError('width must be equal or greater than 40: width=%s' % self.width)
        if not 0 < self.page_size <= 9:
            raise SettingError('page_size must be positive and one digit: page_size=%s' % self.page_size)

    @staticmethod
    def _find_i18n(lang):
        if not lang:
            return i18n.messages_en
        elif lang.lower().startswith('ja'):
            return i18n.messages_ja
        else:
            return i18n.messages_en

    def _num_pages(self, num_items):
        return max(1, (num_items + self.page_size - 1) // self.page_size)

    #
    # Design parts
    #
    def thin_line(self):
        return '-' * self.width

    def thick_line(self):
        return '=' * self.width

    def header_line(self):
        return string_util.edge_just(self.i18n.MSG_HOST % self.host, self.i18n.MSG_USER % self.user, self.width)

    @staticmethod
    def title_line(title):
        return ' ' * 2 + title

    def menu_line(self):
        return '+'.rjust(7, '-').ljust(self.width, '-')

    def pager_line(self, offset, num_pages):
        left = '<= [P]' if 0 < offset else '      '
        right = '[N] =>' if offset + 1 < num_pages else '      '
        middle = ('Page %d / %d' % (offset + 1, num_pages)).center(self.width - len(left) - len(right))
        return left + middle + right

    #
    # Building output string
    #
    def _get_header(self, title):
        return [
            self.header_line(),
            self.thick_line(),
            self.title_line(title),
            self.thin_line(),
        ]

    def _get_footer(self, message):
        return [
            self.thick_line(),
            message,
        ]

    def _get_description(self, item):
        d, c = get_single_item(item)
        return self.i18n.MSG_SUB_MENU % d if isinstance(c, list) else d

    def get_page(self, titles, page_items, offset, num_pages):
        """Make menu page string."""

        assert len(page_items) <= self.page_size, 'Number of page items must less or equal than page size.'

        title = string_util.unicode_right(' > '.join(titles), self.width - 4)

        pager_lines = [] if num_pages <= 1 else [
            self.pager_line(offset, num_pages),
            self.thin_line(),
        ]

        item_lines = [self.i18n.MSG_ITEM % (i + 1, self._get_description(item)) for i, item in enumerate(page_items)]

        quit_lines = [
            self.menu_line(),
            self.i18n.MSG_ITEM % (
                0, self.i18n.MSG_QUIT if len(titles) == 1 else self.i18n.MSG_RETURN % titles[-2]),
        ]

        message = self.i18n.MSG_INPUT_NUM % (0, len(page_items))
        return '\n'.join(self._get_header(title) + pager_lines + item_lines + quit_lines + self._get_footer(message))

    def get_confirm(self, description):
        """
        Make confirmation page string

        :param description: description for the command to execute
        :return: string
        """

        item_lines = [
            self.i18n.MSG_CONFIRM % description
        ]
        return '\n'.join(
            self._get_header(self.i18n.MSG_CONFIRM_TITLE) + item_lines +
            self._get_footer(self.i18n.MSG_CONFIRM_QUESTION))

    def get_before_execute(self, description):
        return '\n'.join(self._get_header(self.i18n.MSG_RUN_TITLE % description) + [''])

    def get_after_execute(self, return_code):
        result_lines = [
            self.thin_line(),
            'Return code: %d' % return_code,
        ]
        return '\n'.join(result_lines + self._get_footer(self.i18n.MSG_INPUT_ANY))

    #
    # Wait for input
    #
    def wait_input_char(self):
        ch = term_util.getch(self._input)
        if ch in ['\x03', '\x04']:
            # pressed C-c or C-d
            raise KeyboardInterrupt
        return ch

    #
    # Output
    #
    def _print(self, unicode_text):
        assert string_util.is_unicode(unicode_text), 'Text must be unicode: %s' % unicode_text

        try:
            term_util.universal_print(self._output, unicode_text, self.encoding)
        except (LookupError, UnicodeError):
            raise EncodingError('Failed to print menu: lang=%s, encoding=%s' % (self.lang, self.encoding))

    def _draw(self, unicode_text):
        term_util.clear_screen(self._input, self._output)
        self._print(unicode_text)

    #
    # Main loop
    #
    def wait_input_menu(self, menu_items, offset, num_pages):
        """
        :param menu_items: list of items
        :param offset: page offset
        :return: function(stack, offset => stack, offset)
        """
        num_items = len(menu_items)

        while True:
            ch = self.wait_input_char().lower()
            if ch == '0':
                return lambda s, o: (s[:-1], 0)
            elif ch.isdigit():
                index = offset * self.page_size + int(ch) - 1
                if index < num_items:
                    d = menu_items[index]
                    description, command = get_single_item(d)

                    # check if it is a sub menu
                    if isinstance(command, list):
                        # check if it is a command list
                        if not all(isinstance(child, six.string_types) for child in command):
                            return lambda s, o: (s + [d], 0)

                    def f(s, o):  # side effect only
                        self.execute_command(description, command)
                        return s, o

                    return f
            elif ch == 'n' and offset + 1 < num_pages:
                return lambda s, o: (s, o + 1)
            elif ch == 'p' and 0 < offset:
                return lambda s, o: (s, o - 1)

    def execute_command(self, description, command):
        """
        Confirm with prompt before executing command.

        :param description: description string
        :param command: command line string or list of command line string
        :return: None
        """

        # confirmation
        self._draw(self.get_confirm(description))

        while True:
            ch = self.wait_input_char().lower()
            if ch == 'y':
                break
            if ch == 'n' or ch == '\r':
                return

        # run command
        self._draw(self.get_before_execute(description))

        # if command is string, convert to a list
        if isinstance(command, six.string_types):
            command = [command]

        return_code = 0
        for cmd in command:
            return_code = self.executor.execute(
                cmd, stdin=self._input, stdout=self._output, stderr=self._output, encoding=self.encoding)

            if return_code == 130:
                # maybe interrupted
                self._print('\n')
            # if a command fails, the successors will not run
            if return_code != 0:
                break

        self._print(self.get_after_execute(return_code))
        self.wait_input_char()  # wait for any input

    def loop(self):
        stack = [self.root_menu]
        offset = 0  # current page index

        while stack:
            titles = [get_single_key(d) for d in stack]
            items = get_single_value(stack[-1])
            num_pages = self._num_pages(len(items))

            # apply offset
            page_items = items[self.page_size * offset:self.page_size * (offset + 1)]

            self._draw(self.get_page(titles, page_items, offset, num_pages))

            f = self.wait_input_menu(get_single_value(stack[-1]), offset, num_pages)
            stack, offset = f(stack, offset)

        term_util.clear_screen(self._input, self._output)
