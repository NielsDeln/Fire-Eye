import numpy as np
from math import cos, sin, tan, radians
from pprint import pprint

# Conversion functions
def g_to_kg(mass_g):
    return mass_g / 1000.0

def compute_cg(components):
    total_mass = 0
    weighted_sum_x = 0.0
    weighted_sum_y = 0.0
    weighted_sum_z = 0.0

    for name, comp in components.items():
        dims_m = mm_to_m(comp["dimensions_mm"])
        mass_kg_unit = g_to_kg(comp["weight_g"])
        quantity = comp["quantity"]
        x_cgs = comp["x_cg"]
        # print(f"\n{name} - Dimensions (m): {dims_m}, Mass (kg): {mass_kg_unit}, Quantity: {quantity}, CoG: {x_cgs}")
        for i in range(quantity):
            # x_cg = x_cgs[i]
            x_cg_mm = x_cgs[i]
            x_cg = tuple(coord / 1000.0 for coord in x_cg_mm)
            total_mass += mass_kg_unit
            weighted_sum_x += mass_kg_unit * x_cg[0]
            weighted_sum_y += mass_kg_unit * x_cg[1]
            weighted_sum_z += mass_kg_unit * x_cg[2]
        
    x_cg_total = (
        weighted_sum_x / total_mass,
        weighted_sum_y / total_mass,
        weighted_sum_z / total_mass,
    )
    return x_cg_total, total_mass

#check up
def compute_x_distance(cg, point_mm):
    return abs(point_mm[0] / 1000 - cg[0])

def iterate_arm_length(components, arms_back_v_len_mm=20.0, max_iter=1000, tol=1e-6):
    arms_back_v_len = arms_back_v_len_mm / 1000
    angle_rad = radians(68.2)

    # Match these front Y values
    y_arm_front = 137.81
    y_arm_front_v = 216.62

    # Initial rear arm length
    arms_back_len = 0.19
    front_arm_positions = [(137.34, -216.62), (137.34, 216.62)]

    #Constants
    density = 1.38e-6 #kg/mm^3
    diameter_mm, thickness_mm, _ = components["arms_back"]["dimensions_mm"]

    cg, total_mass = compute_cg(components)

    for _ in range(max_iter):
        front_x_dist = abs(137.34 / 1000 - cg[0])

        arms_back_len_mm = arms_back_len * 1000
        x_offset = (210.5 / 2 - tan(radians(8)) * (118 / 2) - 18.6)
        x_arm = -x_offset - cos(angle_rad) * arms_back_len_mm
        x_arm_mid = -x_offset - 0.5 * cos(angle_rad) * arms_back_len_mm

        # Force symmetry in y-axis to match front arms
        y_arm_upper = y_arm_front
        y_arm_lower = -y_arm_front
        y_arm_v_upper = y_arm_front_v
        y_arm_v_lower = -y_arm_front_v

        components["arms_back"]["x_cg"][0] = (x_arm_mid, y_arm_upper, 39.65)
        components["arms_back"]["x_cg"][1] = (x_arm_mid, y_arm_lower, 39.65)

        #old_dims = components["arms_back"]["dimensions_mm"]
        #components["arms_back"]["dimensions_mm"] = (old_dims[0], old_dims[1], arms_back_len * 1000)
        components["arms_back"]["dimensions_mm"] = (diameter_mm, thickness_mm, arms_back_len_mm)

        components["arms_back_v"]["x_cg"][0] = (x_arm, y_arm_v_upper, 19.65)
        components["arms_back_v"]["x_cg"][1] = (x_arm, y_arm_v_lower, 19.65)

        components["motor"]["x_cg"][2] = (x_arm, y_arm_v_upper, -9.2)
        components["motor"]["x_cg"][3] = (x_arm, y_arm_v_lower, -9.2)

        # Update weight dynamically
        delta_x = abs(x_arm + x_offset)
        delta_y = abs(y_arm_v_upper-59)
        rear_arm_len = np.sqrt(delta_x**2 + delta_y**2)
        r_outer = diameter_mm / 2
        r_inner = r_outer - thickness_mm
        if r_inner < 0:
            r_inner = 0  # prevent negative radius
        vol_per_arm = np.pi * (r_outer**2 - r_inner**2) * rear_arm_len  # in mm³
        mass_per_arm = density * vol_per_arm  # in kg
        components["arms_back"]["weight_g"] = mass_per_arm * 1000  # convert to grams


        cg, total_mass = compute_cg(components)
        rear_x_dists = [
            compute_x_distance(cg, (x_arm, y_arm_v_upper, 0)),
            compute_x_distance(cg, (x_arm, y_arm_v_lower, 0)),
        ]
        rear_x_dist = np.mean(rear_x_dists)
        

        if abs(rear_x_dist - front_x_dist) < tol:
            # Final rear arm length calculation based on actual geometry
            print(arms_back_len, rear_arm_len)
            print(f"Rear Distances: {rear_x_dists}, x position: {x_arm:.6f}, Front Distance: {front_x_dist:.6f}")
            return rear_arm_len, cg, total_mass

        scale = 1 - 0.5 * (rear_x_dist - front_x_dist)
        arms_back_len *= scale
    raise ValueError("Convergence not achieved")

    #return arms_back_len, cg

