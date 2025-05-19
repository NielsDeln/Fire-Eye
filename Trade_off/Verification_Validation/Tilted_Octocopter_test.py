import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import numpy as np
from Trade_off.Tilted_Octocopter import propulsion_iteration_octo
from Trade_off.Tilted_Octocopter import weight_estimation_octo
from Trade_off.Tilted_Octocopter import power_iteration_octo

class TestWeightEstimation(unittest.TestCase):
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
        result = weight_estimation_octo.m_payload(m_dmcomm, m_navig, m_mapping, m_control, m_forensics)
        self.assertAlmostEqual(result, expected_result)
    
    def test_m_avionics(self):
        # Test the m_avionics function
        m0 = 1000
        expected_result = 0.12 * m0
        result = weight_estimation_octo.m_avionics(m0)
        self.assertAlmostEqual(result, expected_result)
    
    def test_m_motor(self):
        # Test the m_motor function
        T_motor = 1000
        expected_result = (1e-07 * T_motor**3 - 0.0003 * T_motor**2 + 0.2783 * T_motor - 56.133)/4
        result = weight_estimation_octo.m_motor(T_motor)
        self.assertAlmostEqual(result, expected_result)
    
    def test_m_ESC(self):
        # Test the m_ESC function
        I_max = 30
        battery_cells = 4
        expected_result = (102.71*I_max+3510*battery_cells+2.2781*I_max**2+73.77*battery_cells**2+32.86*I_max*battery_cells)*10**(-6) *1000  #g
        result = weight_estimation_octo.m_ESC(I_max, battery_cells)
        self.assertAlmostEqual(result, expected_result)

    def test_m_propeller(self):
        # Test the m_propeller function
        for d in [5, 7.62, 10, 15.4]:
            if d == 5: 
                expected_result = 0.5
            elif d == 7.62:
                expected_result = 0.8
            elif d == 10:
                expected_result = 1
            else:
                expected_result = 0.04 * d - 0.2
            result = weight_estimation_octo.m_propeller(d)
            self.assertAlmostEqual(result, expected_result)
        
    def test_m_frame(self):
        # Test the m_frame function
        D_UAV = 0.302
        expected_result = 2.255 * D_UAV**2.084 * 1000
        result = weight_estimation_octo.m_frame(D_UAV)
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
        result = weight_estimation_octo.GTOW(m_m, m_e, m_b, m_p, m_f, m_a, m_pl)
        self.assertAlmostEqual(result, expected_result)


class TestPropulsionIteration(unittest.TestCase):
    def setUp(self):
        pass 


class TestPowerIteration(unittest.TestCase):
    def setUp(self):
        pass 
    

if __name__ == '__main__':
    unittest.main()