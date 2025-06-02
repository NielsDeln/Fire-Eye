import os
import sys
import numpy as np
import math
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Trade_off.Tilted_Quadcopter.propulsion_iteration_tquad import converge_gtow_and_prop_tquad
from Trade_off.Tilted_Quadcopter.weight_estimation_tquad import  m_payload, converge_gtow_tquad
from Trade_off.datasets import *
from Trade_off.Quadcopter.power_iteration import analyze_performance, print_final_summary


def full_system_loop(m_pl, P_payload, t_flight, tol=1e-2, max_outer=10, max_gtow=5000):
    prev_gtow = 0
    battery_guess = battery_db[0]
    n_batt = 1

    throttle = 0.38

    discharge_eff = 0.9

    for i in range(max_outer):
        #print(f"\n========================")
        #print(f"   Outer Loop {i+1} - Weight + Power")
        #print(f"========================")

        # Step 1: GTOW + motor/prop optimization with current battery guess
        result = converge_gtow_and_prop_tquad(
            m_pl,
            battery_capacity=battery_guess['capacity'],
            n_cells=battery_guess['cells'], 
            battery_override=battery_guess,
            n_batteries=n_batt
        )

        # Step 2: total power consumption
        motor = result['motor']
        #T_motor = result['T_motor']  
        T_motor = motor["thrust"]  # thrust per motor [g]
        #print(f"Motor Thrust: {T_motor:.2f} g")
        motor_eff = motor['efficiency'] 
        #print(f"Motor Efficiency: {motor_eff:.2f}")

        #P_motor = T_motor / motor_eff   # watts
        P_motor = motor["power"] * throttle
        #print(f"Motor Power: {P_motor:.2f} W")
        P_total = 4 * P_motor + P_payload 
        #print(f"Estimated Power Use: {P_total:.2f} W")

        # Step 3: Required energy
        E_required = P_total  * t_flight #* throttle # Wh

        # Step 4: Find best battery from database
        best_battery = None
        min_mass = float('inf')

        P_required = P_total #* throttle   # or any specific power required for the system
        for b in battery_db:
            usable_energy = (b['voltage'] * b['capacity'] / 1000) * discharge_eff  # Wh
            if b['C-rating'] is None:
                continue
            max_discharge_power = b['capacity'] * b['C-rating'] * b['voltage'] / 1000  # in watts
            print(f"Battery {b['id']} - Usable Energy: {usable_energy:.2f} Wh - Maximum discharge power: {max_discharge_power:.2f}W - Num needed: {math.ceil(E_required / usable_energy)} - Mass: {math.ceil(E_required / usable_energy)*b['mass']} g")

            # Check if the battery can supply the required power (C-rating check)

    
            """if usable_energy >= E_required and max_discharge_power >= P_required:
            #if b["voltage"] >= motor["voltage"] and b["capacity"] >= motor["capacity"]:
                if b['mass'] < min_mass:
                    best_battery = b
                    min_mass = b['mass']
                    n_batt = 1"""
            if usable_energy > 0 and max_discharge_power > 0:
                n_needed_energy = math.ceil(E_required / usable_energy)
                n_needed_power = math.ceil(P_required / max_discharge_power)
                n_batt_temp = max(n_needed_energy, n_needed_power)
                total_mass = n_batt_temp * b['mass']

                if usable_energy * n_batt_temp >= E_required and max_discharge_power * n_batt_temp >= P_required:
                    if total_mass < min_mass:
                        best_battery = b
                        min_mass = total_mass
                        n_batt = n_batt_temp

        if not best_battery:
            try:
                # Step 1: Get top 3 batteries with highest discharge power
                top_batteries = sorted(
                    [b for b in battery_db if b.get('C-rating') is not None],
                    key=lambda b: b['capacity'] * b['C-rating'] * b['voltage'] / 1000,
                    reverse=True
                )[:3]

                best_combination = None
                min_total_mass = float('inf')

                for b in top_batteries:
                    usable_energy = (b['voltage'] * b['capacity'] / 1000) * discharge_eff  # Wh
                    max_discharge_power = b['capacity'] * b['C-rating'] * b['voltage'] / 1000  # W
                    n_needed_energy = math.ceil(E_required / usable_energy)
                    n_needed_power = math.ceil(P_required / max_discharge_power)
                    n_batt = max(n_needed_energy, n_needed_power)
                    total_mass = n_batt * b['mass']

                    if total_mass < min_total_mass:
                        best_combination = b
                        best_battery = b
                        #n_batteries = n_batt
                        n_batt = n_batt
                        min_total_mass = total_mass

                if best_battery is not None:
                    print(f"Using {n_batt}x {best_battery['id']} in parallel.")
                    print(f"Total mass of batteries: {n_batt * best_battery['mass']} g")
                else:
                    raise RuntimeError("No suitable battery combination found.")

            except Exception as e:
                raise RuntimeError("Battery selection failed with error: " + str(e))

        print(f"Selected Battery: {best_battery['id']} | {best_battery['capacity']} mAh | {best_battery['cells']}S | {best_battery['mass']} g")
        motor_guess = result["motor"]
        d_p = motor_guess['prop_diameter']  # cm
        gtow, T_max, T_motor, m_m, m_e, m_b, m_p, m_f, m_a, m_pl = converge_gtow_tquad(m_pl, d_p=d_p, n_batteries=n_batt, battery_override=best_battery, motor_override=motor_guess)
        # Step 5: Convergence check
        if abs(result['GTOW'] - prev_gtow) < tol:
            print("\nSYSTEM CONVERGED at iteration", i+1)
            return {
                **result,
                "GTOW": gtow,
                "T_max": T_max,
                "T_motor": T_motor,
                "m_motor": m_m,
                "m_ESC": m_e,
                "m_battery": m_b,
                "m_propeller": m_p,
                "m_frame": m_f,
                "m_avionics": m_a,
                "m_payload": m_pl,
                'P_total': P_total,
                'E_required': E_required,
                'battery': best_battery,
                "m_battery": best_battery['mass'] * n_batt,
                "usable_energy": (best_battery['voltage'] * best_battery['capacity'] / 1000) * discharge_eff * n_batt,
                "power_discharge": best_battery['capacity'] * best_battery['C-rating'] * best_battery['voltage'] / 1000 * n_batt,
            }

        if result['GTOW'] > max_gtow:
            #print(f"GTOW exceeds the cap of {max_gtow} g. Stopping the iteration.")
            raise RuntimeError("GTOW exceeded the maximum limit.")
        
        battery_guess = best_battery
        prev_gtow = result['GTOW']

    raise RuntimeError("System did not converge after all iterations.")

