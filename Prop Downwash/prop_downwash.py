import matplotlib.pyplot as plt
import numpy as np
import random
#dfsd
############# VARIABLES #############

rho = 1.225 # air density at room temp 

D_p = 0.127 # Propeller diameter [m]
C_T = 0.0652601 # Thrust coefficient
n = 27600 / 60 # Propeller speed [rps]
R_p = D_p / 2 # Propeller radius [m]
R_h = 0.013 # Hub radius [m]

alt = 1.5 # max x value to be looked at, i.e. flying altitude ig [m]
res = 300 # resolution for plotting

K = 10 # RANDOM VALUE!!!
K_visc = K * (1 / 15.68) # Viscosity coefficient [m^2/s] AT ROOM TEMPERATURE!!!!

V_x = 4 # RANDOM VALUE!!! # velocity at which propeller moving forward (technically 0 cause we hoverin)

T = C_T * (rho * n**2 * D_p**4)


############# INITIAL CALCULATIONS #############


# Efflex velocity [m/s] - absolute max value reached at efflex
def V_0(D_p = D_p, C_T = C_T, n = n): 
    # print(f'V_0: {1.33 * n * D_p * np.sqrt(C_T)}')
    return 1.33 * n * D_p * np.sqrt(C_T)


# Some coefficient ( = inf for V_x = 0)
def K_T(V_x = V_x, T=T, rho=1.225, R_p = R_p):
    return (T / (4 * rho * R_p**2 * V_x**2)) if V_x != 0 else np.inf

# Some coefficient 
def a(K_T):
    return (-1 + np.sqrt(1 + 8 * (K_T/np.pi)))/2 if K_T != np.inf else np.inf

# Efflux position [m]
def x_0(V_0, a, V_x, R_p = R_p): # efflux position [m]
    return ((V_0 - a * V_x) * R_p) / (np.sqrt(V_0*(2*a*V_x - V_0)))

# Average velocity at given x position [m/s]
def v_i_avg(x, a, V_x = 0, R_p = R_p):
    return a * V_x * (1 + x / np.sqrt((R_p**2 + x**2)))

# Radius at given x position [m]
def R_s(x, a, R_p = R_p):
    # print('""""')
    # print(a)
    # print(np.sqrt((R_p**2 + x**2)))
    # print(0.5 * a * x / np.sqrt((R_p**2 + x**2)))
    # print('""""')
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
    # print(f'x0: {x_0}')

    if x >= 0 and x <= (x_0 + 0.5*D_0): # ZFE
        return V_max * np.e ** (-0.5 * ((r - R_m_0) / (0.5 * R_m_0))**2)

    elif x > (x_0 + 0.5*D_0 and x <= (x_0 + 3.25 * D_0)): # ZFE
        return V_max * np.e ** (-0.5 * ((r - R_m_0) / (0.5 * R_m_0 + (0.075 * (x - x_0 - R_0))/K_visc))**2)

    elif x > (x_0 + 3.25 * D_0): # ZEF
        return V_max * np.e ** (-22.2 * (r / (K_visc * (x-x_0)))**2)
    
    else:
        print('poop happened (sqrt for x_0 is negative) ')
        return 0
    


def plot_downwash(orientation = 'vertical', to_scale = False):
    x_vals = np.linspace(int(np.round(x_0(V_0(), a(K_T()), V_x))), alt, res)
    r_grid = []
    v_i_grid = []

    for i in range(len(x_vals)):
        x = x_vals[i]
        r_row = np.linspace(-D_p, 1.2*D_p, res)
        v_i_row = []
        for r in r_row:
            v_max = V_max(V_0(), x, x_0(V_0(), a(K_T()), V_x))
            v_i_val = v_i(v_max, r, x, x_0(V_0(), a(K_T()), V_x), R_m_0())
            # v_i_val = random.random()
            v_i_row.append(v_i_val)
        r_grid.append(r_row)
        v_i_grid.append(v_i_row)

    r_grid = np.array(r_grid)  # shape: (len(x_vals), 100)
    # r_grid = r_grid / R_p

    v_i_grid = np.array(v_i_grid)  # shape: (len(x_vals), 100)



    if to_scale:
        width = r_grid[0, -1] - r_grid[0, 0]
        height = x_vals[-1] - x_vals[0]
        factor = 10

        plt.figure(figsize=(width*factor, height*factor))
    else:
        plt.figure(figsize=(5, 8))


    if orientation == 'horizontal':
        plt.imshow(
            v_i_grid.T, 
            extent=[x_vals[0], x_vals[-1], 0, np.max(r_grid)], 
            aspect='auto', 
            origin='lower', 
            cmap='jet'
        )
        plt.vlines(x_0(V_0(), a(K_T()), V_x), 0, np.max(r_grid), color='white', linestyle='--', label='Efflux Position $x_0$')
        plt.colorbar(label='Induced Velocity $v_i$ [m/s]')
        plt.xlabel('Axial Position $x$ [m]')
        plt.ylabel('Radial Position $r$ [m]')

    elif orientation == 'vertical':
        plt.imshow(
            v_i_grid,
            extent=[r_grid[0, 0], r_grid[0, -1], x_vals[0], x_vals[-1]],
            aspect='auto',
            origin='lower',
            cmap='jet'
        )
        plt.gca().invert_yaxis()  # Flip y-axis: highest x at top, lowest at bottom
        plt.hlines(x_0(V_0(), a(K_T()), V_x), r_grid[0, 0], r_grid[0, -1], color='white', linestyle='--', label='Efflux Position $x_0$')
        plt.colorbar(label='Induced Velocity $v_i$ [m/s]')
        plt.xlabel('Radial Position $r$ [m]')
        plt.ylabel('Axial Position $x$ [m]')

    else:
        print("wrong orientation")


    plt.title('Induced Velocity Heatmap ($v_i$) along Propeller Axis')
    plt.tight_layout()
    plt.show()

plot_downwash(orientation='vertical', to_scale=False)





