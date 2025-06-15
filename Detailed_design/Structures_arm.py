import numpy as np


def calculate_arm_forces(F_T, W, alpha, beta, T, R_position):
    """
    Calculate the forces acting on a structure based on the given parameters.
    Axis system:
    - x: Complete right handed coordinate system
    - y: Downwards direction positive
    - z: In beam direction (Right) positive

    Parameters:
    F_t (float): Thrust force due to motors.
    W (float): Weight of the motor + ESC + propellor in Newtons.
    alpha (float): Angle of the motor with respect to the vertical.
    beta (float): Angle of the motor with respect to the negative x axis.
    T (float): Torque due to spinning propeller.
    R_position (array): Position vector of the reaction point in the structure.

    Returns:
    array: Reaction force acting on the structure.
    array: Reaction moment acting on the structure.
    """
    # Calculate the applied forces and torques based on the angles
    F_applied = np.array([F_T * np.sin(beta), W - (F_T * np.cos(alpha)), -(F_T * np.sin(alpha))])
    T_applied = T * np.array([np.sin(beta), -np.cos(alpha), -np.sin(alpha)])

    # Calculate the reaction forces and moments
    # Reaction force is equal and opposite to the applied force
    # Reaction moment is calculated using the cross product of position vector and applied force, minus the applied torque
    # Note: The reaction force and moment are in the opposite direction of the applied force and moment
    F_reaction = -F_applied
    M_reaction = -np.cross(R_position, F_applied) - T_applied
    return F_reaction, M_reaction


def calculate_internal_forces(F_T, alpha, beta, T, L, h):
    """
    DOES NOT WORK CURRENTLY 
    Calculate the internal forces acting on a structure based on the given parameters.
    
    Parameters:
    F_T (float): Thrust force due to motors.
    alpha (float): Angle of the motor with respect to the vertical.
    beta (float): Angle of the motor with respect to the negative x axis.
    T (float): Torque due to spinning propeller.
    L (array): Length of the arm.
    h (array): Height of the arm.

    Returns:
    array: Internal reaction force acting on the structure.
    array: Internal reaction moment acting on the structure.
    """
    raise NotImplementedError("This function is not implemented yet.")
    # Calculate the position vector of the reaction point in the structure
    R_position = np.array([np.zeros(len(L)), L, h])

    # Initialize lists to store forces and moments
    forces = []
    moments = []

    # Calculate the forces and moments for each motor
    force, moment = calculate_arm_forces(F_T, alpha, beta, T, R_position)
    forces.append(force)
    moments.append(moment)
    return forces, moments


def calculate_section(d0, t):
    """
    Calculate the moment of inertia for a hollow cylinder.
    """
    I = np.pi * (d0**4 - (d0 - 2*t)**4) / 64
    J = np.pi * (d0**4 - (d0 - 2*t)**4) / 32
    A = np.pi * (d0**2 - (d0 - 2*t)**2) / 4
    return I, J, A


def calculate_shear_stress(V, M, d0, I, J, t):
    """
    Calculate the shear stress in a structure based on the applied force and dimensions.

    Parameters:
    V (array): Applied shear force.
    M (array): Applied moment vector.
    d0 (float): Outer diameter of the structure.
    I (float): Moment of inertia of the cross-section.
    J (float): Polar moment of inertia of the cross-section.
    t (float): Thickness of the structure.

    Returns:
    array: Shear stress in the x and y directions, and torsional shear stress.
    """
    # First moment of area where transverse shear stress is max (at half section)
    Q = 2 * ((d0 / 2)**3 - ((d0 - 2 * t) / 2)**3) / 3

    # Calculate the shear stress using the formula (V * Q) / (I * t)
    shear_y = V[1] * Q / (I * t)
    if V[0] != 0:
        shear_x = V[0] * Q / (I * t)
    else:
        shear_x = 0

    # Calculate shear stress due to torsion
    if t < 0.1 * d0:
        torsion_shear = M[2] / (2 * t * np.pi * (d0 - t)**2)
    else:
        torsion_shear = M[2] * (d0 / 2) / J

    return np.array([shear_x, shear_y, torsion_shear])


def calculate_neutral_axis(M):
    """
    Calculate the neutral axis of the structure based on the applied moment.

    Parameters:
    M (array): Applied moment vector.

    Returns:
    float: Position of the neutral axis.
    """
    return np.pi / 2 if M[0] == 0 else np.arctan2(M[1], M[0])



