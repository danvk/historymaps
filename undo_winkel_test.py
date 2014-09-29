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
        self.assertEquals([('M', [10, 20]), ('L', [40, 50]), ('z', [])],
                undo_winkel.parse_draw_string('M 10 20 l 30 40 L 40 50 z'))

    def test_extremes_from_path(self):
        self.assertEquals(((100, 100), (200, 200)),
                undo_winkel.extremes_from_path([('M', [100, 100]), ('L', [200, 200])]))
        self.assertEquals(((10, 20), (40, 50)),
                undo_winkel.extremes_from_path([('M', [10, 20]), ('L', [40, 50])]))

    def test_scaled_winkel(self):
        sw = winkel.ScaledWinkel(25201, 15120)
        self.assertTuplesWithin((180.0, 0.0),  sw.invert(25201, 15120/2), delta=0.02)
        self.assertTuplesWithin((-180.0, 0.0), sw.invert(0, 15120/2), delta=0.02)
        self.assertTuplesWithin((0, 90.0),     sw.invert(12600, 0), delta=0.02)
        self.assertTuplesWithin((0, -90.0),    sw.invert(12600, 15120), delta=0.02)
        self.assertTuplesWithin((0, 0),        sw.invert(12600, 15120/2), delta=0.02)


if __name__ == '__main__':
    unittest.main()
