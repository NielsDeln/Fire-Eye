import unittest
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import prop_downwash_NEW as pdn

class TestPropDownwash(unittest.TestCase):

    def test_V_max_profile(self):
        D_0 = 2 * pdn.R_0
        x0 = pdn.x_0
        vals = [
            (x0, pdn.V_0 * (1.24 - 0.0765 * 0)),
            (x0 + 1.7 * D_0, pdn.V_0 * (1.37 - 0.1529 * 1.7)),
            (x0 + 4.25 * D_0, pdn.V_0 * (0.89 - 0.04 * 4.25))
        ]
        for x, expected in vals:
            self.assertAlmostEqual(pdn.V_max(x), expected, places=4)

    def test_R_max_profile(self):
        D_0 = 2 * pdn.R_0
        x0 = pdn.x_0
        vals = [
            (x0, pdn.R_max_0 * (1 - 0.1294 * 0)),
            (x0 + 1.7 * D_0, pdn.R_max_0 * (1.3 - 0.3059 * 1.7)),
            (x0 + 4.25 * D_0 + 0.1, 0)
        ]
        for x, expected in vals:
            self.assertAlmostEqual(pdn.R_max(x), expected, places=4)

    def test_v_i_shape_and_peak(self):
        x = pdn.x_0 + 0.5
        r_peak = pdn.R_max(x)
        vi_center = pdn.v_i(x, r_peak)
        vi_offset = pdn.v_i(x, r_peak + 0.1 * pdn.R_max_0)
        self.assertGreater(vi_center, vi_offset)

    def test_v_i_falloff(self):
        x = pdn.x_0 + 3 * pdn.D_0
        r_far = 3 * pdn.D_p
        vi_val = pdn.v_i(x, r_far)
        self.assertLess(vi_val, 0.5)

    def test_plot_functions(self):
        try:
            pdn.plot_downwash(orientation='horizontal')
            pdn.plot_downwash(orientation='vertical')
            pdn.plot_ground_velocity()
        except Exception as e:
            self.fail(f"Plotting functions raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()
