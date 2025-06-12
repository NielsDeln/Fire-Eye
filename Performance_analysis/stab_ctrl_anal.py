import numpy as np
import structures_anal as stru
import propulsion_anal as prop

# create moment of inertia of the quadcopter
# components.py
# Define dimensions (in mm) and weights (in g) and xcg in 3D (x,y,z) for each component.
# These constants can be used for moment of inertia calculations later.

COMPONENTS = {
    "voyant_carbon": {
        "dimensions_mm": (42.0, 28.0, 44.0),  # (length, width, height)
        "weight_g": 150.0,
        "quantity": 1,
        "x_cg": [(1, 1, 1)],
    },
    "herelink_1_1": {
        "dimensions_mm": (78.5, 30.0, 15.0),
        "weight_g": 98.0,
        "quantity": 1,
        "x_cg": [(1, 1, 1)],
    },
    "seoul_viosys_cun66b1g_uv_led": {
    # 3x3 array: assume 3 in X, 3 in Y direction
        "dimensions_mm": (3.5 * 3, 3.5 * 3, 2.83),  # 10.5mm x 10.5mm x 2.83mm
        "weight_g": 0.44 * 9,  # total mass
        "quantity": 1,
        "x_cg": [(1, 1, 1)],  # list of CoMs for uniformity
    },
    "tof_ranging_sensor": {
        "dimensions_mm": (19.0, 12.0, 10.3),
        "weight_g": 1.0,
        "quantity": 1,
        "x_cg": [(1, 1, 1)],
    },
    "battery_grp_b042104": {
        "dimensions_mm": (103.5, 41.5, 10.7),
        "weight_g": 102.0,
        "quantity": 2,
        "x_cg": [(1,1,1), (1,1,1)],
    },
    "dc_dc_step_down_3_2_to_35v_2a": {
        "dimensions_mm": (43.0, 20.0, 14.0),
        "weight_g": 12.0,
        "quantity": 1,
        "x_cg": [(1, 1, 1)],
    },
    "pcb": {
        "dimensions_mm": (20.5, 20.5, 4.0),
        "weight_g": 10.0,
        "quantity": 1,
        "x_cg": [(1, 1, 1)],
    },
    "cool_innovations_heatsink": {
        # Splayed heatsink: fins base (20.5×20.5×4 mm)
        # (Ignoring larger base/top footprints for moment calculations)
        "dimensions_mm": (20.5, 20.5, 4.0),
        "weight_g": 15.0,
        "quantity": 1,
        "x_cg": [(1, 1, 1)],
    },
    "imx462_camera_module": {
        "dimensions_mm": (24.0, 25.0, 30.0),
        "weight_g": 9.0,
        "quantity": 1,
        "x_cg": [(1, 1, 1)],
    },
    "arducam_imx462_camera_module": {
        "dimensions_mm": (24.0, 25.0, 30.0),
        "weight_g": 9.0,
        "quantity": 1,
        "x_cg": [(1, 1, 1)],
    },
    "cube_orange_body": {
        "dimensions_mm": (38.4, 38.4, 22.0),
        "weight_g": 73.0 * (38.4 * 38.4 * 22.0) / ((38.4 * 38.4 * 22.0) + (94.5 * 44.3 * 17.3)),  # estimated split
        "quantity": 1,
        "x_cg": [(1, 1, 1)],
    },
    "cube_orange_carrier": {
        "dimensions_mm": (94.5, 44.3, 17.3),
        "weight_g": 73.0 * (94.5 * 44.3 * 17.3) / ((38.4 * 38.4 * 22.0) + (94.5 * 44.3 * 17.3)),
        "quantity": 1,
        "x_cg": [(1, 1, 1)],
    },

    "orange_pi_5": {
        "dimensions_mm": (62.0, 100.0, 10.0),  # approximate thickness = 10 mm
        "weight_g": 46.0,
        "quantity": 1,
        "x_cg": [(1, 1, 1)],
    },
}

# For convenience, create per‐component constants at the top level:

# Voyant Carbon
VOYANT_CARBON_DIMS_MM = COMPONENTS["voyant_carbon"]["dimensions_mm"]
VOYANT_CARBON_WEIGHT_G = COMPONENTS["voyant_carbon"]["weight_g"]
VOYANT_CARBON_QTY = COMPONENTS["voyant_carbon"]["quantity"]
VOYANT_CARBON_XCG = COMPONENTS["voyant_carbon"]["x_cg"]

# Herelink 1.1
HERELINK_1_1_DIMS_MM = COMPONENTS["herelink_1_1"]["dimensions_mm"]
HERELINK_1_1_WEIGHT_G = COMPONENTS["herelink_1_1"]["weight_g"]
HERELINK_1_1_QTY = COMPONENTS["herelink_1_1"]["quantity"]
HERELINK_1_1_XCG = COMPONENTS["herelink_1_1"]["x_cg"]

# Seoul Viosys UV LEDs
SEOUL_VIOSYS_LED_DIMS_MM = COMPONENTS["seoul_viosys_cun66b1g_uv_led"]["dimensions_mm"]
SEOUL_VIOSYS_LED_WEIGHT_G = COMPONENTS["seoul_viosys_cun66b1g_uv_led"]["weight_g"]
SEOUL_VIOSYS_LED_QTY = COMPONENTS["seoul_viosys_cun66b1g_uv_led"]["quantity"]
SEOUL_VIOSYS_LED_XCG = COMPONENTS["seoul_viosys_cun66b1g_uv_led"]["x_cg"]

