import numpy as np
import matplotlib.pyplot as plt
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Trade_off.Quadcopter.propulsion_iteration import *
from Trade_off.Quadcopter.power_iteration import *

"""from mission profile requirements"""
def m_payload(m_dmcomm, m_navig, m_mapping, m_control, m_forensics): #g
    return  m_dmcomm + m_navig + m_mapping + m_control + m_forensics # g

def m_avionics(m_0): #g
    return 0.12*m_0 # g

"""semi empirical equations for estimating the weight of a quadcopter"""
def m_motor(T_max): # Maximum Thrust of Motor [gr]
    return 1e-07 * T_max**3 - 0.0003 * T_max**2 + 0.2783 * T_max - 56.133 # g

def m_ESC(I_max): #  Maximum Continuous Current of ESC [A]
    return 0.9546* I_max - 2.592 # g

def m_battery(n, C): # n cells, C capacity [mAh]
    if n == 3:
        return  0.0625* C + 35.526 # g
    elif n == 4:
        return  0.0761*C + 69.522 # g
    elif n == 6:
        return 0.1169*C + 132.0 # g
    
def m_propeller(d_p): # Diameter of the Propeller [cm]
    if d_p == 7.62:
        return 0.4
    elif d_p == 10.16:
        return 0.5
    elif d_p == 11.9:
        return 0.6
    elif d_p == 15.4:
        return 0.9
    else:
        return 0.04 * d_p - 0.2 
    
    #return  0.1367* d_p_in**2 - 9.317* d_p_in + 0.881 # g negative values

def m_frame(t, l): # Thickness of the frame [mm], Diagonal Size of the Frame [mm]
    if t == 3:
        return 3e-6 * l**3 - 0.003 * l**2 + 1.3666 * l - 106.53 # g
    elif t == 4:
        return 4e-6 * l**3 - 0.004 * l**2 + 1.8221 * l - 142.04 # g
    
def GTOW(m_m, m_e, m_b, m_p, m_f, m_a, m_pl): # Total Weight of the Quadcopter [g]
    return m_m + m_e + m_b + m_p + m_f + m_a + m_pl # g


"""Weight convergence loop"""
"""
Estimate GTOW m0

Compute required total thrust 
Tmax = 2 m0

Recalculate component masses (especially motors, avionics, frame).

Iterate until GTOW converges."""




if __name__ == "__main__":

    """converge_gtow(
        m_pl,
        I_max=22,
        d_p=10,       # cm
        battery_cells=4,
        battery_capacity=4276,  # mAh
        t_frame=4,
        l_frame=300,
    )
    result = converge_gtow_and_prop(m_pl, n_cells=4)"""

    base_m_pl = m_payload(198, 19 , 230, 0, 0)  # g
    base_P_payload = 10+5+10  # watts
    t_flight = 0.25  # hours

    # Margins: -20%, baseline, +20%
    margin_factors = [0.8, 1.0, 1.2]

    for margin in margin_factors:
        adjusted_m_pl = base_m_pl * margin
        adjusted_P_payload = base_P_payload * margin
        print(f"\n==== Running Analysis for m_pl {int(margin*100)}%, P_payload {int(margin*100)}% ====")
        try:
            results = full_system_loop(adjusted_m_pl, adjusted_P_payload, t_flight=t_flight)
            performance = analyze_performance(results)
            print_final_summary(results, performance)
        except RuntimeError as e:
            print(f"Failed to converge: {e}")

