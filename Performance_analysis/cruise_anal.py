import numpy as np


alt = 1.5 # flying altitude in m
motion_px = 2
shutter_speed = 1 / 120

camera_res = [1920, 1080] # hoz, vert resolution in px
camera_fov_deg = [141.4, 81.7] # hoz, vert FOV in degrees
camera_fov_rad = [np.deg2rad(fov) for fov in camera_fov_deg] # hoz, vert FOV in radians

def forensic_cruise(alt = alt, motion_px = motion_px):
    
    W = 2 * alt * np.tan(camera_fov_rad[0] / 2) # width of the scene in m
    H = 2 * alt * np.tan(camera_fov_rad[1] / 2) # height of the scene in m

    pixel_size = [W / camera_res[0], H / camera_res[1]] # size of a pixel in m

    max_velocities = [pixel_size[0] / shutter_speed, pixel_size[1] / shutter_speed] * motion_px

    v_max = max(max_velocities)

    return v_max

print(forensic_cruise())


