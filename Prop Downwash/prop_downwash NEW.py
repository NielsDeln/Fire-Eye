import matplotlib.pyplot as plt
import numpy as np
import random
import bisect
#dfsd
############# VARIABLES #############

rho = 1.225 # air density at room temp 
n = 21119 / 60 # Propeller speed [rps]

D_p = 0.127 * 2# Propeller diameter [m]
C_T = 0.012423 # Thrust coefficient
print('C_T:', C_T)
R_p = D_p / 2 # Propeller radius [m]
R_h = 0.002 # Hub radius [m]
# pitch = 0.1143 # Propeller pitch [m]
D_arm = 0.47
R_arm = D_arm / 2 # Arm radius [m]

alt = 1.5 # max x value to be looked at, i.e. flying altitude ig [m]
res = 300 # resolution for plotting

K = 10 # RANDOM VALUE!!!
K_visc = K * (1 / 15.68) # Viscosity coefficient [m^2/s] AT ROOM TEMPERATURE!!!!

V_x = 0.1 # RANDOM VALUE!!! # velocity at which propeller moving forward (technically 0 cause we hoverin)

# P = pitch / D_p # Pitch ratio

# T = C_T * (rho * n**2 * D_p**4)

max_width = 0.61
half_width = max_width / 2

V_0 = 1.46 * n * D_p * (C_T**0.5)
print(f'V0: {V_0}')
x_0 = 1.528 * R_p
R_0 = 0.74 * R_p
D_0 = 2 * R_0
R_max_0 = 0.67 * (R_0 - R_h)


def V_max(x):
    if x >= x_0 and x < (x_0 + 1.7 * D_0):
        return V_0 * (1.24 - 0.0765 * ((x - x_0) / D_0))
    elif x >= (x_0 + 1.7 * D_0) and x < (x_0 + 4.25 * D_0):
        return V_0 * (1.37 - 0.1529 * (x - x_0) / D_0)
    elif x >= (x_0 + 4.25 * D_0):
        return V_0 * (0.89 - 0.04 * (x - x_0) / D_0)
    else:
        return None
    
# texting max velocity distributions
D_0 = 2 * R_0
x_vals = np.linspace(x_0, x_0 + 5 * D_0, 300)

# Calculate V_max for each x
V_max_vals = [V_max(x) for x in x_vals]

plt.figure(figsize=(8, 4))
plt.plot(x_vals, V_max_vals, label='$V_{max}(x)$')
plt.xlabel('Axial Position $x$ [m]')
plt.ylabel('Maximum Velocity $V_{max}$ [m/s]')
plt.title('Maximum Velocity $V_{max}$ vs Axial Position $x$')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
    
def R_max(x):
    if x >= x_0 and x < (x_0 + 1.7 * D_0):
        return R_max_0 * (1 - 0.1294 * (x - x_0) / D_0)
    elif x >= (x_0 + 1.7 * D_0) and x < (x_0 + 4.25 * D_0):
        return R_max_0 * (1.3 - 0.3059 * (x - x_0) / D_0)
    elif x >= (x_0 + 4.25 * D_0):
        return 0
    else:
        return None
    
def v_i(x, r):
    if x >= x_0 and x < (x_0 + 1.7 * D_0):
        return V_max(x) * np.e ** (-((r - R_max(x))/(0.8839 * R_max_0 + 0.1326*(x-x_0-R_0)))**2)
    elif x >= (x_0 + 1.7 * D_0) and x < (x_0 + 4.25 * D_0):
        return V_max(x) * np.e ** (-((r - R_max(x))/(0.5176 * R_max_0 + 0.2295*(x-x_0-R_0)))**2)
    elif x >= (x_0 + 4.25 * D_0):
        return V_max(x) * np.e ** (-((r / (0.2411 * (x - x_0)))**2))
    else:
        return None
          




