import numpy as np
import matplotlib.pyplot as plt
from weight_estimation import converge_gtow, m_payload, m_pl

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


# Dummy motor database TBD ACTUAL DTABASE
motor_db = [
    {'id': 'M1', 'thrust': 1800, 'mass': 75, 'KV': 900, 'diameter': 35, 'efficiency': 0.8},
    {'id': 'M2', 'thrust': 2000, 'mass': 90, 'KV': 850, 'diameter': 40, 'efficiency': 0.82},
    {'id': 'M3', 'thrust': 1900, 'mass': 80, 'KV': 920, 'diameter': 36, 'efficiency': 0.78},
    # Add more motors as needed
]
# PLACEHOLDERS TBD VALUES
prop_diameters = np.array([7.62, 10.16, 12.7, 15.4]) 
#prop_pitches = [4.5, 5.0, 5.5]  # example values


# optimization metric function
def evaluate_motor_prop_combo(motor, prop_diameter, prop_pitch = 5.0): # fill in prop pitch
    # Placeholder model
    downwash = prop_diameter * 0.1  # dummy relation
    thrust_efficiency = motor['efficiency'] - 0.01 * abs(prop_pitch - 5.0)
    mass_penalty = 0.001 * motor['mass']
    if thrust_efficiency <= 0:
        return float('inf')  # infeasible
    metric = (1 / thrust_efficiency) + downwash + mass_penalty
    return metric


# Main optimization thing
def select_best_motor_and_prop(T_motor):
    candidates = [m for m in motor_db if m['thrust'] >= T_motor]
    best_combo = None
    best_metric = float('inf')

    for motor in candidates:
        for d in prop_diameters:
            metric = evaluate_motor_prop_combo(motor, d)

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
def converge_gtow_and_prop(m_pl, battery_capacity=None, n_cells=None, tol=1e-2, max_iter=10):
    d_p = 10  # initial guess for prop diameter [cm]
    prev_gtow = 0

    for i in range(max_iter):
        print(f"\n Outer Iteration {i+1}")
        
        # 1. GTOW estimation (with current propeller diameter)
        gtow, T_max, T_motor = converge_gtow(m_pl, d_p=d_p, battery_cells=n_cells if n_cells is not None else 4, battery_capacity=n_cells if n_cells is not None else 5000)

        print(f"GTOW Estimate: {gtow:.2f} g")
        print(f"T_max: {T_max:.2f} g | Required per motor: {T_motor:.2f} g")

        # 2. Motor + Propeller Optimization
        best_config = select_best_motor_and_prop(T_motor)
        new_d_p = best_config['prop_diameter']
        print(f"Selected Motor: {best_config['motor']['id']} | Prop: {new_d_p} cm")

        # 3. Convergence check
        if abs(gtow - prev_gtow) < tol and abs(new_d_p - d_p) < 0.5:
            print("\n Converged!")
            break
        
        d_p = new_d_p
        prev_gtow = gtow
    else:
        raise RuntimeError(" Convergence not reached within iteration limit.")

    # Final output summary
    motor = best_config['motor']
    print("\n Final Optimized Configuration:")
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
    print("---------------------------------\n")

    return {
        'GTOW': gtow,
        'T_max': T_max,
        'T_motor': T_motor,
        'motor': motor,
        'propeller': {
            'diameter': best_config['prop_diameter']
        }
    }


if __name__ == "__main__":
    result = converge_gtow_and_prop(m_pl)