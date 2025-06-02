import numpy as np
import matplotlib.pyplot as plt
# -------------------------------------------------------------
#   Material property sheet  ―  Carbon-Fibre / PEEK laminate
#   (continuous UD fibres, ~55 % Vf, room-temperature data)
#   Units: SI  (kg, m, N, Pa, J, °C)
# -------------------------------------------------------------
CF_PEEK = {
    # PHYSICAL
    "rho"           : 1550,           # density ρ  [kg/m³]

    # ELASTIC MODULI  (use the one that matches your lay-up)
    "E"        : 150 * 10**9,           # UD 0° modulus  [Pa]
    "E_quasi_iso"   : 75 *10**9,            # quasi-isotropic laminate  [Pa]
    "G_in_plane"    : 5.0 *10**9,           # shear modulus  ±45° laminate [Pa]
    "nu"            : 0.3,             # Poisson’s ratio  (average)

    # STRENGTH ALLOWABLES (already knocked-down, A-basis) – apply project SF!
    "sigma_t_allow" : 2.5 *10** 8,           # tensile allow (0°)  [Pa]
    "sigma_c_allow" : 2.0 *10** 8,           # compressive allow (0°) [Pa]
    "tau_allow"     : 9.0 *10** 7,           # in-plane shear allow  [Pa]
}

# 2024-T3 aluminium (sheet) – key room-temperature properties
Al2024_T3 = {
    "rho": 2780,              # kg/m^3
    "E": 73e9,                    # Pa  (Young’s modulus)
    "G": 27e9,                    # Pa  (shear modulus)
    "melting_range": (502, 638),  # °C  (solidus, liquidus)
    "Tg": None,                   # not applicable – fully crystalline
    "sigma_y": 345e6,             # Pa  (0.2 % yield strength)
    "sigma_UTS": 483e6            # Pa  (ultimate tensile strength)
}

# CFRP (carbon-fibre reinforced polymer) – key properties
CFRP = {
    "rho": 1560,              # kg/m^3
    "E_flex": 4.1e9,              # Pa  (Flexural modulus)
    "E": 131e9,              # Pa  (Tensile modulus 0°)
    "E_comp": 128e9,              # Pa  (Compressive modulus 0°)
    "G": 128e9,                   # Pa  (shear modulus)
    "Tg": 194,                    # °C  (glass-transition temperature)
    "sigma_Comp": 1680e6,         # Pa  (ultimate compressive strength)
    "sigma_Tens": 1620e6          # Pa  (ultimate tensile strength)
}

# Acrylonitrile Butadiene Styrene (ABS), unfilled
ABS = {
  "rho": 1020,           # kg/m³
  "E_flex": 2.3e9,       # Pa  (Flexural modulus)
  "E": 2.1e9,       # Pa  (Tensile modulus 0°)
  "E_comp": 2.4e9,       # Pa  (Compressive modulus 0°)
  "G": 0.9e9,            # Pa  (Shear modulus)
  "Tg": 105,             # °C  (Glass‑transition temperature)
  "sigma_Comp": 62e6,    # Pa  (Ultimate compressive strength)
  "sigma_Tens": 40e6     # Pa  (Ultimate tensile strength)
}

# Polypropylene (PP), molded
PP = {
  "rho": 900,            # kg/m³
  "E_flex": 1.5e9,       # Pa  (Flexural modulus)
  "E": 1.5e9,       # Pa  (Tensile modulus 0°)
  "E_comp": 1.6e9,       # Pa  (Compressive modulus 0°)
  "G": 0.7e9,            # Pa  (Shear modulus)
  "Tg": 0,               # °C  (Glass‑transition temperature)
  "sigma_Comp": 45e6,    # Pa  (Ultimate compressive strength)
  "sigma_Tens": 30e6     # Pa  (Ultimate tensile strength)
}
# Liquid Crystal Polymer (LCP), e.g. Vectra A950
LCP = {
  "rho": 1650,            # kg/m³
  "E_flex": 22e9,         # Pa  (Flexural modulus)
  "E": 12e9,         # Pa  (Tensile modulus 0°)
  "E_comp": 18e9,         # Pa  (Compressive modulus 0°)
  "G": 4e9,               # Pa  (Shear modulus)
  "Tg": 260,              # °C  (Glass‑transition temperature)
  "sigma_Comp": 200e6,    # Pa  (Ultimate compressive strength)
  "sigma_Tens": 250e6     # Pa  (Ultimate tensile strength)
}