COMPONENTS = {
    "voyant_carbon": {                                      #Lidar
        "dimensions_mm": (42.0, 28.0, 44.0),
        "weight_g": 150.0,
        "quantity": 1,
        "x_cg": [(78, 0, 14)], #[(78, 6, 14)],
    },
    "herelink_1_1": {                                       #herelink controller
        "dimensions_mm": (78.5, 30.0, 15.0),
        "weight_g": 98.0,
        "quantity": 1,
        "x_cg": [(-18.58, 0, 106)],
    },
    # "seoul_viosys_cun66b1g_uv_led": {                       #UV Light   
    #     "dimensions_mm": (3.5 * 3, 3.5 * 3, 2.83),
    #     "weight_g": 0.44 * 9,
    #     "quantity": 1,
    #     "x_cg": [(1, 1, 1)],
    # },
    # "tof_ranging_sensor": {                                 #ToF Ranging Sensor
    #     "dimensions_mm": (19.0, 12.0, 10.3),
    #     "weight_g": 1.0,
    #     "quantity": 1,
    #     "x_cg": [(1, 1, 1)],
    # },
    "HCL-HP 22.2V 7600mAh 150C G10 ": {              #Battery Group
        "dimensions_mm": (46, 70, 160),
        "weight_g": 1065.0,                                                      
        "quantity": 1,
        "x_cg": [(-25.25, 0, 45)],
    },
    # "dc_dc_step_down_3_2_to_35v_2a": {                      #DC-DC Step Down Converter
    #     "dimensions_mm": (43.0, 20.0, 14.0),
    #     "weight_g": 12.0,
    #     "quantity": 1,
    #     "x_cg": [(1, 1, 1)],
    # },
    # "pcb": {
    #     "dimensions_mm": (20.5, 20.5, 4.0),
    #     "weight_g": 10.0,
    #     "quantity": 1,
    #     "x_cg": [(1, 1, 1)],
    # },
    # "cool_innovations_heatsink": {
    #     "dimensions_mm": (20.5, 20.5, 4.0),
    #     "weight_g": 15.0,
    #     "quantity": 1,
    #     "x_cg": [(1, 1, 1)],
    # },
    # "imx462_camera_module": {
    #     "dimensions_mm": (24.0, 25.0, 30.0),
    #     "weight_g": 9.0,
    #     "quantity": 1,
    #     "x_cg": [(1, 1, 1)],
    # },
    # "arducam_imx462_camera_module": {
    #     "dimensions_mm": (24.0, 25.0, 30.0),
    #     "weight_g": 9.0,
    #     "quantity": 1,
    #     "x_cg": [(1, 1, 1)],
    # },
    "cube_orange_body": {
        "dimensions_mm": (38.4, 22, 38.4),
        "weight_g": 73.0 * (38.4 * 38.4 * 22.0) / ((38.4 * 38.4 * 22.0) + (94.5 * 44.3 * 17.3)),
        "quantity": 1,
        "x_cg": [(11.075, 0, 108.3)],
    },
    "cube_orange_carrier": {
        "dimensions_mm": (94.5, 17.3, 44.3),
        "weight_g": 73.0 * (94.5 * 44.3 * 17.3) / ((38.4 * 38.4 * 22.0) + (94.5 * 44.3 * 17.3)),
        "quantity": 1,
        "x_cg": [(11.075, 0, 88.65)],
    },
    "orange_pi_5": {
        "dimensions_mm": (100, 62.0, 3),
        "weight_g": 46.0,
        "quantity": 1,
        "x_cg": [(0, 0, 3)],
    },
    # "propeller": {
    #     "dimensions_mm": (10.0, 10.0, 5.0),
    #     "weight_g": 4.0,
    #     "quantity": 4,
    #     "x_cg": [(1, 1, 1)],
    # },
    # "esc": {
    #     "dimensions_mm": (30.0, 20.0, 10.0),
    #     "weight_g": 15.0,
    #     "quantity": 4,
    #     "x_cg": [(1, 1, 1)] * 4,
    # },
    "motor": {
        "dimensions_mm": (36.0, 22.3),
        "weight_g": 88.3,
        "quantity": 4,
        "x_cg": [(137.34, -216.62, -9.2),
                 (137.34, 216.62, -9.2),
                 (-187.34, 214.64, -9.2),
                 (-187.34, -214.64, -9.2)],
    },
    "body": {
        "dimensions_mm": (118, 210.5, 79.3),
        "weight_g": 98,
        "quantity": 1,
        "x_cg": [(0, 0, 39.65)],
    },
    "body_2": {
        "dimensions_mm": (118, 74, 41),
        "weight_g": 22.08,
        "quantity": 1,
        "x_cg": [(0, 0, 100.5)],
    },
    "arms_front": {
        "dimensions_mm": (20, 1.5, 170),
        "weight_g": 26.533,
        "quantity": 2,
        "x_cg": [(105.50, -137.81, 39.65),
                 (105.50, 137.81, 39.65)],
    },
    "arms_back": {
        "dimensions_mm": (20, 1.5, 190),
        "weight_g": 29.654,
        "quantity": 2,
        "x_cg": [(-132.85, 136.82, 39.65),
                 (-132.85, -136.82, 39.65)],
    },
    "arms_front_v": {
        "dimensions_mm": (20, 1.5, 5),
        "weight_g": 0.780,
        "quantity": 2,
        "x_cg": [(137.34, -216.62, 19.65),
                 (137.34, 216.62, 19.65)],
    },
    "arms_back_v": {
        "dimensions_mm": (20, 1.5, 5),
        "weight_g": 0.780,
        "quantity": 2,
        "x_cg": [(-187.34, 214.64, 19.65),
                 (-187.34, -214.64, 19.65)],
    },
    "legs": {
        "dimensions_mm": (20, 1, 130),
        "weight_g": 16.4,
        "quantity": 4,
        "x_cg": [(-95.96, 93.36, 114.66),
                 (95.96, -93.36, 114.66),
                 (-95.96, 93.36, 114.66),
                 (-95.96, -93.36, 114.66)],
    },
}

