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
Cd = 0.01674              # Drag coefficient at alpha=5°, Re~100k
Cl = 0.6141               # Lift coefficient at alpha=5°, Re~100k


# Aerodynamic forces
S = b * dr                   # local surface area
dY = 0.5 * Cl * rho * W**2 * S
dX = 0.5 * Cd * rho * W**2 * S

# Thrust and Torque per blade
epsilon = blade_pitch - alpha

#NONTILTED
dT = np.cos(epsilon) * dY - np.sin(epsilon) * dX
dQ = np.sin(epsilon) * dY - np.cos(epsilon) * dX
T_single = np.sum(dT)
Q_single = np.sum(dQ)
# tot system thrust and torque
T_total = T_single * n_rotors
Q_total = Q_single * n_rotors

#TILTED
tilt_angle_deg = 30
tilt_angle = math.radians(tilt_angle_deg)

T_vertical_single = T_single * math.cos(tilt_angle)
T_horizontal_single = T_single * math.sin(tilt_angle)
T_vertical_total =  T_vertical_single * n_rotors
T_horizontal_total = T_horizontal_single * n_rotors
T_net_tilted = np.sqrt(T_vertical_total**2 + T_horizontal_total**2)

# Induced velocity
def calc_Vi(T_single, R, R0, g=9.81, a=0.99): #a: loss of T correction factor
    return np.sqrt((T_single / 1000 * g) / (2 * rho * np.pi * ((R)**2- (R0)**2) * a)) # m/s

Vi = calc_Vi(T_single, R, R0)
Vi_tilted = calc_Vi(T_vertical_single, R, R0)


# Power computations
Pi = T_total * Vi                      # induced rotation resistance power
Pi_tilted = T_vertical_total * Vi_tilted
P0 = n_blades * Q_total * L * Omega   # airfoil resistance power
#P_p = Q_air * V_forward                # waste resistance power
Pm = m_uav * g * V_up                  # amount of power UAVs uses to overcome gravityduring vertical takeoﬀ
# Total power
P_total = Pi + P0 + Pm


# PERFORMANCE METRICS
# propulsive efficiency
eta_cruise = Pi / (Pi + P0 + Pm) 
eta_cruise_tilted = Pi_tilted / (Pi_tilted + P0 + Pm)

# thrust coefficient
n_rev = RPM / 60
CT = T_total / (rho * n_rev**2 * D**4)
CT_tilted = T_vertical_total / (rho * n_rev**2 * D**4)

# advance ratio
J = V_forward / (n_rev * D)
J_tilted = (V_forward * math.cos(tilt_angle)) / (n_rev * D)



print("======== PROPELLER PERFORMANCE RESULTS ========")
print(f"{'Parameter':<30} {'Non-Tilted':>15} {'Tilted (' + str(tilt_angle_deg) + '°)':>15}")
print("-" * 60)
print(f"{'Thrust per rotor [N]':<30} {T_single:>15.2f} {T_vertical_single:>15.2f}")
print(f"{'Thrust per rotor provided (vert) [g]':<15} {T_single *1000 / 9.81:>13.2f} {T_vertical_single *1000 / 9.81:>13.2f}")
print(f"{'Total Thrust (net) [N]':<30} {T_total:>15.2f} {T_net_tilted:>15.2f}")
print(f"{'Total Thrust [g]':<30} {T_total*1000 / 9.81:>15.2f} {T_net_tilted*1000 / 9.81:>15.2f}")

print(f"{'Vertical Thrust Total[N]':<30} {'—':>15} {T_vertical_total:>15.2f}")
print(f"{'Horizontal Thrust Total [N]':<30} {'—':>15} {T_horizontal_total:>15.2f}")
print("-" * 60)

print(f"{'Torque per rotor [Nm]':<30} {Q_single:>20.2f} ")
print(f"{'Total Torque (net) [Nm]':<30} {Q_total:>20.2f} ")
print("-" * 60)

print(f"{'Induced Velocity Vi [m/s]':<30} {Vi:>15.2f} {Vi_tilted:>15.2f}")
print(f"{'Induced Power Pi [W]':<30} {Pi:>15.2f} {Pi_tilted:>15.2f}")
print(f"{'Profile Power P0 [W]':<30} {P0:>20.2f} ")
print(f"{'Gravity Power Pm [W]':<30} {Pm:>20.2f} ")
print(f"{'Total Power [W]':<30} {P_total:>15.2f} {(Pi_tilted + P0 + Pm):>15.2f}")
print(f"{'Efficiency η':<30} {eta_cruise:>15.4f} {eta_cruise_tilted:>15.4f}")
print(f"{'Thrust Coefficient CT':<30} {CT:>15.5f} {CT_tilted:>15.5f}")
print(f"{'Advance Ratio J':<30} {J:>15.3f} {J_tilted:>15.3f}")
print("=" * 60)


