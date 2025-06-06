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

# === ANALYSIS SCRIPT ===
def analyze_results():
    best_configs = deque(maxlen=TOP_N)

    for file in RESULTS_DIR.glob("*.txt"):
        print(f"Processing: {file.name}")
        data = parse_output(file)
        if data is None:
            continue
        for tilt in [0,15,30,45]:
            # Extract config names from filename
            try:
                base = file.stem  # no .txt
                airfoil, prop, motor, motor_mass = base.split("_")
                motor_mass = int(motor_mass)
            except ValueError:
                print(f"Filename format invalid: {file.name}")
                continue


            # Vertical thrust with tilt
            vertical_thrust = data["thrust"] * math.cos(math.radians(tilt))

            # Minimum thrust constraint
            if vertical_thrust < 4.3:
                continue

            # Score formula (tune as needed)
            score = (
                data["efficiency"] * 0.6 +
                data["ct"] * 0.3 -
                (data["power"] / 100) * 0.05 -
                motor_mass * 0.05
            )

            config = {
                "airfoil": airfoil,
                "motor": motor,
                "prop": prop,
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
