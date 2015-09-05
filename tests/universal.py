import sys
import six

# unittest
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

# mock
if sys.version_info < (3, 3):
    import mock
else:
    from unittest import mock

import tempfile
from contextlib import contextmanager
import jinja2
import io


class TestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)
        if six.PY3:
            self.assertRaisesRegexp = self.assertRaisesRegex

    @contextmanager
    def withAssertOutput(self, expect_stdout, expect_stderr):
        stdout = six.StringIO()
        stderr = six.StringIO()
        yield stdout, stderr
        self.assertEqual(stdout.getvalue(), expect_stdout)
        self.assertEqual(stderr.getvalue(), expect_stderr)

    @contextmanager
    def withAssertOutputFile(self, expect_file, variables=None, encoding='utf-8'):
        with tempfile.TemporaryFile() as out:
            yield out

            with io.open(expect_file, encoding=encoding) as f:
                data = f.read()
                if variables:
                    data = jinja2.Template(data).render(**variables)
                expect = data.splitlines()

            out.seek(0)
            actual = out.read().splitlines(0)

            self.assertEqual(len(actual), len(expect), 'actual=%s, expect=%s' % (actual, expect))
            for i in range(len(expect)):
                self.assertEqual(
                    actual[i].decode(encoding),
                    expect[i],
                    'lineno=%d, actual=%r, expect=%r' % (i, actual[i], expect[i])
                )

    @contextmanager
    def withAssertOutputInject(self, expect_stdout, expect_stderr):
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
            self.assertEqual(new_out.getvalue(), expect_stdout)
            self.assertEqual(new_err.getvalue(), expect_stderr)
        finally:
            sys.stdout, sys.stderr = old_out, old_err
