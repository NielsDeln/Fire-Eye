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
    return x_cg_total

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

    cg = compute_cg(components)

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
        r_outer = diameter_mm / 2
        r_inner = r_outer - thickness_mm
        if r_inner < 0:
            r_inner = 0  # prevent negative radius
        vol_per_arm = np.pi * (r_outer**2 - r_inner**2) * arms_back_len_mm  # in mm³
        mass_per_arm = density * vol_per_arm  # in kg
        components["arms_back"]["weight_g"] = mass_per_arm * 1000  # convert to grams


        cg = compute_cg(components)
        rear_x_dists = [
            compute_x_distance(cg, (x_arm, y_arm_v_upper, 0)),
            compute_x_distance(cg, (x_arm, y_arm_v_lower, 0)),
        ]
        rear_x_dist = np.mean(rear_x_dists)
        

        if abs(rear_x_dist - front_x_dist) < tol:
            # Final rear arm length calculation based on actual geometry
            delta_x = abs(x_arm + x_offset)/ 1000
            delta_y = abs(y_arm_v_upper-59)/ 1000
            final_rear_arm_len = np.sqrt(delta_x**2 + delta_y**2) 
            print(arms_back_len, final_rear_arm_len)
            print(f"Rear Distances: {rear_x_dists}, x position: {x_arm:.6f}, Front Distance: {front_x_dist:.6f}")
            return final_rear_arm_len, cg

        scale = 1 - 0.5 * (rear_x_dist - front_x_dist)
        arms_back_len *= scale
        print(rear_x_dist - front_x_dist, arms_back_len)
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
        "dimensions_mm": (20, 1, 100),
        "weight_g": 15.8,
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

# Run the loop and print final results
final_len, final_cg = iterate_arm_length(COMPONENTS)

print(f"\n✅ Final arm length: {final_len * 1000:.2f} mm")
print(f"✅ Final CoG:")
print(f"  x = {final_cg[0]:.6f} m")
print(f"  y = {final_cg[1]:.6f} m")
print(f"  z = {final_cg[2]:.6f} m")

print("\n✅ Updated Component Positions (x_cg in mm):")
for name, comp in COMPONENTS.items():
    print(f"\n{name}:")
    pprint(comp["x_cg"])