# Polycarbonate (PC), unfilled, injection‑molded
PC = {
  "rho": 1200,            # kg/m³
  "E_flex": 2.4e9,        # Pa  (Flexural modulus)
  "E": 2.2e9,        # Pa  (Tensile modulus 0°)
  "E_comp": 2.3e9,        # Pa  (Compressive modulus 0°)
  "G": 0.8e9,             # Pa  (Shear modulus)
  "Tg": 147,              # °C  (Glass‑transition temperature)
  "sigma_Comp": 90e6,     # Pa  (Ultimate compressive strength)
  "sigma_Tens": 65e6      # Pa  (Ultimate tensile strength)
}

# Nylon 6 (PA6), unfilled, injection‑molded
PA6 = {
  "rho": 1140,            # kg/m³
  "E_flex": 2.7e9,        # Pa  (Flexural modulus)
  "E": 2.9e9,        # Pa  (Tensile modulus 0°)
  "E_comp": 3.1e9,        # Pa  (Compressive modulus 0°)
  "G": 1.0e9,             # Pa  (Shear modulus)
  "Tg": 50,               # °C  (Glass‑transition temperature)
  "sigma_Comp": 80e6,     # Pa  (Ultimate compressive strength)
  "sigma_Tens": 70e6      # Pa  (Ultimate tensile strength)
}

# Polyether Ether Ketone (PEEK), unfilled
PEEK = {
  "rho": 1320,            # kg/m³
  "E_flex": 3.6e9,        # Pa  (Flexural modulus)
  "E": 3.4e9,        # Pa  (Tensile modulus 0°)
  "E_comp": 4.3e9,        # Pa  (Compressive modulus 0°)
  "G": 1.5e9,             # Pa  (Shear modulus)
  "Tg": 143,              # °C  (Glass‑transition temperature)
  "sigma_Comp": 100e6,    # Pa  (Ultimate compressive strength)
  "sigma_Tens": 90e6      # Pa  (Ultimate tensile strength)
}
mat_dict = {"PEEK": PEEK, "PA6": PA6, "PC": PC, "LCP": LCP, "ABS": ABS, "PP": PP, "Al2024_T3": Al2024_T3, "CFRP": CFRP, "CF_PEEK": CF_PEEK}

def calc_nvm(L=0.17889, h=3.175, Tz=-4.429, Ty=-7.6716, Wr=1.6527888, PLOT=True):
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
    Mr = (Ty - Wr) * L + h * Tz    # reaction moment   (counter-clockwise +)

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
        colours = ["#26547C",  # YInMn Blue
                   "#A6808C",  # Mountbatten Pink
                   "#EAC435"]  # Saffron
        # ----- plots -----
        for (data, title, ylabel), col in zip(
            [(N, "Axial-Force Diagram (N)",     "N(z)  [N]"),
            (V, "Shear-Force Diagram (V)",     "V(z)  [N]"),
            (M, "Bending-Moment Diagram (M)", "M(z)  [N·m]")],
            colours):
            plt.figure(figsize=(6, 3))
            plt.plot(x, data, linewidth=2, color=col)          # main curve
            plt.axhline(0, color="gray", linestyle="--", linewidth=0.8)
            plt.fill_between(x, data, color=col, alpha=0.30)   # lighter tint
            # plt.title(title)
            plt.xlim(0, L)
            plt.ylim(-np.max(np.abs(data))*1.1, np.max(np.abs(data))*0.5)
            plt.gca().invert_yaxis()
            plt.xlabel(r"Beam length $z$  [m]", fontsize=30)  # axis title
            plt.ylabel(ylabel, fontsize=30)
            plt.tick_params(axis='both', which='major', labelsize=30)  # tick numbers
            plt.grid(False)
    
    return N, V, M


def calc_mmoi_rec(b, h, t,):    
    """
    Cal
    c = h / 2culate the moment of inertia of a rectangular beam
    """
    I_rec = (b * h**3) / 12 - (b - 2*t) * (h - 2*t)**3 / 12
    A = b * h - (b - 2* t) * (h - 2* t)
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


def calc_mass(A, L, h, rho):
    """
    Calculate the mass of a beam
    """
    return A * L * rho + A * h * rho


