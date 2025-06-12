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
    "propeller": {
        "dimensions_mm": (10.0, 10.0, 5.0),  # diameter, width, height
        "weight_g": 4.0,
        "quantity": 4,
        "x_cg": [(1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1)],
    },
    #esc
    "esc": {
        "dimensions_mm": (30.0, 20.0, 10.0),  # length, width, height
        "weight_g": 15.0,
        "quantity": 4,
        "x_cg": [(1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1)],
    },
    "motor": {
        "dimensions_mm": (28.0, 28.0, 30.0),  # diameter, width, height
        "weight_g": 50.0,
        "quantity": 4,
        "x_cg": [(1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1)],
    },
    "frame": {
        "dimensions_mm": (450.0, 450.0, 10.0),  # length, width, height
        "weight_g": 500.0,
        "quantity": 1,
        "x_cg": [(1, 1, 1)],
    },
}

# Convert dimensions from mm to m and mass from g to kg
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



