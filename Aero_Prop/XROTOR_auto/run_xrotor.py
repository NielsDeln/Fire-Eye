import subprocess
import math
import os
import hashlib
import re
from pathlib import Path
from collections import deque
import json
import numpy as np
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


"""OPTIMAL:
for prop in props:
    for motor in motors:
        for voltage in allowed_voltages(motor):
            rpm = motor["kv"] * voltage
            for tilt_angle in tilt_configs:
                run_xrotor_with(rpm, prop)
                get_thrust_and_power()

                # project thrust based on tilt
                T_v = T_total * cos(tilt)
                T_h = T_total * sin(tilt)
                score = (T_v / power) + (T_h / power) * cruise_weight

                if score > best[regime]:
                    save_optimal_config()


"""



"""LOAD DATA"""

PROJECT_ROOT = Path(__file__).parent.resolve()
AIRFOIL_DIR = PROJECT_ROOT / "airfoils"
PROP_DIR = PROJECT_ROOT / "propellers"
MOTOR_DIR = PROJECT_ROOT / "motors"
RESULTS_DIR = PROJECT_ROOT / "Results"
OPTIMAL_DIR = RESULTS_DIR / "optimal_configs"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OPTIMAL_DIR.mkdir(parents=True, exist_ok=True)

with open('tilt_configs.json') as f:
    tilt_angles = json.load(f)

TOP_N = 5


"""Flight regimes"""
flight_modes = {
    "hover": {"weight": 1.0, "cruise_weight": 0.0},
    "cruise": {"weight": 0.5, "cruise_weight": 0.5},
    "max_load": {"weight": 0.8, "cruise_weight": 0.2}
} # TO BE SEEN IF ILL USE THESE, VALUES ARE NOW BS

#best_configs = best_configs = {mode: {"score": -1e9} for mode in flight_modes}
top_results = []


"""FUNCTIONS TO USE"""
# Load databases
def load_json_files_from_folder(folder):
    return [json.load(open(folder / f)) for f in os.listdir(folder) if f.endswith(".json")]

def load_airfoils():
    return [f for f in os.listdir(AIRFOIL_DIR) if f.endswith(".pol")]

# for Optimization
def compute_rpm(motor, voltage):
    return motor["kv"] * voltage

def compute_thrust_components(thrust, tilt_deg):
    tilt_rad = math.radians(tilt_deg)
    return {
        "vertical": thrust * math.cos(tilt_rad),
        "horizontal": thrust * math.sin(tilt_rad)
    }

# To run XROTOR
def generate_input_file(airfoil, motor, prop, tilt, voltage, rpm, file_path):
    with open(file_path, "w") as f:
        f.write(f"aero\n")
        f.write(f"read {AIRFOIL_DIR / airfoil}\n") # change airfoil first
        f.write("desi\n") # start input propeller
        f.write("inpu\n")
        f.write(f"B {prop['blades']}\n")
        f.write(f"RT {prop['diameter_m']/2:.4f}\n")
        f.write(f"RH {prop['hub_diameter_m']/2:.4f}\n")
        f.write(f"RW {prop['hub_wake displacement_body_radius']:.4f}\n")
        f.write(f"V 10.0\n") # AIRSPEED TO BE CHANGED
        f.write(f"A 0\n")
        f.write(f"RPM {rpm:.1f}\n")
        f.write(f"T 0\n")
        f.write(f"P {motor['power']:.1f}\n")
        f.write(f"CC 0.6\n") # balanced for moderate thrust & efficiency
        f.write(f"\n")  # trigger design
        f.write(f"\n") # Enter twice
        f.write("oper\n")
        f.write("velo 10.0\n") # AIRSPEED TO BE CHANGED
        f.write(f"rpm {rpm:.1f}\n")
        f.write("disp\n")
        f.write("addc\n")
        f.write("disp\n")
        # ADD VELO THIMNG UUUUUUGHGHGHHG
        f.write(f"writ {RESULTS_DIR / f'{airfoil}_{motor['name']}_{prop['name']}_{tilt}.txt'}\n")
        f.write("quit\n")

def run_xrotor(input_file):
    result = subprocess.run(f"xrotor < {input_file}", shell=True, capture_output=True, text=True)
    return result.stdout


