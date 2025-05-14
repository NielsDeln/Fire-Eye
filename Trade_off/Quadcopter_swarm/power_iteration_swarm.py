import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Trade_off.Quadcopter_swarm.propulsion_iteration_swarm import converge_gtow_and_prop
from Trade_off.Quadcopter_swarm.weight_estimation_swarm import  m_payload
from Trade_off.datasets import *
from Trade_off.Quadcopter.power_iteration import analyze_performance, print_final_summary


P_payloads = [12, 0, 4] # in watts


def full_system_loop(payloads, P_payloads, t_flight, tol=1e-2, max_outer=10):
    all_results = []
    discharge_eff = 0.9

    for idx_p, power in enumerate(P_payloads):
        prev_gtow = 0
        battery_guess = battery_db[0]
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
            E_required = P_total * t_flight  # Wh

            # Step 4: Find best battery from database
            best_battery = None
            min_mass = float('inf')

            P_required = P_total  # or any specific power required for the system
            for b in battery_db:
                usable_energy = (b['voltage'] * b['capacity'] / 1000) * discharge_eff  # Wh

                # Check if the battery can supply the required power (C-rating check)
                if b['C-rating'] is None:
                    continue
                max_discharge_power = b['capacity'] * b['C-rating'] * b['voltage'] / 1000  # in watts
                if usable_energy >= E_required and b['mass'] < min_mass or max_discharge_power >= P_required:
                    best_battery = b
                    min_mass = b['mass']

            if not best_battery:
                raise RuntimeError("No suitable battery found in the database.")
            #print(f"Selected Battery drone{idx_p+1}: {best_battery['id']} | {best_battery['capacity']} mAh | {best_battery['cells']}S | {best_battery['mass']} g")

            # Step 5: Convergence check
            if abs(result['GTOW'] - prev_gtow) < tol:
                #print("\nSYSTEM CONVERGED")
                result.update({
                    'P_total': P_total,
                    'E_required': E_required,
                    'battery': best_battery
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
    results = full_system_loop(payloads1, P_payloads1, t_flight=0.416) # hours
    
    for i, res in enumerate(results):
        print(f"\n====== Final Results for Drone {i+1} ======")
        print_final_summary(res, analyze_performance(res))