#DOWNWASH CALCULATIONS
def downwash_V2(T_single, D, z=0, tilt_angle=0): # one rotor thrust (kg * m / s^2), one rotor diameter (m), air density (kg/m^3), distance (vertically downwards) from rotor (m)
    A = math.pi/4 * D**2 # single rotor area
    T_vert = T_single * math.cos(tilt_angle)
    vi = math.sqrt(2 * T_vert / (rho * A))  # vertical induced velocity
    vz = (10 / z) * vi * math.sqrt(A / (2 * math.pi))   # projected downwash
    return vz, vi


def outwash_V(downwash_V2):
    return (7.2 / 2) * downwash_V2 


def z_req(downwash_V2, D, max_v = 1.5): # max velocity at ground (default 1.5 m/s), one rotor diameter (m)
    reduction_factor = max_v / downwash_V2 
    z_req = (10/(2*math.sqrt(2))) * D * (1/reduction_factor)
    return z_req


vz, vi = downwash_V2(T_single, D, z=3.5355*D)
vz_tilted, vi_tilted = downwash_V2(T_single, D, z=3.5355*D, tilt_angle=tilt_angle)

outwash = outwash_V(vz)
outwash_tilted = outwash_V(vz_tilted)

z_rq = z_req(vz, D)
z_tilted = z_req(vz_tilted, D)

print("\n======== DOWNWASH PERFORMANCE RESULTS ========")
print(f"{'Parameter':<45} {'Non-Tilted':>15} {'Tilted (' + str(tilt_angle_deg) + '°)':>15}")
print("-" * 75)
print(f"{'Induced Velocity (vi) why diff other[m/s]':<45} {vi:>15.2f} {vi_tilted:>15.2f}")
print(f"{'Projected Downwash Velocity (vz) [m/s]':<45} {vz:>15.2f} {vz_tilted:>15.2f}")
print(f"{'Outwash Velocity [m/s]':<45} {outwash:>15.2f} {outwash_tilted:>15.2f}")
print(f"{'Required Altitude for 1.5 m/s Ground Wind [m]':<45} {z_rq:>15.2f} {z_tilted:>15.2f}")
print("=" * 75)



# Plotting the effect of tilt angle on poop
tilt_angles = np.linspace(0, 45, 100)
T_vert_tot_list, vi_list, vz_list, outwash_list, zreq_list = [], [], [], [], []

for tilt in tilt_angles:
    T_vertical_total = T_single * math.cos(math.radians(tilt)) * n_rotors   
    vi,  vz = downwash_V2(T_single, D, z=3.5355*D, tilt_angle=math.radians(tilt))
    out = outwash_V(vi)
    zreq = z_req(vi, D)

    T_vert_tot_list.append(T_vertical_total)
    vi_list.append(vi)
    vz_list.append(vz if vz else 0)
    outwash_list.append(out)
    zreq_list.append(zreq)

plt.figure(figsize=(12, 6))

plt.subplot(2, 2, 1)
plt.plot(tilt_angles, vz_list, label="Downwash (vz)", color='purple')
plt.xlabel("Tilt Angle (deg)")
plt.ylabel("Downwash velocity at z = 3.5355D (m/s)")
plt.grid(True)

plt.subplot(2, 2, 2)
plt.plot(tilt_angles, outwash_list, label="Outwash Velocity", color='magenta')
plt.xlabel("Tilt Angle (deg)")
plt.ylabel("Outwash velocity (m/s)")
plt.grid(True)

plt.subplot(2, 2, 3)
plt.plot(tilt_angles, zreq_list, label="Required Altitude", color='orange')
plt.xlabel("Tilt Angle (deg)")
plt.ylabel("z for max ground wind = 1.5 m/s (m)")
plt.grid(True)

plt.subplot(2, 2, 4)
plt.plot(tilt_angles, T_vert_tot_list, label="Total Vertical Thrust", color='pink')
plt.xlabel("Tilt Angle (deg)")
plt.ylabel("Total Vertical Thrust (N)")
plt.grid(True)

plt.tight_layout()
plt.suptitle("Effect of Tilt Angle on Rotor Flow Characteristics", fontsize=14, y=1.05)
plt.show()

