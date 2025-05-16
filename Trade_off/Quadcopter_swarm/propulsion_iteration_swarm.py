import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Trade_off.Quadcopter_swarm.weight_estimation_swarm import converge_gtow, m_payload
from Trade_off.Quadcopter.propulsion_iteration import evaluate_motor_prop_combo, select_best_motor_and_prop
from Trade_off.datasets import *
"""ITERATION"""

"""
Motor Selection:
Find real-world motors (from a database) that can supply 
Tmax/4.
Each motor has mass, size, performance data.

Propeller Optimization Loop (for each motor):
Iterate over a range of diameters and pitches.
Evaluate downwash, efficiency, or some optimization metric.
Pick the best propeller for the selected motor.
Propeller Size → Weight Loop:
The optimized propeller size goes back into the GTOW estimation loop as an updated input (because propeller size affects weight).

1. Use T_motor to filter motor database
2. For each valid motor:
   a. Loop over a range of propeller diameters/pitches
   b. Evaluate a placeholder for "optimization_metric"
   c. Save the best prop for that motor
3. Select the best motor+prop combo (lowest metric)
4. Send prop diameter back to GTOW loop"""

prop_diameters = np.array([7.62, 10.16, 11.9, 15.4]) # cm 
#prop_pitches = [4.5, 5.0, 5.5]  # example values

# Outer convergence loop: GTOW ↔ Prop ↔ GTOW
def converge_gtow_and_prop(payloads, battery_capacity=None, n_cells=None, tol=1e-2, max_iter=10, battery_override=None, n_batteries=None):  
    results = []
    for idx, payload in enumerate(payloads):
        #print(f"\n--- Drone {idx+1} ---")
        
        d_p = 10  # initial guess for prop diameter [cm]
        prev_gtow = 0
        motor_guess = None
        
        for i in range(max_iter):
            #print(f"\nOuter Iteration {i+1}")
            
            # 1. GTOW estimation (with current propeller diameter)
            result = converge_gtow(payloads, d_p=d_p, battery_cells=n_cells if n_cells is not None else 4, 
                                    battery_capacity=battery_capacity if battery_capacity is not None else 5000, 
                                    battery_override=battery_override,
                                    n_batteries=n_batteries, 
                                    motor_override=motor_guess)
            gtow, T_max, T_motor, m_m, m_e, m_b, m_p, m_f, m_a, m_pl = result[idx]
            #print(f"GTOW: {gtow} | T_max: {T_max} | T_motor: {T_motor}")
            # 2. Motor + Propeller Optimization
            best_config = select_best_motor_and_prop(gtow, T_motor)
            new_d_p = best_config['prop_diameter']
            #print(f"Selected Motor: {best_config['motor']['id']} | Prop: {new_d_p} cm")

            # 3. Convergence check
            if abs(gtow - prev_gtow) < tol:
                #print("\nConverged!")
                break

            motor_guess = best_config["motor"]
            d_p = new_d_p
            prev_gtow = gtow
        else:
            print(f"Iteration {i+1} did not converge. Retrying...")
        # Final output summary
        motor = best_config['motor']
        """
        print(f"\n Final Optimized Configuration drone {idx +1}:")
        print("---------------------------------")
        print(f"Total GTOW          : {gtow:.2f} g")
        print(f"Required T_max      : {T_max:.2f} g")
        print(f"Selected Motor      : {motor['id']}")
        print(f" - Mass             : {motor['mass']} g")
        print(f" - Max Thrust       : {motor['thrust']} g")
        print(f" - Efficiency       : {motor['efficiency']}")
        print(f" - Diameter         : {motor['diameter']} mm")
        print(f"Selected Propeller  : {best_config['prop_diameter']} cm")
        print(f"Optimization Metric : {best_config['metric']:.3f}")
        print("---------------------------------\n")"""

        results.append({
    'GTOW': gtow,
    'T_max': T_max,
    'T_motor': T_motor,
    'motor': motor,
    'propeller': {
        'diameter': best_config['prop_diameter']
    },
    'm_motor': m_m,
    'm_ESC': m_e,
    'm_battery': m_b,
    'm_propeller': m_p,
    'm_frame': m_f,
    'm_avionics': m_a,
    'm_payload': m_pl
    })
    
    return results



if __name__ == "__main__":
    # m_payloads (m_dmcomm, m_navig, m_mapping, m_control, m_forensics)
    #####SWARM 1#####
    payloads = [
    198,  # Drone 1
    273.593,  # Drone 2
    193.583,  # Drone 3
    ]
    P_payloads = [10, 21, 51] # in watts

    #####SWARM 2#####
    payloads2 = [
    428,  # Drone 1
    348,  # Drone 2
    ]
    P_payloads = [20, 50] # in watts
    results = converge_gtow_and_prop(payloads, n_cells=4)
    for idx, res in enumerate(results):
        print(f"\n=== Final Summary for Drone {idx + 1} ===")
        print(f"GTOW (Total Weight)    : {res['GTOW']:.2f} g")
        print(f"Total Required Thrust  : {res['T_max']:.2f} g")
        print(f"Per Motor Thrust       : {res['T_motor']:.2f} g")
        
        motor = res['motor']
        print(f"Selected Motor         : {motor['id']}")
        print(f" - Mass                : {motor['mass']} g")
        print(f" - Max Thrust          : {motor['thrust']} g")
        print(f" - Efficiency          : {motor['efficiency']}")
        print(f" - Diameter            : {motor['diameter']} mm")
        
        print(f"Selected Propeller     : {res['propeller']['diameter']} cm")
        print("=" * 40)