import unittest
from unittest.mock import patch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Trade_off.Quadcopter_swarm import weight_estimation_swarm as wes
from Trade_off.Quadcopter_swarm import propulsion_iteration_swarm as pis

# class TestWeightEstimationSwarm(unittest.TestCase):

#     def test_payload_sum(self):
#         """Test payload mass sum is correct"""
#         result = wes.m_payload(100, 50, 230, 69, 169)  # g
#         expected = 100 + 50 + 230 + 69 + 169
#         self.assertEqual(result, expected)

#     def test_avionics_fraction(self):
#         """Test avionics mass is 12% of m0"""
#         m0 = 1000
#         expected = 0.12 * m0
#         self.assertAlmostEqual(wes.m_avionics(m0), expected)

#     def test_motor_weight_estimation(self):
#         """Test motor weight for a known thrust value"""
#         thrust = 500  # g
#         weight = wes.m_motor(thrust)
#         self.assertTrue(weight > 0)

#     def test_battery_weight_3s(self):
#         self.assertAlmostEqual(wes.m_battery(3, 1000), 0.0625 * 1000 + 35.526)

#     def test_battery_weight_4s(self):
#         self.assertAlmostEqual(wes.m_battery(4, 1000), 0.0761 * 1000 + 69.522)

#     def test_battery_weight_6s(self):
#         self.assertAlmostEqual(wes.m_battery(6, 1000), 0.1169 * 1000 + 132.0)

#     def test_propeller_weight_known(self):
#         """Bullshit test for known propeller weights"""
#         """The thing is that the value from semi empirical is fucked up, it gives negative shit"""
#         self.assertEqual(wes.m_propeller(10.16), 0.5)

#     def test_frame_weight_formula(self):
#         """Test frame if shit gives positive values"""
#         mass = wes.m_frame(t=4, l=300)
#         self.assertTrue(mass > 0)
   
#     def test_frame_function(self):
#         """Test m_frame returns expected values for given t and l."""
#         # Test with t = 3
#         l_val = 300
#         mass_frame_3 = wes.m_frame(3, l_val)
#         expected_frame_3 = 3e-6 * l_val**3 - 0.003 * l_val**2 + 1.3666 * l_val - 106.53
#         self.assertAlmostEqual(mass_frame_3, expected_frame_3, places=2)

#         # Test with t = 4
#         mass_frame_4 = wes.m_frame(4, l_val)
#         expected_frame_4 = 4e-6 * l_val**3 - 0.004 * l_val**2 + 1.8221 * l_val - 142.04
#         self.assertAlmostEqual(mass_frame_4, expected_frame_4, places=2)

#     def test_gtow_computation(self):
#         """Test final GTOW result is the sum of components"""
#         result = wes.GTOW(100, 20, 50, 5, 60, 15, 200)
#         self.assertEqual(result, 100 + 20 + 50 + 5 + 60 + 15 + 200)

#     def test_converge_gtow_success(self):
#         """Test GTOW convergence on a simple payload list"""
#         payloads = [250]
#         result = wes.converge_gtow(payloads)
#         self.assertEqual(len(result), 1)
#         self.assertIsInstance(result[0], tuple)
#         self.assertAlmostEqual(result[0][0], wes.GTOW(*result[0][3:]))  # m_total ≈ GTOW

#     def test_converge_gtow_output_format(self):
#         """Test the output format and internal consistency of converge_gtow."""
#         """i love copilot <3."""
#         payloads = [250]
#         result = wes.converge_gtow(payloads)
#         # Check that one result is returned
#         self.assertEqual(len(result), 1)
#         # Unpack results (expecting 10 elements, as defined in converge_gtow)
#         (m_total, T_total, T_motor, m_m, m_e, m_b, m_p, m_f, m_a, m_pl) = result[0]
#         # Verify the tuple format has 10 elements
#         self.assertEqual(len(result[0]), 10)
#         # Verify that m_total equals the sum of components (i.e. GTOW)
#         self.assertAlmostEqual(m_total, wes.GTOW(m_m, m_e, m_b, m_p, m_f, m_a, m_pl), places=2)
# print("AAAAAAAAAAAAAAAAAAAAAAAAAA")
class TestConvergeGtowAndProp(unittest.TestCase):
    def setUp(self):
        # Single-drone payload for simplicity
        self.payloads = [100.0]

        # A fake motor dict for our selector stub
        self.fake_motor = {
            'id': 'FAKE_MTR',
            'mass': 50,
            'thrust': 60,       # must be ≥ T_motor
            'efficiency': 0.85,
            'diameter': 30.0,
            'peak_current': 12
        }

        # A full tuple that mimic converge_gtow output:
        # (GTOW, T_max, T_motor, m_motor, m_ESC, m_battery,
        #  m_propeller, m_frame, m_avionics, m_payload)
        self.stub_gtow_tuple = (100, 200, 50, 10, 5, 20, 3, 15, 8, 100)

    @patch('Trade_off.Quadcopter_swarm.propulsion_iteration_swarm.converge_gtow')
    @patch('Trade_off.Quadcopter_swarm.propulsion_iteration_swarm.select_best_motor_and_prop')
    def test_convergence_and_result_structure(self, mock_select, mock_converge):
        # 1) Stub converge_gtow so that two iterations occur:
        #    both calls return the same tuple in a list of length=1
        mock_converge.side_effect = [
            [self.stub_gtow_tuple],
            [self.stub_gtow_tuple]
        ]

        # 2) Stub selector to capture calls and return our fake config
        calls = []
        def fake_selector(gtow, T_motor):
            calls.append((gtow, T_motor))
            return {
                'motor': self.fake_motor,
                'prop_diameter': 12.7,
                'metric': 0.01
            }
        mock_select.side_effect = fake_selector

        # 3) Run the function under test
        results = pis.converge_gtow_and_prop(
            payloads=self.payloads,
            battery_capacity=1000,  # unused by our stub
            n_cells=4,
            tol=1e-6,
            max_iter=5
        )

        # ---- Assertions ----

        # converge_gtow called exactly twice (2 iterations)
        self.assertEqual(mock_converge.call_count, 2)

        # select_best_motor_and_prop called once, with the GTOW and T_motor from stub
        self.assertEqual(calls, [(100, 50)])

        # We get a single-element list back
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)

        res = results[0]

        # Must contain these keys
        expected_keys = {
            'GTOW','T_max','T_motor','motor','propeller',
            'm_motor','m_ESC','m_battery','m_propeller',
            'm_frame','m_avionics','m_payload'
        }
        self.assertTrue(expected_keys.issubset(res.keys()))

        # Values should match our stubs
        self.assertEqual(res['GTOW'], 100)
        self.assertEqual(res['T_max'], 200)
        self.assertEqual(res['T_motor'], 50)

        self.assertIs(res['motor'], self.fake_motor)
        self.assertEqual(res['propeller']['diameter'], 12.7)

        # And the component masses should come from stub_gtow_tuple:
        self.assertEqual(res['m_motor'],    10)
        self.assertEqual(res['m_ESC'],       5)
        self.assertEqual(res['m_battery'],  20)
        self.assertEqual(res['m_propeller'], 3)
        self.assertEqual(res['m_frame'],    15)
        self.assertEqual(res['m_avionics'],  8)
        self.assertEqual(res['m_payload'],100)

if __name__ == "__main__":
    unittest.main()

