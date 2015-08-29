import sys

from easy_menu.util import string_util, term_util
from easy_menu.exceptions import InterruptError, EncodeError
from i18n import *


class Terminal(object):
    def __init__(self, root_menu, host, user, executor, width=80, page_size=9, _input=sys.stdin, _output=sys.stdout,
                 encoding=None):
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
        :return:
        """
        assert 0 < width, 'width must be positive'
        assert 0 < page_size <= 9, 'page_size must be positive and one digit'

        # fields
        self.root_menu = root_menu
        self.host = host
        self.user = user
        self.executor = executor
        self.width = width
        self.page_size = page_size
        self._input = _input
        self._output = _output
        self.encoding = self._find_encoding(encoding, _output)

    @staticmethod
    def _find_encoding(encoding, output):
        if not encoding:
            if hasattr(output, 'encoding'):
                encoding = output.encoding
        if not encoding:
            encoding = locale.getpreferredencoding()
        return encoding

    def _num_pages(self, num_items):
        return max(1, (num_items + self.page_size - 1) // self.page_size)

    #
    # Design parts
    #
    def thin_line(self):
        return u'-' * self.width

    def thick_line(self):
        return u'=' * self.width

    def header_line(self):
        return string_util.edge_just(MSG_HOST % self.host, MSG_USER % self.user, self.width)

    @staticmethod
    def title_line(title):
        return u' ' * 2 + title

    def menu_line(self):
        return u'+'.rjust(7, '-').ljust(self.width, '-')

    def pager_line(self, offset, num_pages):
        left = u'<= [P]' if 0 < offset else '      '
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

    @staticmethod
    def _get_description(item):
        d, c = item.items()[0]
        return MSG_SUB_MENU % d if isinstance(c, list) else d

    def get_page(self, title, page_items, parent_title, offset, num_pages):
        """Make menu page string."""

        pager_lines = [] if num_pages <= 1 else [
            self.pager_line(offset, num_pages),
            self.thin_line(),
        ]

        item_lines = [MSG_ITEM % (i + 1, self._get_description(item)) for i, item in enumerate(page_items)]

        quit_lines = [
            self.menu_line(),
            MSG_ITEM % (0, MSG_QUIT if parent_title is None else MSG_RETURN % parent_title),
        ]

        message = MSG_INPUT_NUM % (0, len(page_items))
        return u'\n'.join(self._get_header(title) + pager_lines + item_lines + quit_lines + self._get_footer(message))

    def get_confirm(self, description):
        """
        Make confirmation page string

        :param description: description for the command to execute
        :return: string
        """

        item_lines = [
            MSG_CONFIRM % description
        ]
        return u'\n'.join(self._get_header(MSG_CONFIRM_TITLE) + item_lines + self._get_footer(MSG_CONFIRM_QUESTION))

    def get_before_execute(self, description):
        return u'\n'.join(self._get_header(MSG_RUN_TITLE % description) + [''])

    def get_after_execute(self, return_code):
        result_lines = [
            self.thin_line(),
            'Return code: %d' % return_code,
        ]
        return '\n'.join(result_lines + self._get_footer(MSG_INPUT_ANY))

    #
    # Wait for input
    #
    def wait_input_char(self):
        ch = term_util.getch(self._input)
        if ch in ['\x03', '\x04']:
            # pressed C-c or C-d
            raise InterruptError()
        return ch

    #
    # Output
    #
    def _print(self, unicode_text):
        try:
            self._output.write(unicode_text.encode(self.encoding))
        except LookupError, e:
            raise EncodeError(e)

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
                    description, command = d.items()[0]

                    # check if it is a sub menu
                    if isinstance(command, list):
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
        :param command: command line string
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
        return_code = self.executor.execute(
            command.encode(self.encoding), stdin=self._input, stdout=self._output, stderr=self._output)

        if return_code == 130:
            # maybe interrupted
            self._print(u'\n')

        self._print(self.get_after_execute(return_code))
        self.wait_input_char()  # wait for any input

    def loop(self):
        stack = [self.root_menu]
        offset = 0  # current page index

        while stack:
            title, items = stack[-1].items()[0]
            num_pages = self._num_pages(len(items))
            parent_title = None if len(stack) == 1 else stack[-2].keys()[0]

            # apply offset
            page_items = items[self.page_size * offset:self.page_size * (offset + 1)]

            self._draw(self.get_page(title, page_items, parent_title, offset, num_pages))

            f = self.wait_input_menu(stack[-1].values()[0], offset, num_pages)
            stack, offset = f(stack, offset)

        term_util.clear_screen(self._input, self._output)