def plot_downwash(orientation = 'vertical'):
    x_vals = np.linspace(x_0, alt, res)
    r_grid = []
    v_i_grid = []

    for i in range(len(x_vals)):
        x = x_vals[i]
        r_row = np.linspace(0, 1.2*D_p, res)

        v_i_row = []
        for r in r_row:
            v_i_val = v_i(x, r)
            # v_i_val = random.random()
            v_i_row.append(v_i_val)

        v_i_grid.append(v_i_row)
        r_grid.append(r_row)


    r_grid = np.array(r_grid)  # shape: (len(x_vals), 100)
    # r_grid = r_grid / R_p

    v_i_grid = np.array(v_i_grid)  # shape: (len(x_vals), 100)


    if orientation == 'horizontal':
        plt.figure(figsize=(12, 5))
        plt.imshow(
            v_i_grid.T, 
            extent=[x_vals[0], x_vals[-1], 0, np.max(r_grid)], 
            aspect='auto', 
            origin='lower', 
            cmap='jet'
        )
        # plt.vlines(x_0(V_0(), a(K_T()), V_x), 0, np.max(r_grid), color='white', linestyle='--', label='Efflux Position $x_0$')
        plt.colorbar(label='Induced Velocity $v_i$ [m/s]')
        plt.xlabel('Axial Position $x$ [m]')
        plt.ylabel('Radial Position $r$ [m]')

    elif orientation == 'vertical':
        plt.figure(figsize=(5, 8))
        plt.imshow(
            v_i_grid,
            extent=[r_grid[0, 0], r_grid[0, -1], x_vals[0], x_vals[-1]],
            aspect='auto',
            origin='lower',
            cmap='jet'
        )
        plt.gca().invert_yaxis()  # Flip y-axis: highest x at top, lowest at bottom
        # plt.hlines(x_0(V_0(), a(K_T()), V_x), r_grid[0, 0], r_grid[0, -1], color='white', linestyle='--', label='Efflux Position $x_0$')
        # plt.hlines(10*D_p, r_grid[0, 0], r_grid[0, -1], color='gray', linestyle='--', label='10x Propeller Diameter')
        # plt.vlines(R_h, x_vals[0], x_vals[-1], color='black', linestyle='--', label='Hub Radius $R_h$')
        plt.colorbar(label='Induced Velocity $v_i$ [m/s]')
        plt.xlabel('Radial Position $r$ [m]')
        plt.ylabel('Axial Position $x$ [m]')

    else:
        print("wrong orientation")


    plt.title('Induced Velocity Heatmap ($v_i$) along Propeller Axis')
    # plt.vlines(R_h, x_vals[0], x_vals[-1], color='black', linestyle='-', label='Hub Radius $R_h$')
    # plt.vlines(-R_h, x_vals[0], x_vals[-1], color='black', linestyle='-', label='Hub Radius $R_h$')

    # plt.legend()
    plt.tight_layout()
    plt.show()

plot_downwash(orientation='horizontal')

def plot_ground_velocity():
    x = alt
    width_factor = 3
    r = np.linspace(0, width_factor * D_p, res // 2)

    v_max = V_max(x)
    v_i_vals = [v_i(x, r_val) for r_val in r]
    v_i_vals_full = list(reversed(v_i_vals)) + v_i_vals
    r_full = np.concatenate([-r[::-1], r])

    plt.figure(figsize=(14, 4))

    plt.plot(r_full, v_i_vals_full, label='Propeller 1', linestyle='-', color='pink')
    plt.xlabel('Radial Position $r$ [m]')
    plt.ylabel('Induced Velocity $v_i$ [m/s]')
    plt.title('Induced Velocity at Ground Level (flying @ ' + str(round(x, 2)) + ' m altitude)')


    for i in range(len(v_i_vals_full)):
        val = v_i_vals_full[i]
        if val > 1.5:
            roi = abs(r_full[i])
            break
        else:
            continue

    max_v = round(np.max(v_i_vals_full), 3)

    plt.text(roi * 0.9, max_v - 0.1*max_v, 'Max velocity: ' + str(round(np.max(v_i_vals_full),3)) + ' m/s', fontsize = 10)
    plt.text(roi * 0.9, max_v - 0.2*max_v, 'Radius of influence: ' + str(round(abs(roi),3)) + 'm', fontsize = 10)
    plt.text(roi * 0.9 , max_v - 0.3*max_v, 'Area of influence: ' + str(round(roi**2 * np.pi,3)) + 'm$^2$', fontsize = 10)
    plt.text(roi * 0.9 , max_v - 0.4*max_v, 'Radius of influence (4 propellers): ' + str(round((abs(roi) + R_arm), 3)) + 'm', fontsize = 10)
    plt.text(roi * 0.9, max_v - 0.5*max_v, 'Area of influence (4 propellers): ' + str(round((abs(roi) + R_arm)**2 * np.pi, 3)) + 'm$^2$', fontsize = 10)


    plt.axhline(y=1.5, color='black', linestyle='--', linewidth=0.5)

    plt.show()

    centers = [
        (-half_width + R_p,  half_width - R_p),  # Top-left
        ( half_width - R_p,  half_width - R_p),  # Top-right
        (-half_width + R_p, -half_width + R_p),  # Bottom-left
        ( half_width - R_p, -half_width + R_p)   # Bottom-right
    ]

    fig, ax = plt.subplots()

    # Draw the propeller circles
    for center in centers:
        prop_circle = plt.Circle(center, R_p, fill=False, edgecolor='blue', linewidth=2)
        ax.add_patch(prop_circle)

    # Draw the ROI circles in light blue with 50% opacity
    for center in centers:
        roi_circle = plt.Circle(center, roi, color='lightblue', alpha=0.5)
        ax.add_patch(roi_circle)

    # Formatting the plot
    ax.set_xlim(-half_width - roi, half_width + roi)
    ax.set_ylim(-half_width - roi, half_width + roi)
    ax.set_aspect('equal', 'box')
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.set_title('Propellers with ROI Circles')
    plt.grid(True)
    plt.show()


plot_ground_velocity()



