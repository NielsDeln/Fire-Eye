import unittest
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import numpy as np
from Trade_off.Quadcopter import propulsion_iteration
from Trade_off.Quadcopter import weight_estimation
from Trade_off.Quadcopter import power_iteration

class TestPropulsionIteration(unittest.TestCase):
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
        result = weight_estimation.m_payload(m_dmcomm, m_navig, m_mapping, m_control, m_forensics)
        self.assertAlmostEqual(result, expected_result)
    
    def test_m_avionics(self):
        # Test the m_avionics function
        m0 = 1000
        expected_result = 0.12 * m0
        result = weight_estimation.m_avionics(m0)
        self.assertAlmostEqual(result, expected_result)

    def test_m_motor(self):
        # Test the m_motor function
        T_motor = 1000
        expected_result = 1e-07 * T_motor**3 - 0.0003 * T_motor**2 + 0.2783 * T_motor - 56.133
        result = weight_estimation.m_motor(T_motor)
        self.assertAlmostEqual(result, expected_result)

    def test_m_ESC(self):
        # Test the m_ESC function
        I_max = 30
        expected_result = 0.9546* I_max - 2.592
        result = weight_estimation.m_ESC(I_max)
        self.assertAlmostEqual(result, expected_result)

    def test_m_battery(self):
         for n in [3, 4, 6]:
            C = 5000
            if n == 3:
                expected_result = 0.0625 * C + 35.526
            elif n == 4:
                expected_result = 0.0761 * C + 69.522
            elif n == 6:
                expected_result = 0.1169 * C + 132.0
            result = weight_estimation.m_battery(n, C)
            self.assertAlmostEqual(result, expected_result)

    def test_m_propeller(self):
        for d in [7.62, 10.16, 11.9, 15.4]:
            if d == 7.62:
                expected_result = 0.4
            elif d == 10.16:
                expected_result = 0.5
            elif d == 11.9:
                expected_result = 0.6
            elif d == 15.4:
                expected_result = 0.9
            result = weight_estimation.m_propeller(d)
            self.assertAlmostEqual(result, expected_result)
    
    def test_m_frame(self):
        for t in [3, 4]:
            l = 300
            if t == 3:
                expected_result = 3e-6 * l**3 - 0.003 * l**2 + 1.3666 * l - 106.53
            elif t == 4:
                expected_result = 4e-6 * l**3 - 0.004 * l**2 + 1.8221 * l - 142.04
            result = weight_estimation.m_frame(t, l)
            self.assertAlmostEqual(result, expected_result)
    
    def test_GTOW(self):
        m_m = 1000
        m_e = 200
        m_b = 300
        m_p = 400
        m_f = 500
        m_a = 600
        m_pl = 700
        expected_result = m_m + m_e + m_b + m_p + m_f + m_a + m_pl
        result = weight_estimation.GTOW(m_m, m_e, m_b, m_p, m_f, m_a, m_pl)
        self.assertAlmostEqual(result, expected_result)
    
    def test_evaluate_motor_prop_combo(self):
        mass_aircraft = 1000
        prop_diameter = 10.16
        prop_pitch = 5.0
        motor = {
            'efficiency': 0.85,
            'mass': 200,
            'thrust': 1500,
            'power': 500,
        }
        rho = 1.225

        M = mass_aircraft / 1000  # grams → kg
        d_m = prop_diameter / 100  # cm → meters
        A = np.pi * (d_m / 2)**2  # rotor disc area in m²
        
        # induced velocity V1 under rotor
        V1 = np.sqrt((M * 9.81) / (2 * rho * A))
        V2 = 2 * V1
        
        # penalty terms 
        thrust_efficiency = motor['efficiency'] - 0.01 * abs(prop_pitch - 5.0)
        mass_penalty = 0.001 * motor['mass']
        
        expected_result = V2 + mass_penalty - 0.2 * thrust_efficiency
        result = propulsion_iteration.evaluate_motor_prop_combo(motor, prop_diameter, mass_aircraft)
        self.assertAlmostEqual(result, expected_result)

    def test_select_best_motor_and_prop(self):
        GTOW = 1000
        T_motor = 1500
        motor_db = [
            {'id': 'motor1', 'efficiency': 0.85, 'mass': 200, 'thrust': 1500, 'power': 500, 'prop_diameter': 10.16},
            {'id': 'motor2', 'efficiency': 0.90, 'mass': 250, 'thrust': 1600, 'power': 450, 'prop_diameter': 11.9},
            {'id': 'motor3', 'efficiency': None, 'mass': 300, 'thrust': 1700, 'power': 700, 'prop_diameter': 15.4},
        ]

        best_combo = propulsion_iteration.select_best_motor_and_prop(GTOW, T_motor, motor_db)
        self.assertIsNotNone(best_combo)
        self.assertEqual(best_combo['motor']['id'], 'motor2')

    def test_analyze_performance(self):
        drone = {
            'GTOW': 1000,  # g
            'T_max': 2000,  # g
            'P_total': 5000,  # W
            'propeller': {'diameter': 10.16},  # cm
            'motor': {'thrust': 1500},  # g
            'battery': {'voltage': 22.2, 'capacity': 5000, 'C-rating': 20},  # V, mAh, C
            'E_required': 10000,  # Wh
        }
        n_rotors = 4
        cruise_speed_kmh = 50
        rho = 1.225  # kg/m³
        # Calculate performance metrics
        g = 9.81  # m/s²
        W_takeoff = drone['GTOW'] / 1000 * g  # N
        T_max = drone['T_max'] / 1000 * g  # N
        T_W = T_max / W_takeoff

        battery = drone['battery']
        energy_batt = (battery['voltage'] * battery['capacity'] / 1000) * 0.9
        discharg_p = battery['capacity'] * battery['C-rating'] * battery['voltage'] / 1000 # W 

        # adding this in case there's more than 1 battery 
        n_needed_energy = np.ceil(drone["E_required"] / energy_batt)
        n_needed_power = np.ceil((drone["P_total"] / 2) / discharg_p)
        n_batt = max(n_needed_energy, n_needed_power)
        flight_duration_hr = energy_batt * n_batt / (drone["P_total"] / 2)  # h

        range_km = cruise_speed_kmh * flight_duration_hr
        

        # disk loading
        A_prop = (np.pi * (drone["propeller"]['diameter'] / 200) ** 2) 
        A_tot_prop = n_rotors * A_prop  # m²
        disk_loading = drone['GTOW'] / 1000 / A_tot_prop  # kg/m²

        inverse_W_takeoff = 1 / (drone['GTOW'] / 1000)  # 1/kg

        #V2
        V1 = np.sqrt((W_takeoff/ n_rotors) / (2 * rho * A_prop))
        V2 = 2 * V1

        # total power to horsepower (1 HP = 745.7 W)
        power_hp = drone['P_total'] / 745.7

        # hover power 
        P_hover = n_rotors * (drone['motor']["thrust"] * 9.81 / 1000) ** (3/2) /( (2*rho*A_prop)**0.5) # W

        expected_result = {
            'T/W': T_W,
            'Range (R)': range_km,
            'Flight Duration': flight_duration_hr,
            'Cruising Speed (V_crs)': cruise_speed_kmh,
            'Disk Loading downwash': disk_loading,
            '1/W_takeoff': inverse_W_takeoff,
            'Power Plant Parameter (N_take-off)': power_hp,
            'Downwash velocity': V2,
            "Power to hover": P_hover,
        }

        result = power_iteration.analyze_performance(drone, n_rotors, cruise_speed_kmh, rho)
        self.assertTrue(np.allclose(list(result.values()), list(expected_result.values()), rtol=1e-2, atol=1e-2), "Performance metrics do not match expected values.")


if __name__ == "__main__":
        # Run the tests
        unittest.main()