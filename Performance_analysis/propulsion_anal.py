import os
import sys
import math
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import numpy as np
import matplotlib.pyplot as plt
#from Trade_off.Tilted_Quadcopter_Modular.modular_tquad import *


# Constants
g = 9.81                 # Acceleration due to gravity (m/s^2)
rho = 1.225              # Air density (kg/m^3)
mu = 1.8247e-5           # Dynamic viscosity (Pa.s)
vf = 2                   # Freestream velocity (m/s)
alpha_deg = 5           # Angle of attack in degrees
alpha = math.radians(alpha_deg)  # Convert to radians
n_blades = 2              # Number of blades per rotor
n_rotors = 4              # Total number of rotors
blade_pitch = math.radians(16)          # Blade pitch angle in degrees


# Inputs
R = 12.7/2 / 100              # Propeller radius [m]
D = R * 2                 # Propeller diameter [m]
R0 = 0.0013                # Root radius [m], hub clearance 1.3cm
b = 0.035                   # Chord length [m] Chord = Often constant, ≈ 3–4 cm
m_uav = 1.641                # UAV takeoff weight [kg]
V_up = 2                    # Takeoff velocity [m/s]
V_forward = 7.2 / 3.6     # Cruise speed (m/s)
L = 0.015                   # Distance from shaft to torque arm [m] small torque arm, consistent with the motor geometry.
RPM = 27600               # RPM for 2207 2300KV @ 14.8
Omega = RPM * 2 * np.pi / 60  # Angular velocity [rad/s]


# Blade element parameters
n_elements = 100
r = np.linspace(R0, R, n_elements)
dr = (R - R0) / n_elements
W = np.sqrt((Omega * r)**2 + V_up**2)  # Relative velocity at each blade element



# calculate the Reynolds number
def Re(vf , rho , b, mu):
    """  
    b_tip = b - b_root  
    l = b_root + 0.75 * (b_tip - b_root) # chord at 75% R
    print(f"l: {l:.2f} m")
    Re = rho * vf * l / mu
    return Re"""
    b_root = 0.01
    b_tip = 0.0075
    l = b_root + 0.75 * (b_tip - b_root) # chord at 75% R 
    r_75 = 0.75 * R
    V_local = Omega * r_75  # m/s
    return rho * V_local * l / mu


Re = Re(vf, rho, R, mu)  # Reynolds number at the tip of the blade
print(f"Reynolds number: {Re:.2f}")

# Retrieve Cl and Cd from airfoil data (based on Re)  manually look them up from airfoiltools.com
# max cl/cd 36.7 at α=5°
Cd = 0.01674              # Drag coefficient at alpha=5°, Re~500k
Cl = 0.6141               # Lift coefficient at alpha=5°, Re~500k


# Aerodynamic forces
S = b * dr                   # local surface area
dY = 0.5 * Cl * rho * W**2 * S
dX = 0.5 * Cd * rho * W**2 * S

# Thrust and Torque per blade

epsilon = blade_pitch - alpha

dT = np.cos(epsilon) * dY - np.sin(epsilon) * dX
dQ = np.sin(epsilon) * dY - np.cos(epsilon) * dX
T_single = np.sum(dT)
Q_single = np.sum(dQ)

# tot system thrust and torque
T_total = T_single * n_rotors
Q_total = Q_single * n_rotors


# Induced velocity
def calc_Vi(T_single, R, R0, g=9.81, a=0.99): #a: loss of T correction factor
    return np.sqrt((T_single / 1000 * g) / (2 * rho * np.pi * ((R)**2- (R0)**2) * a)) # m/s

Vi = calc_Vi(T_single, R, R0)

# Power computations
Pi = T_total * Vi                      # induced rotation resistance power
P0 = n_blades * Q_total * L * Omega   # airfoil resistance power
#P_p = Q_air * V_forward                # waste resistance power
Pm = m_uav * g * V_up                  # amount of power UAVs uses to overcome gravityduring vertical takeoﬀ
# Total power
P_total = Pi + P0 + Pm

# PERFORMANCE METRICS
# propulsive efficiency
eta = Pi / Pi + P0
# thrust coefficient
n_rev = RPM / 60
CT = T_total / (rho * n_rev**2 * D**4)
# advance ratio
J = V_forward / (n_rev * D)



print("======== PROPELLER PERFORMANCE RESULTS ========")
print(f"Thrust per rotor         : {T_single:.2f} N, {T_single *1000 / 9.81:.2f} g")
print(f"Total Thrust             : {T_total:.2f} N")
print(f"Torque per rotor         : {Q_single:.4f} Nm")
print(f"Total Torque             : {Q_total:.4f} Nm")
print(f"Induced Velocity (Vi)    : {Vi:.2f} m/s")
print(f"Induced Power (Pi)       : {Pi:.2f} W")
print(f"Profile Power (P0)       : {P0:.2f} W")
print(f"Gravity Power (Pm)       : {Pm:.2f} W")
print(f"Total Power Required     : {P_total:.2f} W")
print(f"Propeller Efficiency η   : {eta:.4f}")
print(f"Thrust Coefficient CT    : {CT:.5f}")
print(f"Advance Ratio J          : {J:.3f}")




def downwash_V2(T, D, z=0): # one rotor thrust (kg * m / s^2), one rotor diameter (m), air density (kg/m^3), distance (vertically downwards) from rotor (m)
    
    A = math.pi/4 * D**2 # single rotor area
    
    vi = math.sqrt(2*T / (rho * A))

    vz = (10/z) * vi * math.sqrt(A / (2*math.pi))

    return vz, vi

def outwash_V(downwash_V2):
    return (7.2 / 2) * downwash_V2


def z_req(downwash_V2, D, max_v = 1.5): # max velocity at ground (default 1.5 m/s), one rotor diameter (m)
    reduction_factor = max_v / downwash_V2 
    
    z_req = (10/(2*math.sqrt(2))) * D * (1/reduction_factor)

    return z_req


vz, vi = downwash_V2(T_single, D, 3.5355*D)

print("======== DOWNWASH CHARACHTERISTICS ========")
print(f"Max downwash velocity per rotor        : {vi:.2f} m/s")
print(f"Max outwash velocity per rotor         : {outwash_V(vi):.2f} m/s")
print(f"Alt. to fly at to get wind velocity of 1.5 m/s on ground: {z_req(v2, D):.2f} m")



