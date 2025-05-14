import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Trade_off.datasets import *
from Trade_off.Quadcopter.propulsion_iteration import converge_gtow_and_prop
from Trade_off.Quadcopter.weight_estimation import m_pl, m_payload
import math

def full_system_loop(m_pl, P_payload, t_flight, tol=1e-2, max_outer=2, max_gtow=5000):
    prev_gtow = 0
    battery_guess = battery_db[0]

    discharge_eff = 0.9

    for i in range(max_outer):
        print(f"\n========================")
        print(f"   Outer Loop {i+1} - Weight + Power")
        print(f"========================")

        # Step 1: GTOW + motor/prop optimization with current battery guess
        result = converge_gtow_and_prop(
            m_pl,
            battery_capacity=battery_guess['capacity'],
            n_cells=battery_guess['cells'], 
            battery_override=battery_guess,
        )

        # Step 2: total power consumption
        motor = result['motor']
        #T_motor = result['T_motor']  
        T_motor = motor["thrust"]  # thrust per motor [g]
        print(f"Motor Thrust: {T_motor:.2f} g")
        motor_eff = motor['efficiency'] 
        print(f"Motor Efficiency: {motor_eff:.2f}")

        #P_motor = T_motor / motor_eff   # watts
        P_motor = motor["power"]
        print(f"Motor Power: {P_motor:.2f} W")
        P_total = 4 * P_motor + P_payload
        print(f"Estimated Power Use: {P_total:.2f} W")

        # Step 3: Required energy
        E_required = P_total * t_flight  # Wh

        # Step 4: Find best battery from database
        best_battery = None
        min_mass = float('inf')

        P_required = P_total / 4  # to have like 4 batteries  # or any specific power required for the system
        for b in battery_db:
            usable_energy = (b['voltage'] * b['capacity'] / 1000) * discharge_eff  # Wh

            # Check if the battery can supply the required power (C-rating check)
            if b['C-rating'] is None:
                continue
            max_discharge_power = b['capacity'] * b['C-rating'] * b['voltage'] / 1000  # in watts
            if usable_energy >= E_required and b['mass'] < min_mass and max_discharge_power >= P_required:
                best_battery = b
                min_mass = b['mass']
        if not best_battery:
            raise RuntimeError("No suitable battery found in the database.")
        print(f"Selected Battery: {best_battery['id']} | {best_battery['capacity']} mAh | {best_battery['cells']}S | {best_battery['mass']} g")

        # Step 5: Convergence check
        if abs(result['GTOW'] - prev_gtow) < tol:
            print("\nSYSTEM CONVERGED")
            return {
                **result,
                'P_total': P_total,
                'E_required': E_required,
                'battery': best_battery
            }

        if result['GTOW'] > max_gtow:
            print(f"GTOW exceeds the cap of {max_gtow} g. Stopping the iteration.")
            raise RuntimeError("GTOW exceeded the maximum limit.")
        
        battery_guess = best_battery
        prev_gtow = result['GTOW']

    raise RuntimeError("System did not converge after all iterations.")



def analyze_performance(result, n_rotors=4, cruise_speed_kmh=40):
    g = 9.81  # m/s²
    W_takeoff = result['GTOW'] / 1000 * g  # N
    T_max = result['T_max'] / 1000 * g  # N
    T_W = T_max / W_takeoff

    flight_duration_hr = result['E_required'] / result['P_total']  # h
    range_km = cruise_speed_kmh * flight_duration_hr

    # disk loading
    A_tot_prop = n_rotors * (math.pi * (result["propeller"]['diameter'] / 200) ** 2)   # m²
    disk_loading = result['GTOW'] / 1000 / A_tot_prop  # kg/m²

    fuel_weight_kg = result['battery']['mass'] / 1000  # battery as energy source
    inverse_W_takeoff = 1 / (result['GTOW'] / 1000)  # 1/kg

    # total power to horsepower (1 HP = 745.7 W)
    power_hp = result['P_total'] / 745.7

    return {
        'T/W': T_W,
        'Range (L)': range_km,
        'Flight Duration (T)': flight_duration_hr,
        'Cruising Speed (V_crs) random number now poop': cruise_speed_kmh,
        'Disk Loading (W/S) downwash': disk_loading,
        '1/W_takeoff': inverse_W_takeoff,
        'Fuel Weight (W_fuel)': fuel_weight_kg,
        'Power Plant Parameter (N_take-off)': power_hp
    }



if __name__ == "__main__":
    """base_m_pl = m_payload(198, 19, 230, 0, 150)  # g
    base_P_payload = 65  # watts
    t_flight = 0.416  # hours

    # Margins: -20%, baseline, +20%
    margin_factors = [0.8, 1.0, 1.2]

    for margin in margin_factors:

        adjusted_m_pl = base_m_pl * margin
        adjusted_P_payload = base_P_payload * margin
        print(f"\n==== Running Analysis for m_pl {int(margin*100)}%, P_payload {int(margin*100)}% ====")
        try:
            results = full_system_loop(adjusted_m_pl, adjusted_P_payload, t_flight=t_flight)
            print(results)
            performance = analyze_performance(results, n_rotors=4)
            for k, v in performance.items():
                print(f"{k}: {v:.3f}")
        except RuntimeError as e:
            print(f"Failed to converge: {e}")"""
    m_pl = m_payload(198, 19, 230, 0, 150)  # g
    P_payload = 65  # watts
    t_flight = 0.416  # hours

    results = full_system_loop(m_pl, P_payload, t_flight=t_flight)
    print(results)
    performance = analyze_performance(results, n_rotors=4)
    for k, v in performance.items():
        print(f"{k}: {v:.3f}")

    