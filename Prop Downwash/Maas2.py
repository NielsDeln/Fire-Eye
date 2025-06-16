import matplotlib.pyplot as plt
import numpy as np
import random

#variables----------------------------------
Dpreal = 0.127 *2 # Propeller diameter [m]
Ct = 0.04629 # Thrust coefficient
n = 14080/60 # Propeller speed [rpm]
Rp = Dpreal / 2 # Propeller radius [m]
Rh = 0.013 # Hub radius [m]
pitch = 0.1143 # Propeller pitch [m]
P = pitch / Dpreal # Pitch ratio
A = np.pi * Rp**2 # disk area [m^2]
rho = 1.225 # density [whatever the unit is]
g = 9.81 # gravitalional acceleration [m/s^2]
m = 2.268 # mass [kg]

T = Ct * rho * n**2 * Dpreal**4

W = T * 4

border1 = 1.7
border = 4.25

alt = 2 # max x value to be looked at, i.e. flying altitude ig [m]
res = 300 # resolution for plotting

#FUNCTIONS----------------------------------

VdT = ((W)/(2*rho*A))**0.5
VdM = ((m*g)/(2*rho*A))**0.5
print('Downwash velocity using the thrust:', VdT)
print('Downwash velocity using the weight:', VdM)

V_0 = 1.46*n*Dpreal * (Ct**0.5)
print('Downwash velocity using the semi-empirical methods:', V_0)
R0 = 0.74 * Rp
Rm0 = 0.67 * (R0 - Rh)
Dp = R0*2
x0 = 1.528 * Rp


def V_MAX(x, V_0 = V_0,  Dp = Dp, P = P):
    
    if x >= x0 and x < (x0 + (border1 * Dp)):
      
        V_MAX = V_0 * (1.24 - 0.0765 * ((x-x0)/Dp))
       
       
        return V_MAX
    
    
    elif x >= (x0 + (border1 * Dp)) and x < (x0 + (border * Dp)):
        V_MAX = V_0 * (1.37 - 0.1529*((x-x0)/Dp))
        
        return V_MAX
    
    elif x >= (x0 + (border * Dp)):
        V_MAX = V_0 * (0.89 - 0.04*((x-x0)/Dp))
        
        return V_MAX

    
x_val = np.linspace(0, alt, res)
V_list = []

for i in range(len(x_val)):
    V_val = V_MAX(x_val[i])
    V_list.append(V_val)

plt.plot(x_val, V_list)
plt.show


def V_i(r, V_MAX, x, Rm0 = Rm0, R0 = R0, Dp = Dp, x0 = x0): 

    if x >= x0 and x < (x0 + (border1 * Dp)):
        Rmax = Rm0 * (1-0.01294*((x-x0)/Dp))
        #V_i = V_MAX * np.exp(-(((r-Rmax))/(0.8839*Rm0+0.1326*(x-x0-R0)))**2)
        V_i = V_MAX * np.e ** (-((r - Rmax)/(0.8839 * Rm0 + 0.1326*(x-x0-R0)))**2)
        #print(np.exp(-(((r-Rmax))/(0.8839*Rm0+0.1326*(x-R0)))**2))

        return V_i
    
    
    elif x >= (x0 + (border1* Dp)) and x < (x0 + (border * Dp)):
        Rmax = Rm0 * (1.3 - 0.3059*((x-x0)/Dp)) 
        #V_i = V_MAX * np.exp(-((r-Rmax)/(0.5176*Rm0+0.2295*(x-x0-R0)))**2)
        V_i = V_MAX * np.e ** (-((r - Rmax)/(0.5176 * Rm0 + 0.2295*(x-x0-R0)))**2)
        return V_i
     
    elif x >= (x0 + (border * Dp)):
        
        V_i = V_MAX * np.e ** (-(r/(0.2411*(x-x0)))**2)
        return V_i
    
def plot_downwash(orientation = 'horizontal', to_scale = False):
    x_vals = np.linspace(x0, alt, res)
    r_grid = []
    v_i_grid = []

    for i in range(len(x_vals)):
        x = x_vals[i]
        r_row = np.linspace(0, 1.2*Dpreal, res // 2)

        v_i_row = []
        for r in r_row:
            v_max = V_MAX(x)
            v_i_val = V_i(r, v_max, x)
            # v_i_val = random.random()
            v_i_row.append(v_i_val)
            v_i_row_full = list(reversed(v_i_row)) + v_i_row

        v_i_grid.append(v_i_row_full)
        r_grid.append(np.concatenate([-r_row[::-1], r_row]))


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
        #plt.vlines(x_0(V_0(), a(K_T()), V_x), 0, np.max(r_grid), color='white', linestyle='--', label='Efflux Position $x_0$')
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
        #plt.hlines(x_0(V_0(), a(K_T()), V_x), r_grid[0, 0], r_grid[0, -1], color='white', linestyle='--', label='Efflux Position $x_0$')
        plt.hlines(10*Dp, r_grid[0, 0], r_grid[0, -1], color='gray', linestyle='--', label='10x Propeller Diameter')
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

plot_downwash(orientation='vertical', to_scale=False)
