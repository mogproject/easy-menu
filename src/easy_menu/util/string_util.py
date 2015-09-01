from __future__ import division, print_function, absolute_import, unicode_literals

from unicodedata import east_asian_width
import six

__unicode_width_mapping = {'F': 2, 'H': 1, 'W': 2, 'Na': 1, 'A': 2, 'N': 1}


def is_unicode(s):
    return (six.PY2 and isinstance(s, unicode)) or (six.PY3 and isinstance(s, str))


def is_strlike(s):
    return isinstance(s, (six.string_types, bytes))


def unicode_width(s):
    if is_unicode(s):
        return sum(__unicode_width_mapping[east_asian_width(c)] for c in s)

    assert is_strlike(s), 's must be a string, not %s.' % type(s).__name__
    return len(s)


def to_unicode(s, encoding=None, errors='strict'):
    """
    Make unicode string from any value
    :param s:
    :param encoding:
    :param errors:
    :return: unicode
    """
    encoding = encoding or 'utf-8'

    if is_unicode(s):
        return s
    elif is_strlike(s):
        return s.decode(encoding, errors)
    else:
        if six.PY2:
            return str(s).decode(encoding, errors)
        else:
            return str(s)


def edge_just(left, right, width, fillchar=' '):
    padding = fillchar * max(1, width - unicode_width(left + right))
    return left + padding + right
