from __future__ import division, print_function, absolute_import, unicode_literals

import six


class FakeInput(six.StringIO):
    def __init__(self, buff=None):
        six.StringIO.__init__(self, buff)

    def fileno(self):
        return 0
