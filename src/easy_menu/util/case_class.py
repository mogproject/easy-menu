import copy


class CaseClass(object):
    """
    Implementation like Scala's case class

    Example:
        class Coord(CaseClass):
            def __init__(self, x, y):
                super(Coord, self).__init__(('x', x), ('y', y))

        a = Coord(123, 45)
        a.x  # 123
        a.y  # 45
        str(a)  # 'Coord(x=123, y=45)'
        b = a.copy(y=54)
        str(b)  # 'Coord(x=123, y=54)'
        a < b  # True
    """

    def __init__(self, *args):
        """
        :param args: list of tuple of field key and value
        """
        keys = []
        for k, v in args:
            if k in keys:
                raise ValueError('Found duplicate key name: %s' % k)
            keys.append(k)
            setattr(self, k, v)
        self._keys = keys

    def __cmp__(self, other):
        if not isinstance(other, self.__class__):
            # compare with class names
            return cmp(self.__class__.__name__, other.__class__.__name__)

        for k in self._keys:
            a, b = getattr(self, k), getattr(other, k)
            if a < b:
                return -1
            if a > b:
                return 1
        return 0

    def copy(self, **args):
        n = copy.deepcopy(self)
        for k in args:
            if k not in self._keys:
                raise ValueError('Invalid field name: %s' % k)
            setattr(n, k, args[k])
        return n

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join('%s=%r' % (k, getattr(self, k)) for k in self._keys))