def calculate_axial_stress(M, I, d0, t, NA_alpha):
    """
    Calculate the bending stress in a structure based on the applied moment and dimensions.

    Parameters:
    M (array): Applied bending moment vector [Mx, My, Mz].
    I (float): Moment of inertia of the cross-section.
    d0 (float): Outer diameter of the structure.
    t (float): Thickness of the structure.

    Returns:
    tuple: (bend_stress, x_points, y_points)
        bend_stress (array): Bending stress at each (x, y) point.
        x_points (array): x-coordinates of evaluated points.
        y_points (array): y-coordinates of evaluated points.
    """
    x = d0 / 2 * np.cos(NA_alpha + np.pi / 2)  # x-coordinates based on neutral axis angle
    y = d0 / 2 * np.sin(NA_alpha + np.pi / 2)  # y-coordinates based on neutral axis angle
    # Calculate bending stress at each valid (x, y) point
    bend_stress = (M[0] * y - M[1] * x) / I
    
    return bend_stress


def calculate_stresses(F, M, I, J, A, d0, t):
    """
    Calculate the stresses in a structure based on the applied forces and moments.
    Includes bending stress, shear stress (including due to torsion), and axial stress.

    Parameters:
    F (array): Applied force vector.
    M (array): Applied moment vector.
    I (array): Moment of inertia.
    J (array): Polar moment of inertia.
    A (array): Cross-sectional area.
    d0 (float): Outer diameter of the structure.
    t (float): Thickness of the structure.

    Returns:
    array: Bending stress.
    array: Shear stress.
    array: Axial stress.
    """
    # Calculate the neutral axis position
    NA_alpha = calculate_neutral_axis(M)

    # Calculate stresses
    bending_stress = calculate_axial_stress(M, I, d0, t, NA_alpha)
    shear_stress = calculate_shear_stress(F, M, d0, I, J, t)

    # Axial stress is calculated as force divided by area
    axial_stress = -F[2] / A
    return bending_stress, shear_stress, axial_stress, NA_alpha


def calculate_buckling(E, I, L, K=2):
    """
    Calculate the buckling load for a column based on Euler's formula.

    Parameters:
    E (float): Young's modulus of the material.
    I (float): Moment of inertia of the cross-section.
    L (float): Length of the column.

    Returns:
    float: Critical buckling load.
    """
    P_cr = (np.pi**2 * E * I) / (L**2)
    return P_cr


def calculate_deformation(F, M, L, E, I):
    """
    Calculate the deformation of a structure based on the applied forces and moments.

    Parameters:
    F (array): Applied force vector.
    M (array): Applied moment vector.
    L (float): Length of the structure.
    E (float): Young's modulus of the material.
    I (float): Moment of inertia of the cross-section.

    Returns:
    tuple: (deflection, rotation)
        deflection (float): Deflection at the end of the structure.
        rotation (float): Rotation at the end of the structure.
    """
    deflections = []
    rotations = []
    if F != 0:
        deflections.append(F * L**3 / (3 * E * I))
        rotations.append(F * L**2 / (2 * E * I))
    if M != 0:
        deflections.append(-M * L**2 / (2 * E * I))
        rotations.append(-M * L / (E * I))

    return np.array(deflections), np.array(rotations)


def calculate_torsion_deflection(T, L, G, J):
    """
    Calculate the torsional deflection of a structure based on the applied torque.

    Parameters:
    T (float): Applied torque.
    L (float): Length of the structure.
    G (float): Shear modulus of the material.
    J (float): Polar moment of inertia of the cross-section.

    Returns:
    float: Torsional deflection at the end of the structure.
    """
    theta = T * L / (G * J)
    return theta


def calculate_mass(rho, L, h, d0, t):
    """
    Calculate the mass of a structure based on its dimensions and material density.

    Parameters:
    rho (float): Density of the material.
    L (float): Total length of the arm.
    h (float): Total height of the arm.
    d0 (float): Outer diameter of the structure.
    t (float): Thickness of the structure.

    Returns:
    float: Mass of the structure.
    """
    volume = np.pi * (d0**2 - (d0 - 2*t)**2) / 4 * L + np.pi * (d0**2 - (d0 - 2*t)**2) / 4 * h
    mass = rho * volume
    return mass


