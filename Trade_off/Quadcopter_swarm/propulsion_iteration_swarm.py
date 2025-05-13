import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Trade_off.Quadcopter_swarm.weight_estimation_swarm import converge_gtow, m_payload, payloads
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


# optimization metric function
def evaluate_motor_prop_combo(motor, prop_diameter, mass_aircraft, prop_pitch=5.0, rho=1.225):
    """
    - motor: dict, containing 'efficiency', 'mass', etc.
    - prop_diameter: in cm
    - mass_aircraft: in grams
    - prop_pitch: optional, default = 5.0
    - rho: air density (kg/m^3)
    Returns:
    - V2: max induced velocity under the rotor, lower is better
    """
    M = mass_aircraft / 1000  # grams → kg
    d_m = prop_diameter / 100  # cm → meters
    A = np.pi * (d_m / 2)**2  # rotor disc area in m²
    
    # induced velocity V1 under rotor
    V1 = np.sqrt((M * 9.81) / (2 * rho * A))
    V2 = 2 * V1
    
    # penalty terms 
    thrust_efficiency = motor['efficiency'] - 0.01 * abs(prop_pitch - 5.0)
    mass_penalty = 0.001 * motor['mass']
    
    metric = V2 + mass_penalty - 0.2 * thrust_efficiency  
    return metric



# Main optimization thing
def select_best_motor_and_prop(T_motor):
    candidates = [m for m in motor_db if m['thrust'] >= T_motor and m['efficiency'] is not None]
    best_combo = None
    best_metric = float('inf')

    for motor in candidates:
        for d in prop_diameters:
            metric = evaluate_motor_prop_combo(motor, d, mass_aircraft=T_motor * 4)

            if metric < best_metric:
                best_metric = metric
                best_combo = {
                    'motor': motor,
                    'prop_diameter': d,
                    'metric': metric
                }

    if best_combo:
        #print("\nOptimal Motor-Propeller Pair Found:")
        #print(f"Motor ID: {best_combo['motor']['id']}")
        #print(f"Propeller: {best_combo['prop_diameter']}x{best_combo['prop_pitch']} cm")
        #print(f"Optimization Score: {best_combo['metric']:.3f}")
        return best_combo
    else:
        raise RuntimeError("No valid motor-propeller combo found.")


"""Send prop diameter back to GTOW loop"""
# Outer convergence loop: GTOW ↔ Prop ↔ GTOW
def converge_gtow_and_prop(payloads, battery_capacity=None, n_cells=None, tol=1e-2, max_iter=10, battery_override=None):
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
                                    battery_override=battery_override if battery_override is not None else None, 
                                    motor_override=motor_guess)
            gtow, T_max, T_motor = result[idx]
            #print(f"GTOW: {gtow} | T_max: {T_max} | T_motor: {T_motor}")
            # 2. Motor + Propeller Optimization
            best_config = select_best_motor_and_prop(T_motor)
            new_d_p = best_config['prop_diameter']
            #print(f"Selected Motor: {best_config['motor']['id']} | Prop: {new_d_p} cm")

            # 3. Convergence check
            if abs(gtow - prev_gtow) < tol and abs(new_d_p - d_p) < 0.5:
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
            'motor': motor_guess,
            'propeller': {
                'diameter': best_config['prop_diameter']
            }
        })
    
    return results



if __name__ == "__main__":
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