def mm_to_m(dimensions_mm):
    return tuple(d / 1000.0 for d in dimensions_mm)

def g_to_kg(mass_g):
    return mass_g / 1000.0

def rotation_matrix_from_angles(component_name, index):
    if component_name == "legs":
        # Aligned along y, 45 deg to xy plane → rotate around y-axis by -45°
        angle = np.deg2rad(-45)
        return np.array([
            [np.cos(angle), 0, -np.sin(angle)],
            [0, 1, 0],
            [np.sin(angle), 0,  np.cos(angle)],
        ])
    elif component_name == "arms_front":
        angle = np.deg2rad(68)
        if index == 1:  # right side
            angle = -angle
        return np.array([
            [np.cos(angle), np.sin(angle), 0],
            [-np.sin(angle),  np.cos(angle), 0],
            [0, 0, 1],
        ])
    elif component_name == "arms_back":
        angle = np.deg2rad(55)
        if index == 1:
            angle = -angle
        return np.array([
            [np.cos(angle), np.sin(angle), 0],
            [-np.sin(angle),  np.cos(angle), 0],
            [0, 0, 1],
        ])
    else:
        return np.identity(3)

def compute_inertia_tensor_at_com(name, mass_kg, dims_m, index=0):
    if name == "motor":
        diameter, length = dims_m
        r = diameter / 2
        h = length
        I_xx = I_yy = (1/12) * mass_kg * (3 * r**2 + h**2)
        I_zz = (1/2) * mass_kg * r**2
        return np.diag([I_xx, I_yy, I_zz])

    elif name in ["arms_front", "arms_back", "legs"]:
        diameter, thickness, length = dims_m
        r_outer = diameter / 2
        r_inner = r_outer - thickness
        r_mean = (r_outer + r_inner) / 2
        h = length
        I_xx = I_yy = (1/12) * mass_kg * (3 * r_mean**2 + h**2)
        I_zz = mass_kg * r_mean**2
        I_tensor_local = np.diag([I_xx, I_yy, I_zz])
        R = rotation_matrix_from_angles(name, index)
        return R @ I_tensor_local @ R.T
    else:
        w, h, d = dims_m
        I_xx = (1/12) * mass_kg * (h**2 + w**2)
        I_yy = (1/12) * mass_kg * (h**2 + d**2)
        I_zz = (1/12) * mass_kg * (w**2 + d**2)
        return np.diag([I_xx, I_yy, I_zz])

