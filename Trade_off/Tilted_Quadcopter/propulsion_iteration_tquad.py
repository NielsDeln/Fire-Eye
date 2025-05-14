import numpy as np
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from Trade_off.Tilted_Quadcopter.weight_estimation_tquad import converge_gtow_tquad, m_payload
from Trade_off.Quadcopter.propulsion_iteration import evaluate_motor_prop_combo, select_best_motor_and_prop, converge_gtow_and_prop
from Trade_off.datasets import *


prop_diameters = np.array([7.62, 10.16, 11.9, 15.4]) # cm 
#prop_pitches = [4.5, 5.0, 5.5]  # example values


"""Send prop diameter back to GTOW loop"""
# Outer convergence loop: GTOW ↔ Prop ↔ GTOW
def converge_gtow_and_prop_tquad(m_pl, battery_capacity=None, n_cells=None, tol=1e-2, max_iter=10, battery_override=None):
    d_p = 10  # initial guess for prop diameter [cm]
    prev_gtow = 0
    motor_guess = None

    for i in range(max_iter):
        #print(f"\n Outer Iteration {i+1}")
        
        # 1. GTOW estimation (with current propeller diameter)
        gtow, T_max, T_motor = converge_gtow_tquad(m_pl, d_p=d_p, battery_cells=n_cells if n_cells is not None else 4, battery_capacity=battery_capacity if battery_capacity is not None else 5000, battery_override=battery_override if battery_override is not None else None, motor_override=motor_guess if battery_override is not None else None)


        #print(f"GTOW Estimate: {gtow:.2f} g")
        #print(f"T_max: {T_max:.2f} g | Required per motor: {T_motor:.2f} g")

        # 2. Motor + Propeller Optimization
        best_config = select_best_motor_and_prop(gtow, T_motor)
        new_d_p = best_config['prop_diameter']
        #print(f"Selected Motor: {best_config['motor']['id']} | Prop: {new_d_p} cm")

        # 3. Convergence check
        if abs(gtow - prev_gtow) < tol and abs(new_d_p - d_p) < 0.5:
            #print("\n Converged!")
            break
        
        motor_guess = best_config["motor"]
        d_p = new_d_p
        prev_gtow = gtow
    else:
        raise RuntimeError(" Convergence not reached within iteration limit.")

    # Final output summary
    motor = best_config['motor']
    """print("\n Final Optimized Configuration:")
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
"""
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
    m_pl = m_payload(150, 186, 230, 0, 3) # m_dmcomm, m_navig, m_mapping, m_control, m_forensics
    result = converge_gtow_and_prop_tquad(m_pl, n_cells=4)