import numpy as np
import matplotlib.pyplot as plt

"""from mission profile requirements"""
def m_payload(m_dmcomm, m_navig, m_mapping, m_control, m_forensics): #g
    return  m_dmcomm + m_navig + m_mapping + m_control + m_forensics # g

def m_avionics(m_0): #g
    return 0.05*m_0 # g

"""semi empirical equations for estimating the weight of a quadcopter"""
def m_motor(T_max): # Maximum Thrust of Motor [gr]
    return (1e-07 * T_max**3 - 0.0003 * T_max**2 + 0.2783 * T_max - 56.133) / 4 # g # kept from quadcopter, for first iteration

def m_ESC(I_max, battery_cells): #  Maximum Continuous Current of ESC [A]
    return (102.71*I_max+3510*battery_cells+2.2781*I_max**2+73.77*battery_cells**2+32.86*I_max*battery_cells)*10**(-6) *1000  #g

def m_battery(n_s, C): # n cells, C capacity [mAh]
    #return 2.107*10**(-7)*C*n_s #g
    return 569
    
def m_propeller(d_p): # Diameter of the Propeller [cm]
    if d_p == 5.0:
        return 0.5
    elif d_p == 7.62:
        return 0.8
    elif d_p == 10:
        return 1
    else:
        return 0.04 * d_p - 0.2  #AAAA
    
    #return  0.1367* d_p_in**2 - 9.317* d_p_in + 0.881 # g negative values

def m_frame(D_UAV): # Thickness of the frame [mm], Diagonal Size of the Frame [mm]
    return 2.255 * D_UAV**2.084 * 1000 # g
    
def GTOW(m_m, m_e, m_b, m_p, m_f, m_a, m_pl): # Total Weight of the Quadcopter [g]
    return m_m + m_e + m_b + m_p + m_f + m_a + m_pl # g


"""Weight convergence loop"""
"""
Estimate GTOW m0

Compute required total thrust 
Tmax = 2 m0

Recalculate component masses (especially motors, avionics, frame).

Iterate until GTOW converges."""

m_pl = m_payload(150, 186, 230, 0, 3) # m_dmcomm, m_navig, m_mapping, m_control, m_forensics

def converge_gtow(
    m_pl,
    D_UAV=0.35,  # m
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
        print("T_total: ", T_total) 
        T_motor = T_total / 8

        # Step 2: all component Masses
        if motor_override:
            m_m = motor_override['mass'] * 8
            I_max = motor_override['peak_current']
        else:
            m_m = m_motor(T_motor) * 8
        print(f"Motor Mass 8: {m_m:.2f} g")
        m_e = m_ESC(I_max, battery_cells) * 8
        print(f"ESC Mass: {m_e:.2f} g")
        if battery_override:
            m_b = battery_override['mass']
            battery_cells = battery_override['cells']
            battery_capacity = battery_override['capacity']
        else:
            m_b = m_battery(battery_cells, battery_capacity)
        print(f"Battery Mass: {m_b:.2f} g")
        m_p = m_propeller(d_p) * 8
        print(f"Propeller Mass 8: {m_p:.2f} g")
        m_f = m_frame(D_UAV)
        print(f"Frame Mass: {m_f:.2f} g")
        m_a = m_avionics(m0_guess)
        print(f"Avionics Mass: {m_a:.2f} g")
        # Step 3: new GTOW
        m_total = GTOW(m_m, m_e, m_b, m_p, m_f, m_a, m_pl)
        print(f"GTOW (m_0): {m_total:.2f} g")

        # Step 4: convergence?
        if abs(m_total - m0_guess) < tol:
            print(f"\n GTOW converged after {i+1} iterations.")
            print(f"GTOW (m_0): {m_total:.2f} g")
            print(f"Required Total Thrust (T_max): {T_total:.2f} g")
            print(f"Required Per-Motor Thrust: {T_motor:.2f} g")
            return m_total, T_total, T_motor

        m0_guess = m_total

    raise RuntimeError("GTOW did not converge")


if __name__ == "__main__":
    converge_gtow(
        m_pl,
        D_UAV=0.35,  # m
        I_max=22,
        d_p=10,       # cm
        battery_cells=4,
        battery_capacity=5200,  # mAh
        t_frame=4,
        l_frame=300,
    )