if __name__ == "__main__":
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
    # Material properties
    rho = 1320  # Density in kg/m^3 (e.g., PEEK)
    poisson = 0.35  # Poisson's ratio (e.g., PEEK)
    E = 12e9  # Young's modulus in Pa (e.g., PEEK)
    G = E / (2 * (1 + poisson))  # Shear modulus in Pa (e.g., PEEK)
    d0 = 0.02  # Outer diameter in m
    t = 0.001  # Thickness in m
    L = 0.190  # Length of the arm in m
    h = 0.005  # Height of the arm in m
    safety_factor = 1.5  # Safety factor for the design

    # Propulsion forces and moments
    F_T = 8.22777935  # Thrust force in N
    T = 0.173  # Torque in Nm
    W = 0.7966  # Motor + propellor weight in Newtons
    alpha = np.radians(0)  # Angle in radians
    beta = np.radians(0)  # Angle in radians
    R_A_position = np.array([0.0, -h, L])  # Position vector of the reaction point
    R_B_position = np.array([0.0, -h, 0.0])  # Position vector of the reaction point for the second motor

    A_forces, A_moments = calculate_arm_forces(F_T, W, alpha, beta, T, R_A_position)
    B_forces, B_moments = calculate_arm_forces(F_T, W, alpha, beta, T, R_B_position)

    print("Reaction forces [N]:", A_forces)
    print("Reaction moments [Nm]:", A_moments)
    print("-----------------------------")

    # Calculating section properties
    I, J, A = calculate_section(d0, t)
    print("Moment of Inertia [m^4]:", I)
    print("Polar Moment of Inertia [m^4]:", J)
    print("Cross-sectional Area [m^2]:", A)
    print("-----------------------------")
    # Calculating stresses
    bend_str, shear_str, axial_str, NA_alpha = calculate_stresses(A_forces, A_moments, I, J, A, d0, t)
    min_str = -np.max(np.abs(bend_str)) + axial_str
    max_str = np.max(np.abs(bend_str)) + axial_str
    print("Bending Stress [MPa]:", bend_str * 1e-6)
    print("Shear Stress [MPa]:", shear_str * 1e-6)
    print("Axial Stress [MPa]:", axial_str * 1e-6)
    print("-----------------------------")
    print("Minimum Stress [MPa]:", min_str * 1e-6)
    print("Maximum Stress [MPa]:", max_str * 1e-6)
    print("Shear Stress [MPa]:", shear_str.sum() * 1e-6)
    print("Neutral Axis Angle [deg]:", NA_alpha * 180 / np.pi)
    print("-----------------------------")
    print("Safety Factor:", safety_factor)
    print("Design Minimum Stress [MPa]:", min_str * 1e-6 * safety_factor)
    print("Design Maximum Stress [MPa]:", max_str * 1e-6 * safety_factor)
    print("Design Shear Stress [MPa]:", shear_str.sum() * 1e-6 * safety_factor)
    print("-----------------------------")

    # Calculating buckling load
    buckling_load = calculate_buckling(E, I, L)
    print("Buckling Load [N]:", buckling_load)
    print("-------------------------------")

    # Calculating deformation
    y_deformation, y_rotation = calculate_deformation(-B_forces[1] * safety_factor, -B_moments[0] * safety_factor, L, E, I)
    x_deformation, x_rotation = calculate_deformation(-B_forces[0] * safety_factor, -B_moments[1] * safety_factor, L, E, I)
    z_deformation, z_rotation = axial_str / E, calculate_torsion_deflection(-B_moments[2], L, G, J)
    print("Deformation in y-direction [mm]:", y_deformation.sum() * 1e3)
    print("Rotation in y-direction [deg]:", y_rotation.sum() * 180 / np.pi)
    print("-------------------------------")
    print("Deformation in x-direction [mm]:", x_deformation.sum() * 1e3)
    print("Rotation in x-direction [deg]:", x_rotation.sum() * 180 / np.pi)
    print("-------------------------------")
    print("Deformation in z-direction [mm]:", z_deformation * 1e3)
    print("Rotation in z-direction [deg]:", z_rotation * 180 / np.pi)
    print("-------------------------------")

    # Calculating mass
    mass = calculate_mass(rho, L, h, d0, t)
    print("Mass of the structure [g]:", mass * 1e3)
    print("-------------------------------")