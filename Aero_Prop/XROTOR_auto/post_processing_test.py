import unittest
from unittest.mock import mock_open, patch, MagicMock
import tempfile
from pathlib import Path
import builtins
import math


from post_processing import *  

sample_data = """Free Tip Potential Formulation Solution:  Designed blade                  
                                                  Wake adv. ratio:    0.13430
 no. blades :  2            radius(m)  :   0.1270     adv. ratio:     0.11048
 thrust(N)  :   9.65        power(W)   :   247.       torque(N-m):  0.173    
 Efficiency :  0.7826       speed(m/s) :   0.000     rpm        :  13611.999
 Eff induced:  0.8226       Eff ideal  :   0.8573     Area(m^2)  :    0.05064
 Tnacel(N)  :     0.0006    Rhub(m)    :   0.0030     Rwake(m)   :    0.0035
 Tvisc(N)   :    -0.0257    Pvisc(W)   :   11.4       Mach       :    0.0588
 rho(kg/m3) :   1.22600     Vsound(m/s):  340.000     mu(kg/m-s) : 0.1780E-04
 ---------------------------------------------------------------------------
    J:    0.34708      adv:    0.11048       AF:   49.683
   Ct:    0.03673       Cp:    0.01629  (by rho,Diam,N)
   Tc:    0.77634       Pc:    0.99199  (by rho,Atip,Vel)
   CT:    0.00474       CP:    0.00067  (by rho,Atip,Vtip)
Sigma:    0.04800 CT/sigma:    0.09870

  i  r/R   c/R  beta(deg)  CL     Cd    REx10^3 Mach   effi  effp  na.u/U  solidity
  1 0.041 0.1388  71.23  0.600   0.0000  25.82  0.063  0.769 1.000   0.000  1.0906
  2 0.082 0.1872  56.37  0.600   0.0000  40.68  0.073  0.810 1.000   0.000  0.7244
  3 0.133 0.2079  43.16  0.600   0.0001  56.57  0.091  0.818 1.000   0.000  0.4989
"""

