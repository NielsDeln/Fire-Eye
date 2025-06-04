import matplotlib.pyplot as plt
import numpy as np
import random

############# VARIABLES #############

rho = 1.225 # air density at room temp 

D_p = 0.127 # Propeller diameter [m]
C_T = 0.0652601 # Thrust coefficient
n = 27600 / 60 # Propeller speed [rps]
R_p = D_p / 2 # Propeller radius [m]
R_h = 0.013 # Hub radius [m]

K = 1 # RANDOM VALUE!!!
K_visc = K * (1 / 15.68) # Viscosity coefficient [m^2/s] AT ROOM TEMPERATURE!!!!

V_x = 0.3 # RANDOM VALUE!!! # velocity at which propeller moving forward (technically 0 cause we hoverin)

T = C_T * (rho * n**2 * D_p**4)


############# INITIAL CALCULATIONS #############


# Efflex velocity [m/s] - absolute max value reached at efflex
def V_0(D_p = D_p, C_T = C_T, n = n): 
    print(f'V_0: {1.33 * n * D_p * np.sqrt(C_T)}')
    return 1.33 * n * D_p * np.sqrt(C_T)


# Some coefficient ( = inf for V_x = 0)
def K_T(V_x = V_x, T=T, rho=1.225, R_p = R_p):
    return (T / (4 * rho * R_p**2 * V_x**2)) if V_x != 0 else np.inf

# Some coefficient 
def a(K_T):
    return (-1 + np.sqrt(1 + 8 * (K_T/np.pi)))/2 if K_T != np.inf else np.inf

# Efflux position [m]
def x_0(V_0, a, V_x, R_p = R_p): # efflux position [m]
    print(f'square root for x_0: {V_0*(2*a*V_x - V_0)}')
    return ((V_0 - a * V_x) * R_p) / (np.sqrt(V_0*(2*a*V_x - V_0)))

# Average velocity at given x position [m/s]
def v_i_avg(x, a, V_x = 0, R_p = R_p):
    return a * V_x * (1 + x / np.sqrt((R_p**2 + x**2)))

# Radius at given x position [m]
def R_s(x, a, R_p = R_p):
    print('""""')
    print(a)
    print(np.sqrt((R_p**2 + x**2)))
    print(0.5 * a * x / np.sqrt((R_p**2 + x**2)))
    print('""""')
    return R_p * (1 - 0.5 * a * x / np.sqrt((R_p**2 + x**2)))


R_0 = R_s(0, a(K_T())) # Radius at efflux [m]

# Radius at which V_0 occurs at x_0 [m]
def R_m_0(R_0 = R_0, R_h = R_h): 
    return 0.7 * (R_0 - R_h)

############# VELOCITY CALCULATIONS #############


# Maximum velocity in the zone of flow establishment (POST efflix)
# starts at efflix (x_0) and ends at x_0 + 3.25 * D_0
def V_ZFE_max(V_0, x, x_0, R_0 = R_0):
    D_0 = 2 * R_0 # Diameter at efflux [m]

    if x >= x_0 and x <= (x_0 + 3.25 * D_0):
        return V_0 * (1.0172 - K_visc * 0.1835 * (x - x_0) / D_0)
    else:
        return 0
    
# Maximum velocity  in zone of established flow (also POST efflix, but comes AFTER ZFE)
# Starts at x_0 + 3.25 * D_0 (and goes to infignity technically)
def V_ZEF_max(V_0, x, x_0, R_0 = R_0):
    D_0 = 2 * R_0 # Diameter at efflux [m]

    if x > (x_0 + 3.25 * D_0):
        return V_0 * (0.543 - K_visc * 0.0281 * (x - x_0) / D_0)
    else:
        return 0
    
# Alternatively can use this one combined function instead of the two before this
def V_max(V_0, x, x_0, R_0 = R_0):
    D_0 = 2 * R_0 # Diameter at efflux [m]
    
    if x >= x_0 and x <= (x_0 + 3.25 * D_0):
        return V_0 * (1.0172 - K_visc * 0.1835 * (x - x_0) / D_0)
    elif x > (x_0 + 3.25 * D_0):
        return V_0 * (0.543 - K_visc * 0.0281 * (x - x_0) / D_0)
    else:
        return 0
    

# Induced velocity at given axial (x) position and radial (r) position
def v_i(V_max, r, x, x_0, R_m_0, R_0 = R_0):
    D_0 = 2 * R_0
    print(f'x0: {x_0}')

    if x >= x_0 and x <= (x_0 + 0.5*D_0):
        print(R_m_0)
        return V_max * np.e ** (-0.5 * ((r - R_m_0) / (0.5 * R_m_0))**2)

    elif x > (x_0 + 0.5*D_0) and x <= (x_0 + 3.25 * D_0):
        return V_max * np.e ** (-0.5 * ((r - R_m_0) / (0.5 * R_m_0 + (0.075 * (x - x_0 - R_0))/K_visc))**2)

    elif x > (x_0 + 3.25 * D_0):
        return V_max * np.e ** (-22.2 * (r / (K_visc * (x-x_0)))**2)
    
    else:
        print('poop happened (sqrt for x_0 is negative)')
        return 0
    


x_vals = np.linspace(0, 3, 100)
r_vals = []

# for x in x_vals:
#     r = R_s(x, a(K_T()))
#     print(r)
#     r_vals.append(r)



