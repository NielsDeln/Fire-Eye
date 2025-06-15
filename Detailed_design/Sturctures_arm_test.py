import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import numpy as np
from Detailed_design import Structures_arm

class TestStructuresArm(unittest.TestCase):
    def setUp(self):
        pass

    def test_calculate_deformation(self):
        # Test the calculate_deformation function
        force = 1000  # N
        moment = 500  # Nm
        length = 0.5  # m
        E = 200e9  # Pa
        I = 1e-6  # m^4
        expected_y_deformation = -force * length**3 / (3 * E * I)
        expected_y_rotation = -moment * length / (E * I)
        
        y_deformation, y_rotation = Structures_arm.calculate_deformation(force, moment, length, E, I)
        
        self.assertAlmostEqual(y_deformation, expected_y_deformation)
        self.assertAlmostEqual(y_rotation, expected_y_rotation)
    
    def test_axial_stress(self):
        # Test the axial_stress function
        force = 1000
        area = 0.01
        expected_stress = force / area
        stress = Structures_arm.axial_stress(force, area)
        self.assertAlmostEqual(stress, expected_stress
                               )


if __name__ == '__main__':
    unittest.main()