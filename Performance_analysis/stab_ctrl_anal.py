import numpy as np
import structures_anal as stru
import propulsion_anal as prop

COMPONENTS = {
    "voyant_carbon": {                                      #Lidar
        "dimensions_mm": (42.0, 28.0, 44.0),
        "weight_g": 150.0,
        "quantity": 1,
        "x_cg": [(-2.37, 91.86,-51.20)],
    },
    "herelink_1_1": {                                       #herelink controller
        "dimensions_mm": (78.5, 30.0, 15.0),
        "weight_g": 98.0,
        "quantity": 1,
        "x_cg": [(-0.06, -52.87, 82.53)],
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
        "dimensions_mm": (46, 160, 70),
        "weight_g": 1065.0,                                                      
        "quantity": 1,
        "x_cg": [(0, 35, 31.74)],
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
        "dimensions_mm": (38.4, 38.4, 22.0),
        "weight_g": 73.0 * (38.4 * 38.4 * 22.0) / ((38.4 * 38.4 * 22.0) + (94.5 * 44.3 * 17.3)),
        "quantity": 1,
        "x_cg": [(1.29, -36.91, 0.67)],
    },
    "cube_orange_carrier": {
        "dimensions_mm": (94.5, 44.3, 17.3),
        "weight_g": 73.0 * (94.5 * 44.3 * 17.3) / ((38.4 * 38.4 * 22.0) + (94.5 * 44.3 * 17.3)),
        "quantity": 1,
        "x_cg": [(1.29, -56.56, 0.67)],
    },
    "orange_pi_5": {
        "dimensions_mm": (62.0, 100.0, 10.0),
        "weight_g": 46.0,
        "quantity": 1,
        "x_cg": [(1.23, 21.68, -70)],
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
        "x_cg": [(215.84, 191.74, 15.79), 
                 (-215.84, 191.74, 15.79), 
                 (213.86, -197.5, 15.79), 
                 (-213.86, -197.5, 15.79)],
    },
    "body": {
        "dimensions_mm": (119, 172, 179),
        "weight_g": 95,
        "quantity": 1,
        "x_cg": [(-1.16, -2.34, 9.5)],
    },
    "arms_front": {
        "dimensions_mm": (20, 1, 170),
        "weight_g": 15.4,
        "quantity": 2,
        "x_cg": [(137.03, 159.89, 15.80),
                 (-137.03, 159.89, 15.80)],
    },
    "arms_back": {
        "dimensions_mm": (20, 1, 190),
        "weight_g": 15.4,
        "quantity": 2,
        "x_cg": [(136.04, -143.0, 15.80)
                 (-136.04, -143.0, 15.80)],
    },
    "legs": {
        "dimensions_mm": (20, 2, 100),
        "weight_g": 15.8,
        "quantity": 4,
        "x_cg": [(93.57, 128.05, 99),
                 (-93.57, 128.05, 99),
                 (93.57, -88.51, 99),
                 (-93.57, -88.51, 99)],
    },
}

def mm_to_m(dimensions_mm):
    return tuple(d / 1000.0 for d in dimensions_mm)

def g_to_kg(mass_g):
    return mass_g / 1000.0

def compute_inertia_tensor_at_com(mass_kg, dims_m):
    w, h, d = dims_m
    I_xx = (1/12) * mass_kg * (h**2 + d**2)
    I_yy = (1/12) * mass_kg * (w**2 + d**2)
    I_zz = (1/12) * mass_kg * (w**2 + h**2)
    return I_xx, I_yy, I_zz

def parallel_axis_theorem(I_com, mass_kg, r):
    dx, dy, dz = r
    dx2, dy2, dz2 = dx**2, dy**2, dz**2
    I_xx = I_com[0] + mass_kg * (dy2 + dz2)
    I_yy = I_com[1] + mass_kg * (dx2 + dz2)
    I_zz = I_com[2] + mass_kg * (dx2 + dy2)
    I_xy = -mass_kg * dx * dy
    I_xz = -mass_kg * dx * dz
    I_yz = -mass_kg * dy * dz
    return {
        "I_xx": I_xx, "I_yy": I_yy, "I_zz": I_zz,
        "I_xy": I_xy, "I_xz": I_xz, "I_yz": I_yz,
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

    if quantity == 1 and isinstance(x_cgs, tuple):
        x_cgs = [x_cgs]
    elif quantity > 1 and (not isinstance(x_cgs, list) or len(x_cgs) != quantity):
        raise ValueError(f"{name}: x_cg should be a list of length {quantity}")

    for i in range(quantity):
        x_cg = x_cgs[i]
        total_mass += mass_kg_unit
        weighted_sum_x += mass_kg_unit * x_cg[0]
        weighted_sum_y += mass_kg_unit * x_cg[1]
        weighted_sum_z += mass_kg_unit * x_cg[2]

x_cg_total = (
    weighted_sum_x / total_mass,
    weighted_sum_y / total_mass,
    weighted_sum_z / total_mass,
)

print("\nTotal center of gravity (x, y, z) in meters:")
print(x_cg_total)

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
        mass_kg = mass_kg_unit
        x_cg = x_cgs[i]
        I_com = compute_inertia_tensor_at_com(mass_kg, dims_m)
        rel_pos = (
            x_cg[0] - x_cg_total[0],
            x_cg[1] - x_cg_total[1],
            x_cg[2] - x_cg_total[2],
        )
        tensor = parallel_axis_theorem(I_com, mass_kg, rel_pos)

        inertia_results[f"{name}_{i+1}"] = tensor

        total_inertia["I_xx"] += tensor["I_xx"]
        total_inertia["I_yy"] += tensor["I_yy"]
        total_inertia["I_zz"] += tensor["I_zz"]
        total_inertia["I_xy"] += tensor["I_xy"]
        total_inertia["I_xz"] += tensor["I_xz"]
        total_inertia["I_yz"] += tensor["I_yz"]

print("\nIndividual component moments of inertia:")
print(inertia_results)
print("\nTotal Mass Moment of Inertia (kg·m²) about the total CoG:")
print(total_inertia)
