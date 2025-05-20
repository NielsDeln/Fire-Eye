import numpy as np
import matplotlib.pyplot as plt
# -------------------------------------------------------------
#   Material property sheet  ―  Carbon-Fibre / PEEK laminate
#   (continuous UD fibres, ~55 % Vf, room-temperature data)
#   Units: SI  (kg, m, N, Pa, J, °C)
# -------------------------------------------------------------
CF_PEEK = {
    # PHYSICAL
    "rho"           : 1.550,           # density ρ  [kg/m³]

    # ELASTIC MODULI  (use the one that matches your lay-up)
    "E_long"        : 150 * 10**9,           # UD 0° modulus  [Pa]
    "E_quasi_iso"   : 75 *10**9,            # quasi-isotropic laminate  [Pa]
    "G_in_plane"    : 5.0 *10**9,           # shear modulus  ±45° laminate [Pa]
    "nu"            : 0.3,             # Poisson’s ratio  (average)

    # STRENGTH ALLOWABLES (already knocked-down, A-basis) – apply project SF!
    "sigma_t_allow" : 2.5 *10** 8,           # tensile allow (0°)  [Pa]
    "sigma_c_allow" : 2.0 *10** 8,           # compressive allow (0°) [Pa]
    "tau_allow"     : 9.0 *10** 7,           # in-plane shear allow  [Pa]

    # THERMAL
    "Tg"            : 143,             # glass-transition temperature  [°C]
    "Tservice_max"  : 250,             # recommended continuous service [°C]
    "alpha_long"    : 0.5 *10** -6,          # CTE along fibre  [1/K]

    # TOUGHNESS / IMPACT
    "Charpy_unnotched" : 80 *10** 3,         # [J/m²]

    # PROCESSING (thermoplastic)
    "T_melt"        : 380,             # melting / processing temp [°C]
    "weldable"      : True,            # thermoplastic welding possible

    # NOTES / SOURCE
    "notes" : (
        "Values typical for pultruded or thermo-stamped CF/PEEK with "
        "~55 % fibre volume.\n"
        "For short-fibre (30 wt %) PEEK pellets use: "
        "E ≈ 9-25 GPa, simga ≈ 150-250 MPa, rho ≈ 1 410 kg/m³."
    )
}

def calc_nvm(L=0.08839, Tz=-4.429, Ty=-7.6716, Wr=1.6527888, PLOT=True):
    """
    Cantilever beam (drone arm) with three tip-loads:
        Tz : horizontal (rightwards positive) tip force  [N]
        Ty : vertical (downwards positive) tip force  [N]
        Wr : vertical downward weight due to motor, ESC and propellor   [N]

    Returns axial-force N(x), shear-force V(x), and bending-moment M(x)
    diagrams and shows them with Matplotlib.
    """
    # ---- fixed-end reactions ----
    Rz = Tz                 # horizontal reaction at root
    Ry = Ty - Wr            # vertical reaction  (↑ if +ve)
    Mr = (Ty - Wr) * L      # reaction moment   (counter-clockwise +)

    # discretise beam for plotting
    x  = np.linspace(0, L, 400)
    N  = Rz * np.ones_like(x)           # axial: constant
    V  = Ry * np.ones_like(x)           # shear: constant
    M  = Mr - Ry * x                    # bending: linear

    # quick print-out of reactions
    print("\n=== Reactions at x = 0 (root) ===")
    print(f"Rz = {Rz:7.3f}  N")
    print(f"Ry = {Ry:7.3f}  N")
    print(f"Mr = {Mr:7.3f}  N·m")
    print("===============================\n")

    if PLOT:
        # ----- plots -----
        for data, title, ylabel in [
            (N, "Axial-Force Diagram (N)", "N(z)  [N]"),
            (V, "Shear-Force Diagram (V)", "V(z)  [N]"),
            (M, "Bending-Moment Diagram (M)", "M(z)  [N·m]")
        ]:
            plt.figure(figsize=(6,3))
            plt.plot(x, data, linewidth=2)
            plt.axhline(0, color="gray", linestyle="--", linewidth=0.8)
            plt.fill_between(x, data, color='lightblue')
            plt.title(title)
            plt.xlim(0, L)
            plt.ylim(-np.max(np.abs(data)) * 1.1, np.max(np.abs(data)) * 1.1)
            plt.gca().invert_yaxis() # negative values plotted upwards     
            plt.xlabel("Beam length x  [m]")
            plt.ylabel(ylabel)
            plt.grid(False)
            plt.show()
    
    return N, V, M


