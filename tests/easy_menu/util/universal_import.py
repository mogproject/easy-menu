# Import modules with version neutral

import sys
import six

# unittest
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

# StringIO
if six.PY2:
    from StringIO import StringIO
else:
    from io.StringIO import StringIO
