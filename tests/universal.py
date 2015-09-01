import sys
import six

# unittest
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)
        if six.PY3:
            self.assertRaisesRegexp = self.assertRaisesRegex
