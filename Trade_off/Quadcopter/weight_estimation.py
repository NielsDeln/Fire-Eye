import numpy as np
import matplotlib.pyplot as plt

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

m_pl = m_payload(198, 0, 230, 0, 150) # m_dmcomm, m_navig, m_mapping, m_control, m_forensics

def converge_gtow(
    m_pl,
    I_max=22,
    d_p=10.16,       # cm
    battery_cells=4,
    battery_capacity=5000,  # mAh
    t_frame=4,
    l_frame=300,
    tol=1e-2,
    max_iter=100,
    battery_override=None,
    motor_override=None,
):
    # Initial guess for m_0 (MTOW)
    m0_guess = m_pl / 0.4 

    for i in range(max_iter):
        # Step 1: required thrust
        T_total = 2 * m0_guess
        T_motor = T_total / 4

        # Step 2: all component Masses
        if motor_override:
            m_m = motor_override['mass'] * 4
            I_max = motor_override['peak_current']
        else:
            m_m = m_motor(T_motor) * 4
        m_e = m_ESC(I_max) * 4
        if battery_override:
            m_b = battery_override['mass']
            battery_cells = battery_override['cells']
            battery_capacity = battery_override['capacity']
        else:
            m_b = m_battery(battery_cells, battery_capacity)
        m_p = m_propeller(d_p) * 4
        m_f = m_frame(t_frame, l_frame)
        m_a = m_avionics(m0_guess)
        # Step 3: new GTOW
        m_total = GTOW(m_m, m_e, m_b, m_p, m_f, m_a, m_pl)

        # Step 4: convergence?
        if abs(m_total - m0_guess) < tol:
            print(f"\n GTOW converged after {i+1} iterations.")
            print(f"GTOW (m_0): {m_total:.2f} g")
            print(f"Motor Mass 4: {m_m:.2f} g")
            print(f"ESC Mass: {m_e:.2f} g")
            print(f"Propeller Mass 4: {m_p:.2f} g")
            print(f"Frame Mass: {m_f:.2f} g")
            print(f"Avionics Mass: {m_a:.2f} g")
            print(f"Battery Mass: {m_b:.2f} g")
            print(f"Required Total Thrust (T_max): {T_total:.2f} g")
            print(f"Required Per-Motor Thrust: {T_motor:.2f} g")
            return m_total, T_total, T_motor

        m0_guess = m_total

    raise RuntimeError("GTOW did not converge")


if __name__ == "__main__":
    converge_gtow(
        m_pl,
        I_max=22,
        d_p=10,       # cm
        battery_cells=4,
        battery_capacity=4276,  # mAh
        t_frame=4,
        l_frame=300,
    )


