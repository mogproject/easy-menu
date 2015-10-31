from __future__ import division, print_function, absolute_import, unicode_literals

import six
from mog_commons.case_class import CaseClass
from mog_commons.string import to_unicode, is_unicode
from mog_commons.collection import get_single_item
from easy_menu.entity.command_line import CommandLine


class Command(CaseClass):
    def __init__(self, title, command_lines):
        """
        :param title:
        :param command_lines:
        :return:
        """
        assert is_unicode(title)
        assert isinstance(command_lines, list) and all(isinstance(x, CommandLine) for x in command_lines)

        CaseClass.__init__(self, ('title', title), ('command_lines', command_lines))

    @staticmethod
    def parse(data, meta, encoding='utf-8'):
        """
        Parse one command operation.
        :param data: dict:
        :param meta: Meta: meta configuration inherited from the parent menu
        :param encoding: string:
        :return: Command:
        """
        from easy_menu.entity import Meta

        assert isinstance(data, dict), 'Command must be dict, not %s.' % type(data).__name__
        assert isinstance(meta, Meta)

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
