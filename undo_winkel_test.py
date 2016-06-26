import unittest

import undo_winkel
import winkel

class WinkelTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def assertTuplesWithin(self, t1, t2, delta=0.0):
        self.assertAlmostEqual(t1[0], t2[0], delta=delta)
        self.assertAlmostEqual(t1[1], t2[1], delta=delta)

    def test_parse_draw_string(self):
        self.assertEquals([('M', [100, 100]), ('L', [200, 200])],
                undo_winkel.parse_draw_string('M 100 100 L 200 200'))
        self.assertEquals([('M', [10, 20]), ('l', [30, 40]), ('L', [40, 50]), ('z', [])],
                undo_winkel.parse_draw_string('M 10 20 l 30 40 L 40 50 z'))
        self.assertEquals([('M', [10, 20]), ('L', [30, 40]), ('L', [40, 50]), ('z', [])],
                undo_winkel.parse_draw_string('M 10 20 L 30 40 L 40 50 z'))
        self.assertEquals([('M', [10, 20]), ('S', [30, 40, 50, 60]), ('S', [40, 50, 60, 70]), ('z', [])],
                undo_winkel.parse_draw_string((' M 10 20 S 30 40 50 60 40 50 60 70 z')))

    def test_serialize_draw_string(self):
        def testBackAndForth(path):
            self.assertEqual(path, undo_winkel.serialize_path(undo_winkel.parse_draw_string(path)))

        testBackAndForth('M 100 100 L 200 200')
        testBackAndForth('M 10 20 l 30 40 L 40 50 z')
        testBackAndForth('M 10 20 L 30 40 L 40 50 z')
        testBackAndForth('M 10 20 S 30 40 50 60 S 40 50 60 70 z')
        testBackAndForth('M 0 0 S 200 100 100 200 S 200 300 300 300 z')

    def test_absolutize_path(self):
        self.assertEqual([
            ('M', [20, 10]),
            ('L', [30, 20]),
            ('L', [10, 30]),
            ('z', [])
        ], undo_winkel.absolutize_path([
            ('M', [20, 10]),
            ('l', [10, 10]),
            ('l', [-20, 10]),
            ('z', [])
        ]))

    def test_interpolate_curves(self):
        path = undo_winkel.parse_draw_string('M 0 0 S 200 100 100 200 200 300 300 300 z')
        print undo_winkel.serialize_path(undo_winkel.interpolate_curves(path))
        self.assertEqual([],
            undo_winkel.interpolate_curves(path))

    def test_path_to_coords(self):
        path = undo_winkel.parse_draw_string('M 10 20 L 30 40 L 40 50 z')
        self.assertEqual([[
            [10, 20],
            [30, 40],
            [40, 50],
            [10, 20]
        ]], undo_winkel.path_to_coords(path))

        path = undo_winkel.parse_draw_string('M 10 20 L 30 40 z M 30 30 L 40 50 z')
        self.assertEqual([[
            [10, 20],
            [30, 40],
            [10, 20],
        ], [
            [30, 30],
            [40, 50],
            [30, 30],
        ]], undo_winkel.path_to_coords(path))

    def test_extremes_from_path(self):
        self.assertEquals(((100, 100), (200, 200)),
                undo_winkel.extremes_from_path([('M', [100, 100]), ('L', [200, 200])]))
        self.assertEquals(((10, 20), (40, 50)),
                undo_winkel.extremes_from_path([('M', [10, 20]), ('L', [40, 50])]))

    def test_scaled_winkel(self):
        sw = winkel.ScaledWinkel(25201, 15120, 0)
        self.assertTuplesWithin((180.0, 0.0),  sw.invert(25201, 15120/2), delta=0.02)
        self.assertTuplesWithin((-180.0, 0.0), sw.invert(0, 15120/2), delta=0.02)
        self.assertTuplesWithin((0, 90.0),     sw.invert(12600, 0), delta=0.02)
        self.assertTuplesWithin((0, -90.0),    sw.invert(12600, 15120), delta=0.02)
        self.assertTuplesWithin((0, 0),        sw.invert(12600, 15120/2), delta=0.02)


if __name__ == '__main__':
    unittest.main()
