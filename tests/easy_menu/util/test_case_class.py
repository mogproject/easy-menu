from __future__ import division, print_function, absolute_import, unicode_literals

import six

from easy_menu.util.case_class import CaseClass
from tests.universal import TestCase


class Coord(CaseClass):
    def __init__(self, x, y):
        super(Coord, self).__init__(('x', x), ('y', y))


class TestCaseClass(TestCase):
    def test_init(self):
        a = Coord(123, 45)
        self.assertEqual(a.x, 123)
        self.assertEqual(a.y, 45)

    def test_init_error(self):
        class CoordX(CaseClass):
            def __init__(self, x, y):
                super(CoordX, self).__init__(('x', x), ('x', y))

        self.assertRaises(ValueError, lambda: CoordX(123, 45))

    def test_cmp(self):
        a = Coord(123, 45)
        b = Coord(123, 45)
        c = Coord(123, 46)
        d = Coord(124, 45)
        e = Coord(122, 46)

        combi = [(i, j) for i in [a, b, c, d, e] for j in [a, b, c, d, e]]

        self.assertEqual([x == y for x, y in combi], [
            True, True, False, False, False,
            True, True, False, False, False,
            False, False, True, False, False,
            False, False, False, True, False,
            False, False, False, False, True,
        ])

        self.assertEqual([x < y for x, y in combi], [
            False, False, True, True, False,
            False, False, True, True, False,
            False, False, False, True, False,
            False, False, False, False, False,
            True, True, True, True, False,
        ])

    def test_different_types(self):
        class AAA:
            pass

        self.assertEqual(Coord(123, 45) == 10, False)
        self.assertEqual(Coord(123, 45) == 'x', False)
        self.assertEqual(Coord(123, 45) == AAA(), False)

        self.assertRaisesRegexp(TypeError, '^unorderable types: Coord\(\) < int\(\)$', lambda: Coord(123, 45) < 10)
        self.assertRaisesRegexp(TypeError, '^unorderable types: Coord\(\) < ', lambda: Coord(123, 45) < 'x')
        self.assertRaisesRegexp(TypeError, '^unorderable types: Coord\(\) < AAA\(\)$', lambda: Coord(123, 45) < AAA())

    def test_repr(self):
        self.assertEqual(repr(Coord(123, 45)), 'Coord(x=123, y=45)')
