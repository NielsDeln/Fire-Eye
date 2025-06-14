import numpy as np
from pprint import pprint

COMPONENTS = {
    "voyant_carbon": {                                      #Lidar
        "dimensions_mm": (42.0, 28.0, 44.0),
        "weight_g": 150.0,
        "quantity": 1,
        "x_cg": [(6, 78,14)],
    },
    "herelink_1_1": {                                       #herelink controller
        "dimensions_mm": (78.5, 30.0, 15.0),
        "weight_g": 98.0,
        "quantity": 1,
        "x_cg": [(0, -18.58, 106)],
    # },
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
    },
    "HCL-HP 22.2V 7600mAh 150C G10 ": {              #Battery Group
        "dimensions_mm": (46, 70, 160),
        "weight_g": 1065.0,                                                      
        "quantity": 1,
        "x_cg": [(0, 21, 45)],
    # },
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
    },
    "cube_orange_body": {
        "dimensions_mm": (38.4, 22, 38.4),
        "weight_g": 73.0 * (38.4 * 38.4 * 22.0) / ((38.4 * 38.4 * 22.0) + (94.5 * 44.3 * 17.3)),
        "quantity": 1,
        "x_cg": [(0, 11.075, 108.3)],
    },
    "cube_orange_carrier": {
        "dimensions_mm": (94.5, 17.3, 44.3),
        "weight_g": 73.0 * (94.5 * 44.3 * 17.3) / ((38.4 * 38.4 * 22.0) + (94.5 * 44.3 * 17.3)),
        "quantity": 1,
        "x_cg": [(0, 11.075, 88.65)],
    },
    "orange_pi_5": {
        "dimensions_mm": (100, 62.0, 3),
        "weight_g": 46.0,
        "quantity": 1,
        "x_cg": [(0, 0, 3)],
    # },
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
    },
    "motor": {
        "dimensions_mm": (28.0, 14.0),
        "weight_g": 88.3,
        "quantity": 4,
        "x_cg": [(216.62, 137.34, 39.65),
                 (-216.62, 137.34, 39.65),
                 (214.64, -187.34, 39.65),
                 (-214.64, -187.34, 39.65)],
    },
    "body": {
        "dimensions_mm": (118, 210.5, 79.3),
        "weight_g": 107.81,
        "quantity": 1,
        "x_cg": [(0, 0, 39.65)],
    },
    "body_2": {
        "dimensions_mm": (118, 74, 41),
        "weight_g": 24.30,
        "quantity": 1,
        "x_cg": [(0, 0, 100.5)],
    },
    "arms_front": {
        "dimensions_mm": (20, 1, 170),
        "weight_g": 15.4,
        "quantity": 2,
        "x_cg": [(137.81, 105.50, 39.65),
                 (-137.81, 105.50, 39.65)],
    },
    "arms_back": {
        "dimensions_mm": (20, 1, 190),
        "weight_g": 15.4,
        "quantity": 2,
        "x_cg": [(136.82, -132.85, 39.65),
                 (-136.82, -132.85, 39.65)],
    },
    "legs": {
        "dimensions_mm": (20, 2, 100),
        "weight_g": 15.8,
        "quantity": 4,
        "x_cg": [(93.36, 95.96, 114.66),
                 (-93.36, 95.96, 114.66),
                 (93.36, -95.96, 114.66),
                 (-93.36, -95.96, 114.66)],
    },
}

def mm_to_m(dimensions_mm):
    return tuple(d / 1000.0 for d in dimensions_mm)

def g_to_kg(mass_g):
    return mass_g / 1000.0

def rotation_matrix_from_angles(component_name, index):
    if component_name == "legs":
        # Aligned along x, 45 deg to xy plane → rotate around y-axis by -45°
        angle = np.deg2rad(-45)
        return np.array([
            [1, 0, 0],
            [0, np.cos(angle), -np.sin(angle)],
            [0, np.sin(angle),  np.cos(angle)],
        ])
    elif component_name == "arms_front":
        angle = np.deg2rad(68)
        if index == 1:  # right side
            angle = -angle
        return np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle),  np.cos(angle), 0],
            [0, 0, 1],
        ])
    elif component_name == "arms_back":
        angle = np.deg2rad(55)
        if index == 1:
            angle = -angle
        return np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle),  np.cos(angle), 0],
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
        I_xx = (1/12) * mass_kg * (h**2 + d**2)
        I_yy = (1/12) * mass_kg * (w**2 + d**2)
        I_zz = (1/12) * mass_kg * (w**2 + h**2)
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

# Phase 1: Compute total center of gravity
total_mass = 0.0
weighted_sum_x = 0.0
weighted_sum_y = 0.0
weighted_sum_z = 0.0

for name, comp in COMPONENTS.items():
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
            x_cg[0] - x_cg_total[0],
            x_cg[1] - x_cg_total[1],
            x_cg[2] - x_cg_total[2],
        )
        tensor = parallel_axis_theorem(I_com, mass_kg, rel_pos)

        inertia_results[f"{name}_{i+1}"] = tensor
        for key in total_inertia:
            total_inertia[key] += tensor[key]

print("\n" + "="*50)
print("Total Center of Gravity (in meters):")
print(f"  x = {x_cg_total[0]:.4f} m")
print(f"  y = {x_cg_total[1]:.4f} m")
print(f"  z = {x_cg_total[2]:.4f} m")
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