# ToF Ranging Sensor
TOF_SENSOR_DIMS_MM = COMPONENTS["tof_ranging_sensor"]["dimensions_mm"]
TOF_SENSOR_WEIGHT_G = COMPONENTS["tof_ranging_sensor"]["weight_g"]
TOF_SENSOR_QTY = COMPONENTS["tof_ranging_sensor"]["quantity"]
TOF_SENSOR_XCG = COMPONENTS["tof_ranging_sensor"]["x_cg"]

# Battery GRPB042104
BATTERY_GRPB042104_DIMS_MM = COMPONENTS["battery_grp_b042104"]["dimensions_mm"]
BATTERY_GRPB042104_WEIGHT_G = COMPONENTS["battery_grp_b042104"]["weight_g"]
BATTERY_GRPB042104_QTY = COMPONENTS["battery_grp_b042104"]["quantity"]
BATTERY_GRPB042104_XCG = COMPONENTS["battery_grp_b042104"]["x_cg"]

# DC-DC Step‐Down Converter
DC_DC_STEP_DOWN_DIMS_MM = COMPONENTS["dc_dc_step_down_3_2_to_35v_2a"]["dimensions_mm"]
DC_DC_STEP_DOWN_WEIGHT_G = COMPONENTS["dc_dc_step_down_3_2_to_35v_2a"]["weight_g"]
DC_DC_STEP_DOWN_QTY = COMPONENTS["dc_dc_step_down_3_2_to_35v_2a"]["quantity"]
DC_DC_STEP_DOWN_XCG = COMPONENTS["dc_dc_step_down_3_2_to_35v_2a"]["x_cg"]

# PCB
PCB_DIMS_MM = COMPONENTS["pcb"]["dimensions_mm"]
PCB_WEIGHT_G = COMPONENTS["pcb"]["weight_g"]
PCB_QTY = COMPONENTS["pcb"]["quantity"]
PCB_XCG = COMPONENTS["pcb"]["x_cg"]

# Heatsink
HEATSINK_DIMS_MM = COMPONENTS["cool_innovations_heatsink"]["dimensions_mm"]
HEATSINK_WEIGHT_G = COMPONENTS["cool_innovations_heatsink"]["weight_g"]
HEATSINK_QTY = COMPONENTS["cool_innovations_heatsink"]["quantity"]
HEATSINK_XCG = COMPONENTS["cool_innovations_heatsink"]["x_cg"]

# IMX462 Camera
IMX462_CAMERA_DIMS_MM = COMPONENTS["imx462_camera_module"]["dimensions_mm"]
IMX462_CAMERA_WEIGHT_G = COMPONENTS["imx462_camera_module"]["weight_g"]
IMX462_CAMERA_QTY = COMPONENTS["imx462_camera_module"]["quantity"]
IMX462_CAMERA_XCG = COMPONENTS["imx462_camera_module"]["x_cg"]

# Arducam IMX462 Camera
ARDUCAM_CAMERA_DIMS_MM = COMPONENTS["arducam_imx462_camera_module"]["dimensions_mm"]
ARDUCAM_CAMERA_WEIGHT_G = COMPONENTS["arducam_imx462_camera_module"]["weight_g"]
ARDUCAM_CAMERA_QTY = COMPONENTS["arducam_imx462_camera_module"]["quantity"]
ARDUCAM_CAMERA_XCG = COMPONENTS["arducam_imx462_camera_module"]["x_cg"]


# Orange Pi 5
ORANGE_PI_5_DIMS_MM = COMPONENTS["orange_pi_5"]["dimensions_mm"]
ORANGE_PI_5_WEIGHT_G = COMPONENTS["orange_pi_5"]["weight_g"]
ORANGE_PI_5_QTY = COMPONENTS["orange_pi_5"]["quantity"]
ORANGE_PI_5_XCG = COMPONENTS["orange_pi_5"]["x_cg"]


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

# Calculate MMOI for all components
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

    # Make sure x_cg is a list of tuples (one per quantity)
    if quantity == 1 and isinstance(x_cgs, tuple):
        x_cgs = [x_cgs]
    elif quantity > 1 and (not isinstance(x_cgs, list) or len(x_cgs) != quantity):
        raise ValueError(f"{name}: x_cg should be a list of length {quantity}")

    for i in range(quantity):
        mass_kg = mass_kg_unit
        x_cg = x_cgs[i]
        I_com = compute_inertia_tensor_at_com(mass_kg, dims_m)
        tensor = parallel_axis_theorem(I_com, mass_kg, x_cg)

        inertia_results[f"{name}_{i+1}"] = tensor

        # Sum into total inertia
        total_inertia["I_xx"] += tensor["I_xx"]
        total_inertia["I_yy"] += tensor["I_yy"]
        total_inertia["I_zz"] += tensor["I_zz"]
        total_inertia["I_xy"] += tensor["I_xy"]
        total_inertia["I_xz"] += tensor["I_xz"]
        total_inertia["I_yz"] += tensor["I_yz"]

print("Individual component moments of inertia:")
print(inertia_results)
print("\nTotal Mass Moment of Inertia (kg·m²):")
print(total_inertia)



