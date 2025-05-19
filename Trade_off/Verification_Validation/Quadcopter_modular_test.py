import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import numpy as np
from Trade_off.Quadcopter_modular import modular_quad

class TestModularQuad(unittest.TestCase):
    def setUp(self):
        pass

    def test_m_payload(self):
        # Test the m_payload function
        m_dmcomm = 198
        m_navig = 0
        m_mapping = 230
        m_control = 0
        m_forensics = 150
        expected_result = 198 + 0 + 230 + 0 + 150
        result = modular_quad.m_payload(m_dmcomm, m_navig, m_mapping, m_control, m_forensics)
        self.assertAlmostEqual(result, expected_result)
    
    def test_m_avionics(self):
        # Test the m_avionics function
        m0 = 1000
        expected_result = 0.12 * m0
        result = modular_quad.m_avionics(m0)
        self.assertAlmostEqual(result, expected_result)
    
    def test_m_motor(self):
        # Test the m_motor function
        T_motor = 1000
        expected_result = 1e-07 * T_motor**3 - 0.0003 * T_motor**2 + 0.2783 * T_motor - 56.133
        result = modular_quad.m_motor(T_motor)
        self.assertAlmostEqual(result, expected_result)
    
    def test_m_ESC(self):
        # Test the m_ESC function
        I_max = 30
        expected_result = 0.9546 * I_max - 2.592
        result = modular_quad.m_ESC(I_max)
        self.assertAlmostEqual(result, expected_result)
    
    def test_m_battery(self):
        # Test the m_battery function
        for n in [3, 4, 6]:
            if n == 3:
                C = 1000
                expected_result = 0.0625 * C + 35.526
            elif n == 4:
                C = 1000
                expected_result = 0.0761 * C + 69.522
            elif n == 6:
                C = 1000
                expected_result = 0.1169 * C + 132.0
            
            result = modular_quad.m_battery(n, C)
            self.assertAlmostEqual(result, expected_result)
    
    def test_m_propeller(self):
        # Test the m_propeller function
        for d in [7.62, 10.16, 11.9, 15.4, 16]:
            if d == 7.62:
                expected_result = 0.4
            elif d == 10.16:
                expected_result = 0.5
            elif d == 11.9:
                expected_result = 0.6
            elif d == 15.4:
                expected_result = 0.9
            else:
                expected_result = 0.04 * d - 0.2
            result = modular_quad.m_propeller(d)
            self.assertAlmostEqual(result, expected_result)
    
    def test_m_frame(self):
        for t in [3, 4]:
            if t == 3:
                l = 1000
                expected_result = 3e-6 * l**3 - 0.003 * l**2 + 1.3666 * l - 106.53
            elif t == 4:
                l = 1000
                expected_result = 4e-6 * l**3 - 0.004 * l**2 + 1.8221 * l - 142.04
            
            result = modular_quad.m_frame(t, l)
            self.assertAlmostEqual(result, expected_result)

    def test_GTOW(self):
        # Test the GTOW function
        m_m = 1000
        m_e = 200
        m_b = 300
        m_p = 400
        m_f = 500
        m_a = 600
        m_pl = 700
        expected_result = m_m + m_e + m_b + m_p + m_f + m_a + m_pl
        result = modular_quad.GTOW(m_m, m_e, m_b, m_p, m_f, m_a, m_pl)
        self.assertAlmostEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()