if __name__ == "__main__":
    L = 0.17889 # Length of the beam in meters
    h = 0.005175  # Height of the beam in meters
    x = np.linspace(0, L, 100) # Discretize the beam length
    Tz = -4.429 # Horizontal force in Newtons
    Ty = -7.6716 # Vertical force in Newtons
    Wr = 0.7012188 # Motor + ESC + propellor weight in Newtons

    P = Wr + Ty # Total load on the beam in Newtons

    # Plot the NVM diagrams
    N, V, M = calc_nvm(L, h, Tz, Ty, Wr, PLOT=True)

    # Define the dimensions
    b = 0.02
    h = 0.02
    d0 = 0.02

    rect_dict = {}
    circ_dict = {} 
    # , 0.002, 0.004, 0.006
    # Test the moment of inertia calculation for different wall thicknesses
    for material in ["CFRP", "Al2024_T3", "CF_PEEK", "PEEK", "ABS", "PC", "PA6", "LCP"]:
        E = mat_dict[material]['E']
        rho = mat_dict[material]['rho']
        for beam in ["rect", "circ"]:
            for t in [0.001, 0.002, 0.004, 0.006]:
                sub_dict = {}

                # Calculate moment of inertia and area
                if beam == "rect":
                    # Rectangular beam
                    I, A = calc_mmoi_rec(b, h, t)
                else:
                    # Circular beam
                    I, A = calc_mmoi_circ(d0, t)
                sub_dict["MMOI"] = I

                # Calculate buckling load of the beam
                sub_dict["Buckling"] = calc_buckling_load(E, I, L)

                # Calculate bending displacement and slope
                delta, delta_y, slope = calc_bending_displacement(P, I, L, E)
                sub_dict["Max Displacement"] = delta
                sub_dict["Slope"] = slope
                sub_dict["Displacement"] = delta_y

                # Calculate normal and bending stress
                norm_stress = calc_normal_stress(N, A)
                if beam == "rect":
                    comp_bend_stress = calc_bending_stress(M, I, h/2)
                    tens_bend_stress = calc_bending_stress(M, I, -h/2)
                else:
                    comp_bend_stress = calc_bending_stress(M, I, d0/2)
                    tens_bend_stress = calc_bending_stress(M, I, -d0/2)
                sub_dict["Max Stress State"] = np.max(tens_bend_stress + norm_stress)
                sub_dict["Min Stress State"] = np.min(comp_bend_stress + norm_stress)

                # Calculate mass of the beam
                sub_dict["Mass"] = calc_mass(A, L, h, rho)

                # Store the results in the dictionary
                if beam == "rect":
                    rect_dict[t] = sub_dict
                else:
                    circ_dict[t] = sub_dict
        
        # Print the results
        for beam in ["rect", "circ"]:
            for t, data in (rect_dict if beam == "rect" else circ_dict).items():
                print(f"{beam} beam with t={t:.3f} m:")
                print(f"  Material: {material}")
                print(f"  Moment of Inertia: {data['MMOI'] * 1e12:.3e} mm^4")
                print(f"  Buckling Load: {data['Buckling']:.3e} N")
                print(f"  Max Displacement: {np.max(data['Max Displacement']) * 1e3:.3e} mm")
                print(f"  Slope: {data['Slope']:.3e} rad")
                print(f"  Max Stress State: {np.max(data['Max Stress State']) * 1e-6:.3f} MPa")
                print(f"  Min Stress State: {np.min(data['Min Stress State']) * 1e-6:.3f} MPa")
                print(f"  Mass: {data['Mass'] * 1e3:.3f} gg")
                print("==========================")
    
    for beam in ["rectangular", "circular"]:
        plt.figure(figsize=(6,3))
        for t, data in (rect_dict if beam == "rectangular" else circ_dict).items():
            plt.plot(x, data["Displacement"], label=f"t={t:.3f} m")
        plt.plot(x, np.zeros(100), color="gray", label="Zero Displacement")
        plt.title(f"Bending Displacement of {beam} Beam")
        plt.xlabel(r"Beam length $z$  [m]", fontsize=20)
        plt.ylabel("Displacement [m]", fontsize=20)
        plt.tick_params(axis='both', which='major', labelsize=20)
        plt.gca().invert_yaxis()
        plt.legend(fontsize=20)
        plt.grid(False)
        plt.show()