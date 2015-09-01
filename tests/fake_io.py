from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import six
from contextlib import contextmanager

from easy_menu.util import string_util


class FakeInput(six.StringIO):
    def __init__(self, buff=None):
        six.StringIO.__init__(self, buff)

    def fileno(self):
        return 0


class FakeOutput(object):
    """Emulate file output"""

    def __init__(self, encoding='utf-8'):
        self.buff = []
        self.encoding = encoding

    def fileno(self):
        return 1

    def write(self, text):
        self.buff.append(text)

    def flush(self):
        """flush"""

    def read(self):
        return ''.join(string_util.to_unicode(b, self.encoding) for b in self.buff)


@contextmanager
def captured_output():
    """
    Capture and suppress stdout and stderr.
    example:
        with captured_output() as (out, err):
            (do main logic)
        (verify out.getvalue() or err.getvalue())
    :return:
    """
    new_out, new_err = six.StringIO(), six.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err