if __name__ == "__main__":
    base_m_pl = m_payload(198, 19, 230, 0, 150)  # g
    base_P_payload = 65  # watts
    t_flight = 0.25  # hours

    # Margins: -20%, baseline, +20%
    #margin_factors = [0.8, 1.0, 1.2]
    margin_factors = [1.0]

    for margin in margin_factors:
        adjusted_m_pl = base_m_pl * margin
        adjusted_P_payload = base_P_payload * margin
        print(f"\n==== Running Analysis for m_pl {int(margin*100)}%, P_payload {int(margin*100)}% ====")
        try:
            results = full_system_loop(adjusted_m_pl, adjusted_P_payload, t_flight=t_flight)
            performance = analyze_performance(results, n_rotors=4, tilt_angle=30)
            print_final_summary(results, performance)
        except RuntimeError as e:
            print(f"Failed to converge: {e}")


    payloads = np.linspace(0, 500, 100)  # g
    results_list = []
    performance_list = []
    for payload in payloads:
        try:
            results = full_system_loop(payload, base_P_payload, t_flight=t_flight)
            performance = analyze_performance(results, n_rotors=4, tilt_angle=30)
            print_final_summary(results, performance)
            results_list.append(results)
            performance_list.append(performance)
        except RuntimeError as e:
            print(f"Failed to converge for payload {payload} g: {e}")


    gtow = []
    duav = []

    for i, res in enumerate(results_list):
        try:
            d_p = res['motor']['prop_diameter'] / 100  # convert cm to meters
            k = 1.2  # margin factor for motor clearance
            arm_length = k * d_p / 2  # radius from center to one motor
            duav_val = arm_length * math.sqrt(2) * 2  # full diagonal
            #duav.append(duav_val)
            duav.append(performance_list[i]['duav'])
            gtow.append(res['GTOW'])
        except Exception as e:
            print(f"Error processing result: {e}")

    plt.figure(figsize=(8, 5))
    plt.plot(duav, gtow, 'o-', color='teal')
    plt.title('DUAV vs. GTOW')
    plt.xlabel('Motor-to-Motor Distance (DUAV) [m]')
    plt.ylabel('GTOW [g]')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
