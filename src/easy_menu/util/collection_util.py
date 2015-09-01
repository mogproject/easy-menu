from __future__ import division, print_function, absolute_import, unicode_literals

import six


def get_single_item(d):
    """Get an item from a dict which contains just one item."""
    assert len(d) == 1, 'Single-item dict must have just one item, not %d.' % len(d)
    return list(six.iteritems(d))[0]


def get_single_key(d):
    """Get a key from a dict which contains just one item."""
    assert len(d) == 1, 'Single-item dict must have just one item, not %d.' % len(d)
    return list(six.iterkeys(d))[0]


def get_single_value(d):
    """Get a value from a dict which contains just one item."""
    assert len(d) == 1, 'Single-item dict must have just one item, not %d.' % len(d)
    return list(six.itervalues(d))[0]
