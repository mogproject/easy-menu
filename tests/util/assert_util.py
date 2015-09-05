import tempfile
from contextlib import contextmanager
from jinja2 import Template


@contextmanager
def assert_output(test_case_instance, expect_file, variables=None, encoding='utf-8'):
    with tempfile.TemporaryFile() as out:
        yield out

        with open(expect_file) as f:
            data = f.read()
            if variables:
                data = Template(data).render(**variables)
            expect = data.splitlines()

        out.seek(0)
        actual = out.read().splitlines(0)

        test_case_instance.assertEqual(len(actual), len(expect), 'actual=%s, expect=%s' % (actual, expect))
        for i in range(len(expect)):
            test_case_instance.assertEqual(
                actual[i].decode(encoding),
                expect[i],
                'lineno=%d, actual=%r, expect=%r' % (i, actual[i], expect[i])
            )
