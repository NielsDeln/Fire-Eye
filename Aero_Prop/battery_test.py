import unittest
from battery import *

class BatteryMotorSelectionTests(unittest.TestCase):

    def setUp(self):
        self.battery_dbx = [
            {"id": "bat1", "capacity": 2200, "voltage": 11.1, "mass": 180, "C-rating": 25},
            {"id": "bat2", "capacity": 3000, "voltage": 14.8, "mass": 250, "C-rating": 30},
            {"id": "bat3", "capacity": 1300, "voltage": 7.4, "mass": 120, "C-rating": 20},
        ]
        self.motor_db = [
            {"id": "mot1", "power": 260, "voltage": 12, "peak_current": 21.7, "max_thrust": 900},
            {"id": "mot2", "power": 200, "voltage": 11.1, "peak_current": 20, "max_thrust": 500},
        ]
        process_batteries(self.battery_dbx)
        preprocess_motors(self.motor_db)

    def test_max_current_computation(self):
        bat = self.battery_dbx[0]
        self.assertEqual(get_max_current(bat), (2200 / 1000) * 25)

    def test_energy_capacity_and_density(self):
        bat = self.battery_dbx[0]
        self.assertAlmostEqual(bat['energy_capacity'], round((2200/1000)*11.1, 2))
        self.assertTrue('energy_density' in bat)

    def test_motor_selection_filters_by_thrust(self):
        required_thrust = 8  # N
        results = get_batteries_motor(self.motor_db, self.battery_dbx, required_thrust)
        self.assertIn('mot1', results)
        self.assertNotIn('mot2', results)  # Not enough thrust

    def test_best_option_contains_keys(self):
        required_thrust = 8
        results = get_batteries_motor(self.motor_db, self.battery_dbx, required_thrust)
        mot1_results = results.get('mot1', {})
        self.assertIn('single_batteries', mot1_results)
        self.assertIn('combo_batteries', mot1_results)
        self.assertIn('total_batteries', mot1_results)


if __name__ == "__main__":
    unittest.main()
