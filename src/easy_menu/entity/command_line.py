from __future__ import division, print_function, absolute_import, unicode_literals

import six
from mog_commons.case_class import CaseClass
from mog_commons.collection import get_single_item
from mog_commons.string import to_unicode, is_unicode, is_strlike
from easy_menu.entity import Meta


class CommandLine(CaseClass):
    def __init__(self, cmd, meta):
        """
        :param cmd:
        :param meta:
        :return:
        """
        assert is_unicode(cmd)
        assert isinstance(meta, Meta)

        CaseClass.__init__(self, ('cmd', cmd), ('meta', meta))

    @staticmethod
    def parse(data, meta, encoding='utf-8'):
        """
        Parse one command line.
        :param data: string or dict:
        :param meta: Meta: meta configuration inherited from the parent menu
        :param encoding: string:
        :return: CommandLine:
        """
        assert isinstance(meta, Meta)

        def f(s):
            return to_unicode(s, encoding)

        if is_strlike(data):
            return CommandLine(f(data), meta)
        elif isinstance(data, dict):
            cmd, params = get_single_item(data)
            assert is_strlike(cmd), 'cmd must be string, not %s.' % type(cmd).__name__
            new_meta = meta.updated(params, encoding)
            return CommandLine(to_unicode(cmd, encoding), new_meta)
        else:
            raise ValueError('CommandLine must be string or dict, not %s.' % type(data).__name__)
