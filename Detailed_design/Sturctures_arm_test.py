import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import numpy as np
import matplotlib.pyplot as plt
import Structures_arm

class TestStructuresArm(unittest.TestCase):
    def setUp(self):
        # Dummy values for use in tests
        self.F_T = 10.0
        self.W = 2.0
        self.alpha = np.radians(30)
        self.beta = np.radians(45)
        self.T = 1.5
        self.R_position = np.array([1.0, 2.0, 3.0])
        self.L = 2.0
        self.h = 0.5
        self.d0 = 0.1
        self.t = 0.01
        self.E = 200e9
        self.G = 80e9
        self.rho = 2700
        self.K = 2
        self.A = np.pi * (self.d0**2 - (self.d0 - 2*self.t)**2) / 4
        self.I = np.pi * (self.d0**4 - (self.d0 - 2*self.t)**4) / 64
        self.J = np.pi * (self.d0**4 - (self.d0 - 2*self.t)**4) / 32

    def test_calculate_arm_forces(self):
        # Manual calculation
        F_applied = np.array([
            self.F_T * np.sin(self.beta),
            self.W - (self.F_T * np.cos(self.alpha)),
            -(self.F_T * np.sin(self.alpha))
        ])
        T_applied = self.T * np.array([
            np.sin(self.beta),
            -np.cos(self.alpha),
            -np.sin(self.alpha)
        ])
        F_reaction = -F_applied
        M_reaction = -np.cross(self.R_position, F_applied) - T_applied

        F, M = Structures_arm.calculate_arm_forces(
            self.F_T, self.W, self.alpha, self.beta, self.T, self.R_position
        )
        np.testing.assert_allclose(F, F_reaction)
        np.testing.assert_allclose(M, M_reaction)

        # Test with extreme values
        F_T_extreme = 1
        W_extreme = 0
        alpha_extreme = np.radians(90)
        beta_extreme = np.radians(0)
        T_extreme = 1
        R_position_extreme = np.array([0, 1, 1])
        F2, M2 = Structures_arm.calculate_arm_forces(
            F_T_extreme, W_extreme, alpha_extreme, beta_extreme, T_extreme, R_position_extreme
        )
        self.assertTrue((np.isclose(F2[1], 0)) & (np.isclose(M2[1], 0)))
        self.assertTrue((np.isclose(F2[0], 0)) & (F2[2] != 0))
        self.assertTrue((M2[0] != 0) & (M2[2] != 0))

    def test_calculate_section(self):
        I, J, A = Structures_arm.calculate_section(self.d0, self.t)
        I_expected = np.pi * (self.d0**4 - (self.d0 - 2*self.t)**4) / 64
        J_expected = np.pi * (self.d0**4 - (self.d0 - 2*self.t)**4) / 32
        A_expected = np.pi * (self.d0**2 - (self.d0 - 2*self.t)**2) / 4
        self.assertAlmostEqual(I, I_expected)
        self.assertAlmostEqual(J, J_expected)
        self.assertAlmostEqual(A, A_expected)

    def test_calculate_shear_stress(self):
        V = np.array([5.0, 10.0, 0.0])
        M = np.array([0.0, 0.0, 2.0])
        Q = 2 * ((self.d0 / 2)**3 - ((self.d0 - 2 * self.t) / 2)**3) / 3
        shear_y = V[1] * Q / (self.I * self.t)
        shear_x = V[0] * Q / (self.I * self.t)
        torsion_shear = M[2] / (2 * self.t * np.pi * (self.d0 - self.t)**2)
        expected = np.array([shear_x, shear_y, torsion_shear])
        result = Structures_arm.calculate_shear_stress(V, M, self.d0, self.I, self.J, self.t)
        np.testing.assert_allclose(result, expected)

    def test_calculate_neutral_axis(self):
        M = np.array([0.0, 2.0, 0.0])
        expected = np.pi / 2
        result = Structures_arm.calculate_neutral_axis(M)
        self.assertAlmostEqual(result, expected)
        M2 = np.array([1.0, 1.0, 0.0])
        expected2 = np.arctan2(1.0, 1.0)
        result2 = Structures_arm.calculate_neutral_axis(M2)
        self.assertAlmostEqual(result2, expected2)
        M3 = np.array([0.0, 0.0, 0.0])
        expected3 = ValueError("Applied moment cannot be zero for neutral axis calculation.")
        with self.assertRaises(ValueError):
            Structures_arm.calculate_neutral_axis(M3)
            
    def test_calculate_axial_stress(self):
        M = np.array([2.0, 3.0, 0.0])
        NA_alpha = np.pi / 4
        x = self.d0 / 2 * np.cos(NA_alpha + np.pi / 2)
        y = self.d0 / 2 * np.sin(NA_alpha + np.pi / 2)
        expected = (M[0] * y - M[1] * x) / self.I
        result = Structures_arm.calculate_axial_stress(M, self.I, self.d0, self.t, NA_alpha)
        self.assertAlmostEqual(result, expected)

    def test_calculate_stresses(self):
        F = np.array([1.0, 2.0, 3.0])
        M = np.array([2.0, 3.0, 4.0])

        NA_alpha = Structures_arm.calculate_neutral_axis(M)
        bending_stress = Structures_arm.calculate_axial_stress(M, self.I, self.d0, self.t, NA_alpha)
        shear_stress = Structures_arm.calculate_shear_stress(F, M, self.d0, self.I, self.J, self.t)
        axial_stress = -F[2] / self.A

        result = Structures_arm.calculate_stresses(F, M, self.I, self.J, self.A, self.d0, self.t)

        self.assertAlmostEqual(result[0], bending_stress)
        np.testing.assert_allclose(result[1], shear_stress)
        self.assertAlmostEqual(result[2], axial_stress)
        self.assertAlmostEqual(result[3], NA_alpha)

    def test_calculate_buckling(self):
        expected = (np.pi**2 * self.E * self.I) / (self.L**2)
        result = Structures_arm.calculate_buckling(self.E, self.I, self.L)
        self.assertAlmostEqual(result, expected)

    def test_calculate_deformation(self):
        F = 10.0
        M = 5.0
        # Only force
        defl_F = F * self.L**3 / (3 * self.E * self.I)
        rot_F = F * self.L**2 / (2 * self.E * self.I)
        # Only moment
        defl_M = -M * self.L**2 / (2 * self.E * self.I)
        rot_M = -M * self.L / (self.E * self.I)
        deflections, rotations = Structures_arm.calculate_deformation(F, M, self.L, self.E, self.I)
        np.testing.assert_allclose(deflections, [defl_F, defl_M])
        np.testing.assert_allclose(rotations, [rot_F, rot_M])

    def test_calculate_torsion_deflection(self):
        T = 3.0
        expected = T * self.L / (self.G * self.J)
        result = Structures_arm.calculate_torsion_deflection(T, self.L, self.G, self.J)
        self.assertAlmostEqual(result, expected)

    def test_calculate_mass(self):
        volume = np.pi * (self.d0**2 - (self.d0 - 2*self.t)**2) / 4 * self.L + \
                 np.pi * (self.d0**2 - (self.d0 - 2*self.t)**2) / 4 * self.h
        expected = self.rho * volume
        result = Structures_arm.calculate_mass(self.rho, self.L, self.h, self.d0, self.t)
        self.assertAlmostEqual(result, expected)
    
    def test_sensitivity_analysis_deformation(self):
        """
        Sensitivity analysis: vary alpha, t, d0, E and plot the calculated deformation.
        """
        # Fixed parameters
        W = self.W
        beta = self.beta
        R_position = self.R_position
        L = self.L
        G = self.G

        # Ranges for sensitivity
        alphas = np.radians(np.linspace(0, 90, 10))
        ts = np.linspace(0.0005, 0.005, 10)
        d0s = np.linspace(0.005, 0.05, 10)
        Es = np.linspace(1e9, 70e9, 10)

        # Sensitivity to alpha
        deformations_alpha = []
        for alpha in alphas:
            F, M = Structures_arm.calculate_arm_forces(self.F_T, W, alpha, beta, self.T, R_position)
            I, J, A = Structures_arm.calculate_section(self.d0, self.t)
            defl, _ = Structures_arm.calculate_deformation(-F[1], -M[0], L, self.E, I)
            deformations_alpha.append(np.sum(defl))
        plt.figure()
        plt.plot(np.degrees(alphas), np.array(deformations_alpha)*1e3)
        plt.xlabel(r'$\alpha$ (deg)', fontsize=16)
        plt.ylabel(r'$y$ Deformation (mm)', fontsize=16)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.title('Sensitivity: Deformation vs Alpha')
        plt.grid(True)

        # Sensitivity to wall thickness t
        deformations_t = []
        for t in ts:
            I, J, A = Structures_arm.calculate_section(self.d0, t)
            F, M = Structures_arm.calculate_arm_forces(self.F_T, W, self.alpha, beta, self.T, R_position)
            defl, _ = Structures_arm.calculate_deformation(-F[1], -M[0], L, self.E, I)
            deformations_t.append(np.sum(defl))
        plt.figure()
        plt.plot(ts*1e3, np.array(deformations_t)*1e3)
        plt.xlabel(r'Wall Thickness $t$ (mm)', fontsize=16)
        plt.ylabel(r'$y$ Deformation (mm)', fontsize=16)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)

        plt.title('Sensitivity: Deformation vs Wall Thickness')
        plt.grid(True)

        # Sensitivity to d0
        deformations_d0 = []
        for d0 in d0s:
            if d0 < self.t or np.isclose(d0, self.t, atol=1e-6):
                deformations_d0.append(np.nan)  # Avoid division by zero in section calculations
                continue
            I, J, A = Structures_arm.calculate_section(d0, self.t)
            F, M = Structures_arm.calculate_arm_forces(self.F_T, W, self.alpha, beta, self.T, R_position)
            defl, _ = Structures_arm.calculate_deformation(-F[1], -M[0], L, self.E, I)
            deformations_d0.append(np.sum(defl))
        plt.figure()
        plt.plot(d0s*1e3, np.array(deformations_d0)*1e3)
        plt.xlabel(r'Outer Diameter $d_0$ (mm)', fontsize=16)
        plt.ylabel(r'$y$ Deformation (mm)', fontsize=16)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.title('Sensitivity: Deformation vs Outer Diameter')
        plt.grid(True)

        # Sensitivity to E
        deformations_E = []
        for E in Es:
            I, J, A = Structures_arm.calculate_section(self.d0, self.t)
            F, M = Structures_arm.calculate_arm_forces(self.F_T, W, self.alpha, beta, self.T, R_position)
            defl, _ = Structures_arm.calculate_deformation(-F[1], -M[0], L, E, I)
            deformations_E.append(np.sum(defl))
        plt.figure()
        plt.plot(Es*1e-9, np.array(deformations_E)*1e3)
        plt.xlabel(r"Young's Modulus $E$ (GPa)", fontsize=16)
        plt.ylabel(r'$y$ Deformation (mm)', fontsize=16)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.title('Sensitivity: Deformation vs Young\'s Modulus')
        plt.grid(True)
        plt.show()


if __name__ == '__main__':
    unittest.main()