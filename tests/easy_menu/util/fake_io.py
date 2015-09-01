from __future__ import division, print_function, absolute_import, unicode_literals

from tests.easy_menu.util.universal_import import StringIO


class FakeInput(StringIO):
    def __init__(self, buff=None):
        StringIO.__init__(self, buff)

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

    def read(self):
        return ''.join(self.buff)