def parse_output(output_path):
    with open(output_path, "r") as f:
        text = f.read()

    result = {}
    try:
        # Main block
        result["wake_advance_ratio"] = float(re.search(r"Wake adv\. ratio:\s+([\d.]+)", text).group(1))
        result["advance_ratio"] = float(re.search(r"adv\. ratio:\s+([\d.]+)", text).group(1))
        result["thrust"] = float(re.search(r"thrust\(N\)\s*:\s*([\d.+-]+)", text).group(1))
        result["power"] = float(re.search(r"power\(W\)\s*:\s*([\d.+-]+)", text).group(1))
        result["torque"] = float(re.search(r"torque\(N-m\):\s*([\d.+-]+)", text).group(1))
        result["efficiency"] = float(re.search(r"Efficiency\s*:\s*([\d.]+)", text).group(1))
        result["ct"] = float(re.search(r"Ct:\s*([\d.]+)", text).group(1))
        result["cp"] = float(re.search(r"Cp:\s*([\d.]+)", text).group(1))
        result["mach"] = float(re.search(r"Mach\s*:\s*([\d.]+)", text).group(1))

        # Optional: grab table lines (for spanwise efficiency, etc.)
        result["blade_elements"] = []
        table_started = False
        for line in text.splitlines():
            if re.match(r"\s*i\s+r/R\s+c/R", line):
                table_started = True
                continue
            if table_started:
                if re.match(r"\s*\d+\s", line):
                    parts = line.split()
                    if len(parts) >= 11:
                        result["blade_elements"].append({
                            "r/R": float(parts[1]),
                            "c/R": float(parts[2]),
                            "beta": float(parts[3]),
                            "CL": float(parts[4]),
                            "Cd": float(parts[5]),
                            "Re": float(parts[6]),
                            "Mach": float(parts[7]),
                            "effi": float(parts[8]),
                            "effp": float(parts[9])
                        })
                else:
                    break
    except Exception as e:
        print("Failed to parse output:", e)

    return result

def hash_config(a, m, p, tilt, v):
    raw = f"{a}_{m['name']}_{p['name']}_{tilt}_{v}"
    return hashlib.md5(raw.encode()).hexdigest()



"""MAIN SWEEP YAY"""
def main():
    motors = load_json_files_from_folder(MOTOR_DIR)
    props = load_json_files_from_folder(PROP_DIR)
    airfoils = load_airfoils()

    tested = set()
    best_configs = deque(maxlen=TOP_N)

    for airfoil in airfoils:
        for motor in motors:
            for prop in props:
                for tilt in tilt_angles:
                    for voltage in [12.0, 14.8, motor["max_voltage"]]: #12.0V → common for 3S LiPo, 14.8V → common for 4S LiPo
                        rpm = compute_rpm(motor, voltage)
                        cfg_hash = hash_config(airfoil, motor, prop, tilt, voltage)
                        if cfg_hash in tested:
                            continue
                        tested.add(cfg_hash)

                        input_file = PROJECT_ROOT / "xrotor.in"
                        generate_input_file(airfoil, motor, prop, tilt, voltage, rpm, input_file)
                        run_xrotor(input_file)

                        output_file = RESULTS_DIR / f"{airfoil}_{motor['name']}_{prop['name']}_{tilt}.txt"
                        result = parse_output(output_file)

                        thrusts = compute_thrust_components(result["thrust"], tilt)
                        motor_mass = motor.get("mass", 0.1)  # avoid divide-by-zero
                        efficiency = result["efficiency"]

                        if thrusts["vertical"] < 2.5: # Require minimum thrust (TO BE CHANGED)
                            continue

                        # Multi-factor score
                        # EFF_WEIGHT = 0.6
                        # CT_WEIGHT = 0.3
                        # POWER_PENALTY = 0.05  # per 100W
                        # MASS_PENALTY = 0.05   # per kg (or per your motor mass unit)

                        score = (
                            efficiency * 0.6
                            + result["ct"] * 0.3
                            - (result["power"] / 100) * 0.05
                            - motor_mass * 0.05
                        )

                        config = {
                            "airfoil": airfoil,
                            "motor": motor["name"],
                            "prop": prop["name"],
                            "rpm": rpm,
                            "voltage": voltage,
                            "tilt_deg": tilt,
                            "vertical_thrust": thrusts["vertical"],
                            "horizontal_thrust": thrusts["horizontal"],
                            "power_draw_W": result["power"],
                            "torque_Nm": result["torque"],
                            "ct": result["ct"],
                            "cp": result["cp"],
                            "efficiency": result["efficiency"],
                            "mach": result["mach"],
                            "wake_advance_ratio": result["wake_advance_ratio"],
                            "score": score,
                            "blade_elements": result.get("blade_elements", [])
                        }


                        best_configs.append(config)
                        best_configs = deque(sorted(best_configs, key=lambda c: -c["score"]), maxlen=TOP_N)



    for i, config in enumerate(best_configs):     # Save best configs
        with open(OPTIMAL_DIR / f"config_{i+1:03}.json", "w") as f:
            json.dump(config, f, indent=2)

if __name__ == "__main__":
    main()

