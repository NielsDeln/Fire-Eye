import os
import sys
import math
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import numpy as np
import matplotlib.pyplot as plt
from Trade_off.Tilted_Quadcopter_Modular.modular_tquad import *


# Constants
g = 9.81                 # Acceleration due to gravity (m/s^2)
rho = 1.225              # Air density (kg/m^3)
mu = 1.8247e-5           # Dynamic viscosity (Pa.s)
vf = 2                   # Freestream velocity (m/s)
alpha_deg = 5            # Angle of attack in degrees
alpha = math.radians(alpha_deg)  # Convert to radians
n_blades = 2              # Number of blades per rotor
n_rotors = 4              # Total number of rotors


# Inputs
R = 12.7/2 / 100              # Propeller radius [m]
R0 = 0.05                  # Root radius [m]
b = 0.04                   # Chord length [m]
m_uav = 1.641                # UAV takeoff weight [kg]
V_up = 2                    # Takeoff velocity [m/s]
V_forward = 7.2 / 3.6     # Cruise speed (m/s)
L = 0.15                   # Distance from shaft to torque arm [m]  distancebetween the point of action of the rotation resistance and thepropeller shaft
RPM = 27600 
Omega = RPM * 2 * np.pi / 60  # Angular velocity [rad/s]


# Blade element parameters
n_elements = 100
r = np.linspace(R0, R, n_elements)
dr = (R - R0) / n_elements
W = np.sqrt((Omega * r)**2 + V_up**2)  # Relative velocity at each blade element



# calculate the Reynolds number
def Re(V_f=2, rho=1.225, R=6.35, mu=1.8247e-5 , g=9.81):
    l = R * 0.01  # chord at 75% R
    Re = rho * V_f * l / mu
    return Re

# Retrieve Cl and Cd from airfoil data (based on Re)  manually look them up from airfoiltools.com
Cd = 0.01674              # Drag coefficient at alpha=5°, Re~100k
Cl = 0.6141               # Lift coefficient at alpha=5°, Re~100k



# Aerodynamic forces
S = b * dr                   # local surface area
dY = 0.5 * Cl * rho * W**2 * S
dX = 0.5 * Cd * rho * W**2 * S

# Thrust and Torque per blade
dT = np.cos(alpha) * dY - np.sin(alpha) * dX
dQ = np.sin(alpha) * dY - np.cos(alpha) * dX
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
Pi = T_total * Vi                      # nduced rotation resistance power
P0 = n_blades * Q_total * L * Omega   # airfoil resistance power
#P_p = Q_air * V_forward                 # waste resistance power
Pm = m_uav * g * V_up                  # amount of power UAVs uses to overcome gravityduring vertical takeoﬀ


# Total power
P_total = Pi + P0 + Pm

# PERFORMANCE METRICS
# propulsive efficiency
eta = Pi / P_total
# thrust coefficient
n_rev = RPM / 60
D = R * 2
CT = T_total / (rho * n_rev**2 * D**4)
# advance ratio
J = V_forward / (n_rev * D)



print("=== PROPELLER PERFORMANCE RESULTS ===")
print(f"Thrust per rotor         : {T_single:.2f} N")
print(f"Total Thrust             : {T_total:.2f} N")
print(f"Total Torque             : {Q_total:.4f} Nm")
print(f"Induced Velocity (Vi)    : {Vi:.2f} m/s")
print(f"Induced Power (Pi)       : {Pi:.2f} W")
print(f"Profile Power (P0)       : {P0:.2f} W")
print(f"Gravity Power (Pm)       : {Pm:.2f} W")
print(f"Total Power Required     : {P_total:.2f} W")
print(f"Propeller Efficiency η   : {eta:.4f}")
print(f"Thrust Coefficient CT    : {CT:.5f}")
print(f"Advance Ratio J          : {J:.3f}")




def downwash_V2(T, A, rho=1.225, z=0):

    return 






