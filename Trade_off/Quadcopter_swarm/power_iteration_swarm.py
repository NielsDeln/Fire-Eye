import os
import sys
import math
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Trade_off.Quadcopter_swarm.propulsion_iteration_swarm import converge_gtow_and_prop
from Trade_off.Quadcopter_swarm.weight_estimation_swarm import  m_payload
from Trade_off.Quadcopter.weight_estimation import converge_gtow as converge_gtow_quadcopter
from Trade_off.datasets import *
from Trade_off.Quadcopter.power_iteration import analyze_performance, print_final_summary


P_payloads = [12, 0, 4] # in watts


def full_system_loop(payloads, P_payloads, t_flight, tol=1e-2, max_outer=10):
    all_results = []
    discharge_eff = 0.9
    throttle = 0.38


    for idx_p, power in enumerate(P_payloads):
        prev_gtow = 0
        battery_guess = battery_db[0]
        n_batt = 1
        #print(f"\n--- Drone {idx_p+1} ---")
        for i in range(max_outer):
            #print(f"\n========================")
            #print(f"   Outer Loop {i+1} - Weight + Power")
            #print(f"========================")

            # Step 1: GTOW + motor/prop optimization with current battery guess
            result = converge_gtow_and_prop(
                payloads,
                battery_capacity=battery_guess['capacity'],
                n_cells=battery_guess['cells'], 
                battery_override=battery_guess,
            )[idx_p]

            # Step 2: total power consumption
            motor = result['motor']
            T_motor = motor["thrust"]  
            #print(f"Motor Thrust: {T_motor:.2f} g")
            motor_eff = motor['efficiency'] 
            #print(f"Motor Efficiency: {motor_eff:.2f}")

            P_motor = motor["power"]   # watts
            #print(f"Motor Power: {P_motor:.2f} W")
            P_total = 4 * P_motor + power
            #print(f"Estimated Power Use: {P_total:.2f} W")

            # Step 3: Required energy
            E_required = P_total * throttle * t_flight  # Wh

            # Step 4: Find best battery from database
            best_battery = None
            min_mass = float('inf')

            P_required = P_total * throttle  # or any specific power required for the system
            for b in battery_db:
                usable_energy = (b['voltage'] * b['capacity'] / 1000) * discharge_eff  # Wh
                print(f"Battery {b['id']} - Usable Energy: {usable_energy:.2f} Wh - Num needed: {math.ceil(E_required / usable_energy)} - Mass: {math.ceil(E_required / usable_energy)*b['mass']} g")
                # Check if the battery can supply the required power (C-rating check)
                if b['C-rating'] is None:
                    continue
                max_discharge_power = b['capacity'] * b['C-rating'] * b['voltage'] / 1000  # in watts
                if usable_energy >= E_required and  max_discharge_power >= P_required:
                    if b['mass'] < min_mass:
                        best_battery = b
                        min_mass = b['mass']
                        n_batt = 1

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
                            n_batteries = n_batt
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
            m_pl = payloads[idx_p]
            gtow, T_max, T_motor, m_m, m_e, m_b, m_p, m_f, m_a, m_pl = converge_gtow_quadcopter(m_pl, d_p=d_p, n_batteries=n_batt, battery_override=best_battery, motor_override=motor_guess)
            # Step 5: Convergence check
            if abs(result['GTOW'] - prev_gtow) < tol:
                #print("\nSYSTEM CONVERGED")
                result.update({
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
            })
                all_results.append(result)
                break  # exit outer loop for this drone

            battery_guess = best_battery
            prev_gtow = result['GTOW']
        else:
            raise RuntimeError("System did not converge after all iterations.")
    return all_results

if __name__ == "__main__":
    # m_payloads (m_dmcomm, m_navig, m_mapping, m_control, m_forensics)
    #####SWARM 1#####
    payloads1 = [
    198,  # Drone 1
    273.593,  # Drone 2
    193.583,  # Drone 3
    ]
    P_payloads1 = [10, 21, 51] # in watts

    #####SWARM 2#####
    payloads2 = [
    428,  # Drone 1
    348,  # Drone 2
    ]
    P_payloads2 = [20, 50] # in watts


    # no margins too much
    results = full_system_loop(payloads1, P_payloads1, t_flight=0.25) # hours
    
    for i, res in enumerate(results):
        print(f"\n====== Final Results for Drone {i+1} ======")
        print_final_summary(res, analyze_performance(res))
