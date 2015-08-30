import sys
from easy_menu.util.case_class import CaseClass

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class Coord(CaseClass):
    def __init__(self, x, y):
        super(Coord, self).__init__(('x', x), ('y', y))


class TestCaseClass(unittest.TestCase):
    def test_case_class_init(self):
        a = Coord(123, 45)
        self.assertEqual(a.x, 123)
        self.assertEqual(a.y, 45)

    def test_case_class_init_error(self):
        class CoordX(CaseClass):
            def __init__(self, x, y):
                super(CoordX, self).__init__(('x', x), ('x', y))

        self.assertRaises(ValueError, lambda: CoordX(123, 45))

    def test_case_class_cmp(self):
        a = Coord(123, 45)
        b = Coord(123, 45)
        c = Coord(123, 46)
        d = Coord(124, 45)
        e = Coord(122, 46)

        combi = [(i, j) for i in [a, b, c, d, e] for j in [a, b, c, d, e]]

        self.assertEqual(map(lambda x: x[0] == x[1], combi), [
            True, True, False, False, False,
            True, True, False, False, False,
            False, False, True, False, False,
            False, False, False, True, False,
            False, False, False, False, True,
        ])

        self.assertEqual(map(lambda x: x[0] < x[1], combi), [
            False, False, True, True, False,
            False, False, True, True, False,
            False, False, False, True, False,
            False, False, False, False, False,
            True, True, True, True, False,
        ])

    def test_case_class_copy(self):
        a = Coord(123, 45)
        b = a.copy(y=46)
        c = b.copy(x=124)
        d = c.copy()
        e = d.copy(x=125, y=47)

        self.assertEqual(a, Coord(123, 45))
        self.assertEqual(b, Coord(123, 46))
        self.assertEqual(c, Coord(124, 46))
        self.assertEqual(d, Coord(124, 46))
        self.assertEqual(e, Coord(125, 47))

    def test_case_class_copy_error(self):
        a = Coord(123, 45)
        self.assertRaises(ValueError, lambda: a.copy(a=123))
