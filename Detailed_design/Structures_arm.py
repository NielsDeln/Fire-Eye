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


def calculate_shear_stress(V, M, d0, I, J, L, t):
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
    if t < 0.1 * L:
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
    if M[0] == 0:
        return np.pi / 2
    else:
        return np.arctan2(M[1], M[0])


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


def calculate_stresses(F, M, I, J, A, d0, t, L):
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
    shear_stress = calculate_shear_stress(F, M, d0, I, J, L, t)

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
    if F[1] != 0:
        z_deflection = F[2] * L / (3 * E * I)
        z_rotation = F[2] * L**2 / (2 * E * I)
    if M[0] != 0:
        z_deflection += -M[0] * L**2 / (2 * E * I)
        z_rotation += -M[0] / (E * I)
    else:
        z_deflection = 0
        z_rotation = 0

    if F[0] != 0:
        x_deflection = F[0] * L**3 / (3 * E * I)
        x_rotation = F[0] * L**2 / (2 * E * I)
    if M[1] != 0:
        x_deflection += -M[1] * L**2 / (2 * E * I)
        x_rotation += -M[1] / (E * I)
    else:
        x_deflection = 0
        x_rotation = 0

    return z_deflection, z_rotation


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
    # Example usage
    F_T = 8.8583  # Thrust force in N
    T = 5.0  # Torque in Nm
    W = 0.7012188 # Motor + ESC + propellor weight in Newtons
    alpha = np.radians(30)  # Angle in radians
    beta = np.radians(0)  # Angle in radians

    L = 0.17889 # Length of the arm in m
    h = 0.005175  # Height of the arm in m
    R_A_position = np.array([0.0, -h, L])  # Position vector of the reaction point
    R_B_position = np.array([0.0, -h, 0.0])  # Position vector of the reaction point for the second motor

    A_forces, A_moments = calculate_arm_forces(F_T, W, alpha, beta, T, R_A_position)
    B_forces, B_moments = calculate_arm_forces(F_T, W, alpha, beta, T, R_B_position)

    print("Reaction forces [N]:", A_forces)
    print("Reaction moments [Nm]:", A_moments)
    print("-----------------------------")

    # Example for calculating section properties
    d0 = 0.02  # Outer diameter in m
    t = 0.002  # Thickness in m
    I, J, A = calculate_section(d0, t)
    print("Moment of Inertia [kg*m^2]:", I)
    print("Polar Moment of Inertia [kg*m^2]:", J)
    print("Cross-sectional Area [m^2]:", A)
    print("-----------------------------")
    # Example for calculating stresses
    bend_str, shear_str, axial_str, NA_alpha = calculate_stresses(A_forces, A_moments, I, J, A, d0, t, L)
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

    # Example for calculating buckling load
    E = 70e9  # Young's modulus in Pa (e.g., aluminum)
    buckling_load = calculate_buckling(E, I, L, A, A_forces[2])