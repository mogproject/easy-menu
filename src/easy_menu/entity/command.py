from __future__ import division, print_function, absolute_import, unicode_literals

import six
from mog_commons.case_class import CaseClass
from mog_commons.string import to_unicode
from mog_commons.collection import get_single_item
from mog_commons.types import *
from easy_menu.entity import Item, Meta
from easy_menu.entity.command_line import CommandLine


class Command(Item):
    @types(title=Unicode, command_lines=ListOf(CommandLine))
    def __init__(self, title, command_lines):
        """
        :param title:
        :param command_lines:
        :return:
        """
        CaseClass.__init__(self, ('title', title), ('command_lines', command_lines))

    @staticmethod
    @types(Item, data=dict, meta=Meta)
    def parse(data, meta, loader, encoding='utf-8', depth=0):
        """
        Parse one command operation.
        :param data: dict:
        :param meta: Meta: meta configuration inherited from the parent menu
        :param loader: not used
        :param encoding: string:
        :param depth: not used
        :return: Command:
        """
        if len(data) != 1:
            raise ValueError('Command should have only one element, not %s.' % len(data))

        title, content = get_single_item(data)
        assert isinstance(title, six.string_types), 'Command title must be string, not %s' % type(title).__name__
        title = to_unicode(title, encoding)

        if isinstance(content, six.string_types):
            # single command
            return Command(title, [CommandLine.parse(content, meta, encoding)])
        elif isinstance(content, list):
            # command list
            return Command(title, [CommandLine.parse(d, meta, encoding) for d in content])
        else:
            raise ValueError('Invalid command content type: %s' % type(content).__name__)

    @types(Unicode)
    def formatted(self):
        return '\n'.join(
            ['* %s:' % self.title] + ['  %s' % line for x in self.command_lines for line in x.formatted().splitlines()])
