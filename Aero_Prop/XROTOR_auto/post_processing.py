import os
import re
import json
from pathlib import Path
from collections import deque

# === CONFIGURATION ===
PROJECT_ROOT = Path(__file__).parent.resolve()
RESULTS_DIR = PROJECT_ROOT / "Results"
OPTIMAL_DIR = PROJECT_ROOT / "Optimal_configs"
OPTIMAL_DIR.mkdir(parents=True, exist_ok=True)
TOP_N = 5

required_thrust = 2161 / 4 * 1.75 / 1000 * 9.81  # N
print(f"Required vertical thrust: {required_thrust:.2f} N")

# === PARSE FUNCTION ===
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
        result["ct"] = float(re.search(r"CT:\s*([\d.]+)", text).group(1))
        result["cp"] = float(re.search(r"CP:\s*([\d.]+)", text).group(1))
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

# === ANALYSIS SCRIPT ===
def analyze_results():
    best_configs = deque(maxlen=TOP_N)

    for file in RESULTS_DIR.glob("*.txt"):
        print(f"Processing: {file.name}")
        data = parse_output(file)
        if data is None:
            continue
        for tilt in [0]:
            # Extract config names from filename
            try:
                base = file.stem  # no .txt
                if base.endswith("duct"):
                    airfoil, prop, motor, motor_mass_raw, duct = base.split("_")
                    duct = True
                else:
                    airfoil, prop, motor, motor_mass_raw = base.split("_")
                    duct = False
                
                motor_mass_str = motor_mass_raw.replace("o", ".")
                motor_mass = float(motor_mass_str)
            except ValueError:
                print(f"Filename format invalid: {file.name}")
                continue


            # Vertical thrust with tilt
            vertical_thrust = data["thrust"] * math.cos(math.radians(tilt))

            # Minimum thrust constraint
            if vertical_thrust < required_thrust:
                continue
            if motor == str(3) or motor == str(5) or motor == str(9):
                continue

            ## === NPPS (Normalized Propeller Performance Score) ===
            power = data["power"] if data["power"] > 0 else 1e-6
            thrust_per_watt = data["thrust"] / power
            vertical_thrust_per_watt = vertical_thrust / power
            eff_induced = data.get("eff_induced", data["efficiency"])
            ct_sigma = data.get("ct", 0.0001) / 0.00408
            mach_tip = data.get("mach", 0.1)

            # === Blade element heuristics ===
            blade_elements = data.get("blade_elements", [])
            num_elements = len(blade_elements)

            # Defaults
            avg_effp = 0.0
            min_rR, max_rR = 0, 1
            avg_cR = 0.05

            if blade_elements:
                avg_effp = sum(be["effp"] for be in blade_elements) / num_elements
                rR_values = [be["r/R"] for be in blade_elements]
                cR_values = [be["c/R"] for be in blade_elements]
                min_rR = min(rR_values)
                max_rR = max(rR_values)
                avg_cR = sum(cR_values) / len(cR_values)

            # Penalize too few blade elements (poor resolution)
            element_penalty = 0.0
            if num_elements < 6:
                element_penalty += 0.1 * (6 - num_elements)

            # Penalize if blade elements are all bunched inboard (inefficient)
            r_span_penalty = 0.0
            if max_rR - min_rR < 0.5:
                r_span_penalty += 0.05

            # Penalize excessively thin blades
            thin_blade_penalty = 0.0
            if avg_cR < 0.02:
                thin_blade_penalty += 0.05

            # Total penalty from geometry
            geometry_penalty = element_penalty + r_span_penalty + thin_blade_penalty

            # === Final NPPS score ===
            score = (
                0.3 * vertical_thrust_per_watt +
                #0.3 * thrust_per_watt +
                0.3 * eff_induced +
                0.2 * ct_sigma +
                0.1 * avg_effp -  # reward for good spanwise efficiency
                0.1 * mach_tip -
                0.05 * motor_mass / 100 -
                geometry_penalty  # total geometry-based penalties
            )


            config = {
                "airfoil": airfoil,
                "motor": motor,
                "prop": prop,
                "ducted": duct,
                "tilt_deg": tilt,
                "vertical_thrust": vertical_thrust,
                "horizontal_thrust": data["thrust"] * math.sin(math.radians(tilt)),
                "power_draw_W": data["power"],
                "torque_Nm": data["torque"],
                "ct": data["ct"],
                "cp": data["cp"],
                "efficiency": data["efficiency"],
                "mach": data["mach"],
                "wake_advance_ratio": data["wake_advance_ratio"],
                "score": score,
            }

            best_configs.append(config)
            best_configs = deque(sorted(best_configs, key=lambda c: -c["score"]), maxlen=TOP_N)

    # Save top configs
    for i, config in enumerate(best_configs):
        with open(OPTIMAL_DIR / f"config_{i+1:03}.json", "w") as f:
            json.dump(config, f, indent=2)

    print(f"\nTop {TOP_N} configurations saved to {OPTIMAL_DIR}")

if __name__ == "__main__":
    import math
    analyze_results()
