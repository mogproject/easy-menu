from __future__ import division, print_function, absolute_import, unicode_literals

import six

from easy_menu.util import string_util


class FakeInput(six.StringIO):
    def __init__(self, buff=None):
        six.StringIO.__init__(self, buff)

    def fileno(self):
        return 0


class FakeOutput(object):
    """Emulate file output"""

    def __init__(self):
        self.buff = []

    def fileno(self):
        return 1

    def write(self, text):
        self.buff.append(text)

    def flush(self):
        """flush"""

    def read(self, encoding='utf-8'):
        return ''.join(string_util.to_unicode(b, encoding) for b in self.buff)