def calc_mmoi_rec(b, h, t,):    
    """
    Cal
    c = h / 2culate the moment of inertia of a rectangular beam
    """
    I_rec = (b * h**3) / 12 - (b - 2*t) * (h - 2*t)**3 / 12
    A = b * h - (b - t) * (h - t)
    return I_rec, A


def calc_mmoi_circ(d0, t):
    """
    Cal
    c = d0 / 2culate the moment of inertia of a tube beam
    """
    I_circ = np.pi * (d0**4 - (d0 - 2*t)**4) / 64
    A = np.pi * (d0**2 - (d0 - 2*t)**2) / 4
    return I_circ, A


def calc_bending_displacement(P, I, L, E):
    """
    Calculate the bending stress in a beam
    """
    x = np.linspace(0, L, 100) # Discretize the beam length
    delta = P * L**3 / (3 * E * I) # Bending displacement formula
    delta_y = P * x**2 / (6 * E * I) * (3 * L - x) # Bending displacement formula
    slope = P * L**2 / (2 * E * I) # Slope of the beam

    return delta, delta_y, slope


def calc_buckling_load(E, I, L, n=0.25):
    """

    c is distance from the neutral axis to the most distant fibre where you want the stress (m)     Calculate the buckling load of a beam
    """
    return n *(np.pi**2 * E * I) / (L)**2


def calc_bending_stress(M, I, c):
    """
    Calculate the bending stress in a beam IN MPa
    """
    return M * c / I

def calc_normal_stress(N, A):
    """
    Calculate the normal stress in a beam
    """
    return N / A


def calc_mass(A, L, rho):
    """
    Calculate the mass of a beam
    """
    return A * L * rho