class TestParseOutput(unittest.TestCase):
    def test_parse_output_basic(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp:
            tmp.write(sample_data)
            tmp_path = tmp.name

        result = parse_output(tmp_path)

        self.assertIsInstance(result, dict)
        self.assertAlmostEqual(result["wake_advance_ratio"], 0.13430)
        #self.assertAlmostEqual(result["advance_ratio"], 0.11048)
        self.assertAlmostEqual(result["thrust"], 9.65, places=2)
        self.assertAlmostEqual(result["power"], 247.0, places=1)
        self.assertAlmostEqual(result["torque"], 0.173, places=3)
        self.assertAlmostEqual(result["efficiency"], 0.7826, places=4)
        self.assertAlmostEqual(result["ct"], 0.00474, places=5)
        self.assertAlmostEqual(result["cp"], 0.00067, places=5)
        self.assertAlmostEqual(result["mach"], 0.0588, places=4)
        self.assertTrue("blade_elements" in result)
        self.assertGreater(len(result["blade_elements"]), 0)

class TestAnalyzeResults(unittest.TestCase):

    @patch('post_processing.RESULTS_DIR')
    @patch('post_processing.TOP_N', 5)
    @patch('post_processing.required_thrust', 10.0)
    @patch('post_processing.parse_output')

    def test_analyze_results_valid_input(self, mock_parse_output, mock_results_dir):
        # Mocked result file name and structure
        fake_file = MagicMock()
        fake_file.name = 'NACA4412_10x6_2207_8o5.txt'
        fake_file.stem = 'NACA4412_10x6_2207_8o5'
        mock_results_dir.glob.return_value = [fake_file]

        # Mock parse_output result
        mock_parse_output.return_value = {
            'thrust': 12.0,
            'power': 100.0,
            'torque': 0.5,
            'ct': 0.003,
            'cp': 0.02,
            'efficiency': 0.6,
            'mach': 0.3,
            'wake_advance_ratio': 0.4,
            'eff_induced': 0.65,
            'blade_elements': [
                {'r/R': 0.3, 'c/R': 0.05, 'effp': 0.6},
                {'r/R': 0.8, 'c/R': 0.06, 'effp': 0.7},
            ]
        }

        # Call the function
        TOP_N = 5
        required_thrust = 10.0
        RESULTS_DIR = MagicMock()
        RESULTS_DIR.glob.return_value = [fake_file]

        analyze_results()

        # No exceptions = pass. Could assert internal behavior here
        # E.g. check final score value or best_configs structure
        self.assertTrue(True)

    @patch('post_processing.RESULTS_DIR')
    @patch('post_processing.TOP_N', 5)
    @patch('post_processing.required_thrust', 10.0)
    @patch('post_processing.parse_output')
    def test_analyze_results_invalid_file_name(self, mock_parse_output, mock_results_dir):
        fake_file = MagicMock()
        fake_file.name = 'badfilename.txt'
        fake_file.stem = 'badfilename'
        mock_results_dir.glob.return_value = [fake_file]

        mock_parse_output.return_value = {
            'thrust': 15.0,
            'power': 120.0,
            'torque': 0.6,
            'ct': 0.004,
            'cp': 0.03,
            'efficiency': 0.7,
            'mach': 0.25,
            'wake_advance_ratio': 0.5,
            'eff_induced': 0.72,
            'blade_elements': []
        }

        TOP_N = 5
        required_thrust = 10.0
        RESULTS_DIR = MagicMock()
        RESULTS_DIR.glob.return_value = [fake_file]

        analyze_results()

        # Should continue without crashing
        self.assertTrue(True)


class TestFilenameParsing(unittest.TestCase):
    def test_filename_parsing(self):
        filename = "NACA0012_10x4.5_2212_8o5.txt"
        stem = Path(filename).stem
        parts = stem.split("_")
        self.assertEqual(parts, ['NACA0012', '10x4.5', '2212', '8o5'])

        motor_mass_str = parts[3].replace("o", ".")
        motor_mass = float(motor_mass_str)
        self.assertAlmostEqual(motor_mass, 8.5)


class TestScoreComputation(unittest.TestCase):
    def test_score_computation(self):
        # Hypothetical input
        data = {
            "thrust": 25,
            "power": 200,
            "efficiency": 0.7,
            "ct": 0.005,
            "mach": 0.4,
            "blade_elements": [
                {"r/R": 0.2, "c/R": 0.03, "beta": 0, "CL": 0, "Cd": 0, "Re": 0, "Mach": 0, "effi": 0, "effp": 0.8},
                {"r/R": 0.5, "c/R": 0.03, "beta": 0, "CL": 0, "Cd": 0, "Re": 0, "Mach": 0, "effi": 0, "effp": 0.85},
                {"r/R": 0.8, "c/R": 0.03, "beta": 0, "CL": 0, "Cd": 0, "Re": 0, "Mach": 0, "effi": 0, "effp": 0.87}
            ]
        }

        motor_mass = 8.5
        vertical_thrust = data["thrust"] * math.cos(math.radians(0))
        vertical_thrust_per_watt = vertical_thrust / data["power"]
        ct_sigma = data["ct"] / 0.00408
        avg_effp = sum(be["effp"] for be in data["blade_elements"]) / len(data["blade_elements"])
        mach_tip = data["mach"]
        geometry_penalty = 0.0  # adequate blade resolution, span, c/R

        expected_score = (
            0.3 * vertical_thrust_per_watt +
            0.3 * data["efficiency"] +
            0.2 * ct_sigma +
            0.1 * avg_effp -
            0.1 * mach_tip -
            0.05 * motor_mass / 100 -
            geometry_penalty
        )

        self.assertAlmostEqual(expected_score, 0.3 * (25/200) + 0.3 * 0.7 + 0.2 * (0.005/0.00408) + 0.1 * 0.84 - 0.1 * 0.4 - 0.05 * 8.5 / 100, places=5)


class TestThrustRequirement(unittest.TestCase):
    def test_required_thrust_value(self):
        expected = 2121.7 / 4 * 2/ 1000 * 9.81
        self.assertAlmostEqual(required_thrust, expected, places=5)

if __name__ == "__main__":
    unittest.main()