# plt.plot(x_vals, r_vals, label='R_s(x) - Radial Position at x')
# plt.show()

# for i in range(len(x_vals)):
#     x = x_vals[i]
#     r = r_vals[i]

#     v_max = V_max(V_0(), x, x_0(V_0(), a(K_T()), V_x))

#     print(v_max)


#     v_i_vals.append(v_i(v_max, r, x, x_0(V_0(), a(K_T()), V_x), R_m_0()))


# x_vals = np.array(x_vals)
# r_vals = np.array(r_vals)
# v_i_vals = np.array(v_i_vals)

# plt.figure(figsize=(8, 5))
# sc = plt.scatter(x_vals, r_vals, c=v_i_vals, cmap='viridis', s=20)
# plt.colorbar(sc, label='Induced Velocity $v_i$ [m/s]')
# plt.xlabel('Axial Position $x$ [m]')
# plt.ylabel('Radial Position $r$ [m]')
# plt.title('Induced Velocity ($v_i$) along Propeller Axis')
# plt.grid(True)
# plt.tight_layout()
# plt.show()

x_vals = np.linspace(0, 5, 100)
r_grid = []
v_i_grid = []

for i in range(len(x_vals)):
    x = x_vals[i]
    r_row = np.linspace(0, D_p, 100)
    v_i_row = []
    for r in r_row:
        v_max = V_max(V_0(), x, x_0(V_0(), a(K_T()), V_x))
        v_i_val = v_i(v_max, r, x, x_0(V_0(), a(K_T()), V_x), R_m_0())
        # v_i_val = random.random()
        v_i_row.append(v_i_val)
    r_grid.append(r_row)
    v_i_grid.append(v_i_row)

r_grid = np.array(r_grid)  # shape: (len(x_vals), 100)
r_grid = r_grid / R_p
print(r_grid)
v_i_grid = np.array(v_i_grid)  # shape: (len(x_vals), 100)

plt.figure(figsize=(8, 5))

plt.imshow(
    v_i_grid.T, 
    extent=[x_vals[0], x_vals[-1], 0, np.max(r_grid)], 
    aspect='auto', 
    origin='lower', 
    cmap='viridis'
)
plt.colorbar(label='Induced Velocity $v_i$ [m/s]')
plt.xlabel('Axial Position $x$ [m]')
plt.ylabel('Radial Position $r$ [m]')
plt.title('Induced Velocity Heatmap ($v_i$) along Propeller Axis')
plt.tight_layout()
plt.show()


'''

Input slipstream velocity profiles:
      r (m)     Vaxi (m/s)  Vrot (m/s)
      0.15568     5.86057     8.16064
      0.16802     5.90079     7.61286
      0.19034     6.03435     6.87227
      0.21950     6.25457     6.17689
      0.25290     6.51663     5.58578
      0.28876     6.77792     5.08812
      0.32595     7.01059     4.66235
      0.36371     7.19955     4.29100
      0.40151     7.33786     3.96168
      0.43898     7.42315     3.66561
      0.47584     7.45524     3.39628
      0.51186     7.43514     3.14881
      0.54684     7.36418     2.91925
      0.58062     7.24393     2.70448
      0.61307     7.07598     2.50198
      0.64405     6.86201     2.30963
      0.67344     6.60380     2.12567
      0.70116     6.30329     1.94877
      0.72709     5.96261     1.77768
      0.75116     5.58414     1.61150
      0.77328     5.17052     1.44944
      0.79339     4.72468     1.29089
      0.81143     4.24985     1.13535
      0.82733     3.74960     0.98244
      0.84105     3.22800     0.83201
      0.85255     2.68986     0.68392
      0.86179     2.14159     0.53870
      0.86874     1.59404     0.39774
      0.87339     1.07791     0.26752
      0.87572     0.70689     0.17500

Current value <ret takes default>: 0.876300
Enter scale factor for radii)   r>

Current value <ret takes default>:  49.1700
Enter axial velocity scale factor   r>

Current value <ret takes default>:  49.1700
Enter tang. velocity scale factor   r>

 Imposed slipstream velocity profiles:
      r (m)     Vaxi (m/s)  Vrot (m/s)
      0.13642   288.16425   401.25882
      0.14724   290.14197   374.32434
      0.16680   296.70914   337.90948
      0.19235   307.53723   303.71786
      0.22161   320.42255   274.65295
      0.25304   333.27045   250.18266
      0.28563   344.71066   229.24760
      0.31872   354.00204   210.98830
      0.35184   360.80264   194.79602
      0.38468   364.99612   180.23792
      0.41698   366.57437   166.99519
      0.44854   365.58582   154.82693
      0.47919   362.09671   143.53943
      0.50880   356.18378   132.97939
      0.53723   347.92596   123.02227
      0.56438   337.40512   113.56433
      0.59014   324.70886   104.51913
      0.61442   309.93286    95.82092
      0.63715   293.18143    87.40862
      0.65824   274.57224    79.23726
      0.67763   254.23433    71.26881
      0.69525   232.31244    63.47327
      0.71105   208.96504    55.82531
      0.72499   184.36798    48.30646
      0.73701   158.72066    40.90981
      0.74709   132.26057    33.62846
      0.75518   105.30191    26.48774
      0.76128    78.37897    19.55684
      0.76535    53.00084    13.15395
      0.76739    34.75766     8.60483


'''
















