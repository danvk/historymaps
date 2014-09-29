import unittest

import undo_winkel

class WinkelTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_draw_string(self):
        self.assertEquals([('M', [100, 100]), ('L', [200, 200])],
                undo_winkel.parse_draw_string('M 100 100 L 200 200'))
        self.assertEquals([('M', [10, 20]), ('L', [40, 50])],
                undo_winkel.parse_draw_string('M 10 20 l 30 40 L 40 50 z'))


if __name__ == '__main__':
    unittest.main()