if __name__ == "__main__":
    L = 0.1626345597 # Length of the beam in meters
    x = np.linspace(0, L, 100) # Discretize the beam length
    Tz = -4.429 # Horizontal force in Newtons
    Ty = -7.6716 # Vertical force in Newtons
    Wr = 1.6527888 # Motor + ESC + propellor weight in Newtons
    E = 70e9 # Young's modulus in Pascals (for aluminum)

    P = Wr + Ty # Total load on the beam in Newtons

    # Plot the NVM diagrams
    N, V, M = calc_nvm(L, Tz, Ty, Wr, PLOT=False)

    # Define the dimensions
    b = 0.0075
    h = 0.0075
    d0 = 0.0075

    rect_dict = {}
    circ_dict = {} 
    # 0.001, 0.002, 0.006, 0.01]
    # Test the moment of inertia calculation for different wall thicknesses
    for t in [0.004]:
        rect_sub_dict = {}
        # Rectangular beam
        I, A = calc_mmoi_rec(b, h, t)
        rect_sub_dict["MMOI"] = I

        if np.abs(Tz) > calc_buckling_load(E, I, L):
            print("The beam is buckling")
            rect_sub_dict["Buckling"] = True
            continue
        else: 
            rect_sub_dict["Buckling"] = False
        delta, delta_y, slope = calc_bending_displacement(P, I, L, E)
        rect_sub_dict["Max Displacement"] = delta
        rect_sub_dict["Slope"] = slope
        rect_sub_dict["Displacement"] = delta_y
        norm_stress = calc_normal_stress(N, A)
        comp_bend_stress = calc_bending_stress(M, I, d0/2)
        tens_bend_stress = calc_bending_stress(M, I, -d0/2)
        rect_sub_dict["Max Stress State"] = np.max(tens_bend_stress + norm_stress)
        rect_sub_dict["Min Stress State"] = np.min(comp_bend_stress + norm_stress)
        rect_sub_dict["Mass"] = calc_mass(A, L, CF_PEEK["rho"])
        rect_dict[t] = rect_sub_dict

        # Circular beam
        circ_sub_dict = {}
        I, A = calc_mmoi_circ(d0, t)
        circ_sub_dict["MMOI"] = I

        if np.abs(Tz) > calc_buckling_load(E, I, L):
            print("The beam is buckling")
            circ_sub_dict["Buckling"] = True
        else: 
            circ_sub_dict["Buckling"] = False
        delta, delta_y, slope = calc_bending_displacement(P, I, L, E)
        circ_sub_dict["Max Displacement"] = delta
        circ_sub_dict["Slope"] = slope
        circ_sub_dict["Displacement"] = delta_y
        norm_stress = calc_normal_stress(N, A)
        comp_bend_stress = calc_bending_stress(M, I, h/2)
        tens_bend_stress = calc_bending_stress(M, I, -h/2)
        circ_sub_dict["Max Stress State"] = np.max(tens_bend_stress + norm_stress)
        circ_sub_dict["Min Stress State"] = np.min(comp_bend_stress + norm_stress)
        circ_sub_dict["Mass"] = calc_mass(A, L, CF_PEEK["rho"])
        circ_dict[t] = circ_sub_dict
    
    print(f'Moment of inertia of rectangular beam: {rect_dict[0.004]["MMOI"]*10**(12)} mm^4')
    print(f'Moment of inertia of circular beam: {circ_dict[0.004]["MMOI"]*10**(12)} mm^4')
    print(f'Maximum displacement of rectangular beam: {np.max(rect_dict[0.004]["Max Displacement"])*10**(3)} mm')
    print(f'Maximum displacement of circular beam: {np.max(circ_dict[0.004]["Max Displacement"])*10**(3)} mm')
    print(f'Maximum stress state of rectangular beam: {np.max(rect_dict[0.004]["Max Stress State"])*10**(-6):.3f} MPa')
    print(f'Maximum stress state of circular beam: {np.max(circ_dict[0.004]["Max Stress State"])*10**(-6):.3f} MPa')
    print(f'Minimum stress state of rectangular beam: {np.min(rect_dict[0.004]["Min Stress State"])*10**(-6):.3f} MPa')
    print(f'Minimum stress state of circular beam: {np.min(circ_dict[0.004]["Min Stress State"])*10**(-6):.3f} MPa')
    print(f'Mass of rectangular beam: {rect_dict[0.004]["Mass"]*10**(3)} g')
    print(f'Mass of circular beam: {circ_dict[0.004]["Mass"]*10**(3)} g')

        
    # plt.figure(figsize=(6,3))
    # for t, data in rect_dict.items():
    #     plt.plot(x, data["Displacement"], label=f"t={t:.3f} m")
    # plt.plot(x, np.zeros(100), color="gray", label="Zero Displacement")
    # plt.title("Bending Displacement of Rectangular Beam")
    # plt.xlabel("Beam length x  [m]")
    # plt.ylabel("Displacement [m]")
    # plt.gca().invert_yaxis()
    # plt.legend()
    # plt.grid(False)
    # plt.show()

    # plt.figure(figsize=(6,3))
    # for t, data in circ_dict.items():
    #     plt.plot(x, data["Displacement"], label=f"t={t:.3f} m")
    # plt.plot(x, np.zeros(100), color="gray", label="Zero Displacement")
    # plt.title("Bending Displacement of Circular Beam")
    # plt.xlabel("Beam length x  [m]")
    # plt.ylabel("Displacement [m]")
    # plt.gca().invert_yaxis()
    # plt.legend()
    # plt.grid(False)
    # plt.show()
    # for t, data in rect_dict.items():
    #     print(f"Maximum stress state for rectangular beam with t={t:.3f} m: {np.max(data['Max Stress State'])*10**(-6):.3f} MPa")
    #     print(f"Minimum stress state for rectangular beam with t={t:.3f} m: {np.min(data['Min Stress State'])*10**(-6):.3f} MPa")
    # print("==========================")
    # for t, data in circ_dict.items():
    #     print(f"Maximum stress state for circular beam with t={t:.3f} m: {np.max(data['Max Stress State'])*10**(-6):.3f} MPa")
    #     print(f"Minimum stress state for circular beam with t={t:.3f} m: {np.min(data['Min Stress State'])*10**(-6):.3f} MPa")