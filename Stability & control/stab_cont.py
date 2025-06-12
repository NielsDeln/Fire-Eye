import numpy as np

def rotation_matrix_traditional(roll, pitch, yaw):
    """
    Create a 3D rotation matrix from world-frame to body-frame from
    roll, pitch, and yaw angles.
    
    Args:
        roll (float): rotation angle around x-axis in radians
        pitch (float): rotation angle around y-axis in radians
        yaw (float): rotation angle around z-axis in radians
        
    Returns:
        numpy.ndarray: 3x3 rotation matrix
    """
    # Rotation matrix for roll (x-axis)
    Rx = np.array([[1, 0, 0],
                    [0, np.cos(roll), np.sin(roll)],
                    [0, -np.sin(roll), np.cos(roll)]])
    
    # Rotation matrix for pitch (y-axis)
    Ry = np.array([[np.cos(pitch), 0, -np.sin(pitch)],
                    [0, 1, 0],
                    [np.sin(pitch), 0, np.cos(pitch)]])
    
    # Rotation matrix for yaw (z-axis)
    Rz = np.array([[np.cos(yaw), np.sin(yaw), 0],
                    [-np.sin(yaw), np.cos(yaw), 0],
                    [0, 0, 1]])
    
    # Combined rotation matrix: R = Rz * Ry * Rx
    R = Rz @ Ry @ Rx
    return R

def force_vector(Kf, omega, rotor_angles):
    """
    Function for force vector computation for body-ficed frame.
    
    Returns:
        numpy.ndarray: Force vector
    """
    # Compute individual rotor forces
    F_rotors = [Kf * (w ** 2) for w in omega]
    
    Fx = -F_rotors[1] * np.sin(rotor_angles[1]) + F_rotors[3] * np.sin(rotor_angles[3])
    Fy = -F_rotors[0] * np.cos(rotor_angles[0]) + F_rotors[2] * np.cos(rotor_angles[2])
    Fz = -np.sum(F_rotors * np.cos(rotor_angles))

    #Note that this is only the function for the body fixed and you still have to do it for the world frame

    force_vector = np.array([Fx, Fy, Fz])#np.array([0, 0, 0])  # Replace with actual computation
    return force_vector	

def torque_vector(Kf, Km, omega, rotor_angles, l_arm):
    """
    Placeholder function for angular accelerations computation.
    This function should be implemented to compute the angular accelerations
    based on the specific requirements of the stability and control system.
    
    Returns:
        numpy.ndarray: Angular accelerations
    """
    # Compute individual rotor torques and forces
    T_rotors = [Km * (w ** 2) for w in omega]
    F_rotors = [Kf * (w ** 2) for w in omega]
    
    # Compute angular accelerations based on rotor torques and angles
    # This is a placeholder; actual implementation will depend on system dynamics
    Tx = l_arm
    
    '''
    Torques should be adjusted based on rotor angles
    '''
    
    angular_acc = np.array([T_rotors[0] - T_rotors[1], 
                             T_rotors[2] - T_rotors[3], 
                             0])  # Replace with actual computation
    return angular_acc

if __name__ == "__main__":
    # Define angles in degrees
    roll_deg = 30
    pitch_deg = 45
    yaw_deg = 60
    
    # Convert angles to radians
    roll = np.deg2rad(roll_deg)
    pitch = np.deg2rad(pitch_deg)
    yaw = np.deg2rad(yaw_deg)
    
    # Compute rotation matrix
    R = rotation_matrix_traditional(roll, pitch, yaw)
    
    # Print rotation matrix
    print("Rotation Matrix:\n", R)

omega = [1000, 1000, 1000, 1000]  # Example rotor speeds in RPM
Kf = 0.1  # Example force coefficient
rotor_angles = [0, np.pi/2, np.pi, 3*np.pi/2]  # Example rotor angles in radians
force_vec = force_vector(Kf, omega, rotor_angles)
print("Force Vector:", force_vec)