def parallel_axis_theorem(I_com_matrix, mass_kg, r):
    # dx, dy, dz = r
    # r_vec = np.array([dx, dy, dz])
    r_vec = np.array(r)
    
    # Compute the parallel axis theorem
    d_squared = np.dot(r_vec, r_vec)                                                        #square distance between the two points
    I_parallel = mass_kg * (d_squared * np.identity(3) - np.outer(r_vec, r_vec))            #extra moment of inertia tensor
    I_total = I_com_matrix + I_parallel
    return {
        "I_xx": I_total[0, 0], "I_yy": I_total[1, 1], "I_zz": I_total[2, 2],
        "I_xy": -I_total[0, 1], "I_xz": -I_total[0, 2], "I_yz": -I_total[1, 2],
    }

# Run the loop and print final results
final_len, final_cg, final_total_mass = iterate_arm_length(COMPONENTS)
#print(f'here', COMPONENTS["arms_back"])
# Phase 2: Compute inertia tensors relative to total CoG
inertia_results = {}
total_inertia = {
    "I_xx": 0.0,
    "I_yy": 0.0,
    "I_zz": 0.0,
    "I_xy": 0.0,
    "I_xz": 0.0,
    "I_yz": 0.0,
}

for name, comp in COMPONENTS.items():
    dims_m = mm_to_m(comp["dimensions_mm"])
    mass_kg_unit = g_to_kg(comp["weight_g"])
    quantity = comp["quantity"]
    x_cgs = comp["x_cg"]

    for i in range(quantity):
        # x_cg = x_cgs[i]
        x_cg_mm = x_cgs[i]
        x_cg = tuple(coord / 1000.0 for coord in x_cg_mm)
        mass_kg = mass_kg_unit
        I_com = compute_inertia_tensor_at_com(name, mass_kg, dims_m, i)
        rel_pos = (
            x_cg[0] - final_cg[0],
            x_cg[1] - final_cg[1],
            x_cg[2] - final_cg[2],
        )
        tensor = parallel_axis_theorem(I_com, mass_kg, rel_pos)

        inertia_results[f"{name}_{i+1}"] = tensor
        for key in total_inertia:
            total_inertia[key] += tensor[key]

# print(f"\n✅ Final arm length: {final_len * 1000:.2f} mm")
# print(f"✅ Final CoG:")
# print(f"  x = {final_cg[0]:.6f} m")
# print(f"  y = {final_cg[1]:.6f} m")
# print(f"  z = {final_cg[2]:.6f} m")

# print("\n✅ Updated Component Positions (x_cg in mm):")
# for name, comp in COMPONENTS.items():
#     print(f"\n{name}:")
#     pprint(comp["x_cg"])

print("\n" + "="*50)
print("Total Mass (kg):", final_total_mass)
print("Total Center of Gravity (in meters):")
print(f"  x = {final_cg[0]:.6f} m")
print(f"  y = {final_cg[1]:.6f} m")
print(f"  z = {final_cg[2]:.6f} m")
print("="*50)

print("\n" + "="*50)
print("Total Mass Moment of Inertia (kg·m²) about Total CoG:")
print(f"  I_xx = {total_inertia['I_xx']:.6f}")
print(f"  I_yy = {total_inertia['I_yy']:.6f}")
print(f"  I_zz = {total_inertia['I_zz']:.6f}")
print(f"  I_xy = {total_inertia['I_xy']:.6f}")
print(f"  I_xz = {total_inertia['I_xz']:.6f}")
print(f"  I_yz = {total_inertia['I_yz']:.6f}")
print("="*50)