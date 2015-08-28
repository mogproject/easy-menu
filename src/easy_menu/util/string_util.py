from unicodedata import east_asian_width

__unicode_width_mapping = {'F': 2, 'H': 1, 'W': 2, 'Na': 1, 'A': 2, 'N': 1}


def unicode_width(s):
    if not isinstance(s, unicode):
        return len(s)
    return sum(__unicode_width_mapping[east_asian_width(c)] for c in s)


def edge_just(left, right, width, fillchar=' '):
    padding = fillchar * max(1, width - unicode_width(left + right))
    return left + padding + right
