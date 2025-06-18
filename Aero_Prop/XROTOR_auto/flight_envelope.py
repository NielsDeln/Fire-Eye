import numpy as np

# === Battery parameters ===
V_batt = 22.2
C_batt_ah = 7.6
C_batt_mah = C_batt_ah * 1000
Wh_batt = V_batt * C_batt_ah

# === Motor power ===
motor_power_avg = 342.4 * 4  # W for 4 motors

def throttle_for_tw_ratio(calibrated_tw, calibrated_throttle, target_tw):
    return calibrated_throttle * (target_tw / calibrated_tw) ** 0.5

calibrated_throttle = 0.80
calibrated_tw = 2.25
desired_tw = 1.0
required_throttle = throttle_for_tw_ratio(calibrated_tw, calibrated_throttle, desired_tw)
hover_power = 123 * 4 # this is the reading for 55% throttle which is enough to provide 1 T/W

# === Phase 1 (Entry, Max Thrust) ===
t_phase1 = 90 # seconds
P_phase1 = motor_power_avg + 4+0.1+0.25+1+5+5
print(P_phase1, "phase1 power")
e_phase1_total = (P_phase1 * t_phase1) / 3600  # Wh
print(e_phase1_total)

# === Phase 4 (Exit, same as Entry) ===
t_phase4 = 60  # seconds
P_phase4 = P_phase1
e_phase4_total = (P_phase4 * t_phase4) / 3600  # Wh
print(e_phase4_total)

# === Electronics power draw ===
P_mapping = {
    "Voyant Helium": 27,
    "Herelink 1.1": 4,
    "ToF Sensor": 0.1 + 0.25,
    "DC-DC Converter": 0.1,
    "Arducam 1": 0.99,
    "Cube Orange+": 5,
    "Orange Pi 5": 5,
}
P_total_mapping = sum(P_mapping.values())

# === Phase 2: Mapping ===
print("\n=== Phase 2: Mapping ===")
speed_mapping = 1.0  # m/s
e_remaining_map = Wh_batt - (e_phase1_total + e_phase4_total)
power_map = hover_power + P_total_mapping
t_phase2 = (e_remaining_map * 3600) / power_map
area_map = t_phase2 * speed_mapping * 2
total_time_map = t_phase1 + t_phase2 + t_phase4

print(f"Max Time: {t_phase2:.3f} s = {(t_phase2/60):.2f} minutes")
print(f"Total Mapping Mission Time: {total_time_map:.3f} s = {(total_time_map/60):.2f} minutes")
print(f"Ground Area Covered: {area_map:.1f} m^2. Coverage rate: {speed_mapping*2} m^2/s")
print(f"Speed: {speed_mapping} m/s")
print(f"Power required during mission phase: {(power_map):.2f} W. Total power consumed during this phase: {(t_phase2 * power_map/3600):.1f} Wh")

# === Phase 3: Forensics ===
print("\n=== Phase 3: Forensics ===")
speed_foro = 0.5  # m/s
illumination_width = 0.56  # m
illumination_area_per_flash = illumination_width ** 2
flash_duration = 0.2  # s
stride_per_flash = illumination_area_per_flash / illumination_width
time_between_flashes = stride_per_flash / speed_foro
light_off_time = time_between_flashes - flash_duration
duty_cycle = flash_duration / time_between_flashes

P_forensics_static = {
    "Herelink 1.1": 4,
    "ToF Sensor": 0.1 + 0.25,
    "DC-DC Converter": 0.1,
    "PCB": 0.99,
    "Arducam 1": 0.99,
    "Arducam 2": 0.99,
}
P_led_peak = 33.3
P_led_avg = P_led_peak * duty_cycle
P_total_forensics = sum(P_forensics_static.values()) + P_led_avg
power_foro = hover_power + P_total_forensics
e_remaining_foro = Wh_batt - (e_phase1_total + e_phase4_total)
t_phase3 = (e_remaining_foro * 3600) / power_foro / 2
coverage_rate_foro = speed_foro * illumination_width
area_foro = t_phase3 * coverage_rate_foro
total_time_foro = t_phase1 + t_phase3 + t_phase4

print(f"Max Time: {t_phase3:.3f} s = {(t_phase3/60):.2f} minutes")
print(f"Total Forensics Mission Time: {total_time_foro:.3f} s = {(total_time_foro/60):.2f} minutes")
print(f"Ground Area Covered: {area_foro:.1f} m²")
print(f"Speed: {speed_foro} m/s, Coverage Rate: {coverage_rate_foro:.2f} m²/s")
print(f"Power required during mission: {power_foro:.2f} W   . Total power consumed during this phase: {(t_phase3 * power_foro/3600):.1f} Wh")
print(f"UV Flash every {stride_per_flash:.2f} m → every {time_between_flashes:.3f} s")
print(f"Light is ON for {flash_duration}s, OFF for {light_off_time:.3f}s between flashes")

# === Power Analysis Summary ===
print("\n=== Power Analysis Summary ===")

components = [
    {"name": "Voyant Helium", "power": 27, "voltage": 24},
    {"name": "Herelink 1.1", "power": 4, "voltage": 8},
    {"name": "Seoul Viosys LEDs", "power": 33.3, "voltage": 11.1},
    {"name": "ToF Sensor", "power": 0.1, "voltage": 4.8},
    {"name": "PCB", "power": 0.99, "voltage": 3.3},
    {"name": "Arducam 1", "power": 0.99, "voltage": 3.3},
    {"name": "Arducam 2", "power": 0.99, "voltage": 3.3},
    {"name": "Cube Orange+", "power": 5, "voltage": 5},
    {"name": "Orange Pi 5", "power": 5, "voltage": 5},
    {"name": "ToF Cruise", "power": 0.25, "voltage": 4.8},
]

P_components_max = sum(c["power"] for c in components)
I_max_total = P_components_max / V_batt

def max_voltage(used_components):
    return max(comp["voltage"] for comp in used_components)

# Phase 1 (Entry)
P_max1 = motor_power_avg + sum(c["power"] for c in components if c["name"] in ["Herelink 1.1", "ToF Sensor", "Arducam 2", "Cube Orange+", "Orange Pi 5"])
V_max1 = 16
I_max1 = P_max1 / V_batt

# Phase 2 (Mapping)
components_phase2_names = P_mapping.keys()
components_phase2 = [c for c in components if c["name"] in components_phase2_names]
P_max2 = hover_power + sum(c["power"] for c in components_phase2)
I_max2 = P_max2 / V_batt
V_max2 = max_voltage(components_phase2)

# Phase 3 (Forensics)
components_phase3 = [c for c in components if c["name"] != "Voyant Helium"]
components_phase3.append({"name": "Seoul Viosys LEDs", "power": P_led_peak, "voltage": 3.6})
P_max3 = hover_power + sum(c["power"] for c in components_phase3)
I_max3 = P_max3 / V_batt
V_max3 = max(max_voltage(components_phase3), 16)



# Phase 4 (Exit, same as Phase 1)
P_max4 = P_max1
I_max4 = P_max4 / V_batt
V_max4 = V_max1

# === Output Max Power and Current ===
print("\n=== Maximum Phase-wise Electrical Demands ===")
print(f"Phase 1 (Entry):     {I_max1:.2f} A @ {V_max1:.1f} V")
print(f"Phase 2 (Mapping):   {I_max2:.2f} A @ {V_max2:.1f} V")
print(f"Phase 3 (Forensics): {I_max3:.2f} A @ {V_max3:.1f} V")
print(f"Phase 4 (Exit):      {I_max4:.2f} A @ {V_max4:.1f} V")



print("\n=== Grenfell Tower Mission Time Estimation ===")

grenfell_m2 = 11153
ground_time = 10 * 60  # 10 minutes in seconds
daily_operational_time = 7 * 3600  # 7 hours active

# === Mapping Mission Loop ===
area_remaining_map = grenfell_m2
total_time_map_mission = 0

while area_remaining_map > 0:
    area_remaining_map -= area_map
    total_time_map_mission += total_time_map
    if area_remaining_map > 0:
        total_time_map_mission += ground_time  # add ground time if not last

# === Forensics Mission Loop ===
area_remaining_foro = grenfell_m2
total_time_foro_mission = 0

while area_remaining_foro > 0:
    area_remaining_foro -= area_foro
    total_time_foro_mission += total_time_foro
    if area_remaining_foro > 0:
        total_time_foro_mission += ground_time

# === Total Mission Time ===
total_mission_time = total_time_map_mission + total_time_foro_mission
total_minutes = total_mission_time / 60
total_hours = total_minutes / 60

# === Day Estimation ===
days_exact = total_mission_time / daily_operational_time
days_rounded_up = int(np.ceil(days_exact))
print(f"Mapping mission time: {(total_time_map_mission/3600):.1f} hours. Forensics mission time: {(total_time_foro_mission/3600):.1f} hours")
print(f"Total Mission Time (Mapping + Forensics with ground breaks):")
print(f"{total_mission_time:.0f} seconds = {total_minutes:.1f} minutes = {total_hours:.2f} hours")
print(f"Days on site (including 1 hour setup/packup daily): {days_exact:.1f} days")
print(f"Total site days (rounded up): {days_rounded_up} days")

# === Daily Ground Coverage ===
daily_flight_time = daily_operational_time

# Mapping missions per day
single_mapping_cycle = total_time_map + ground_time 
mapping_missions_per_day = int(daily_flight_time // single_mapping_cycle)
daily_area_mapping = mapping_missions_per_day * area_map

# Forensics missions per day
single_foro_cycle = total_time_foro + ground_time 
forensics_missions_per_day = int(daily_flight_time // single_foro_cycle)
daily_area_forensics = forensics_missions_per_day * area_foro

print("\n=== Daily Ground Coverage ===")
print(f"Mapping: {mapping_missions_per_day} missions/day → {daily_area_mapping:.1f} m²/day")
print(f"Forensics: {forensics_missions_per_day} missions/day → {daily_area_forensics:.1f} m²/day")


comparison_drones = {
    "DJI Phantom 4 Pro": {
        "weight_kg": 1.38,
        "flight_time_min": 30,
        "battery_wh": 89.8,
        "area_per_flight_m2": 1000,  # approximate mapping coverage
    },
    "Autel Evo Lite+": {
        "weight_kg": 0.835,
        "flight_time_min": 40,
        "battery_wh": 68.7,
        "area_per_flight_m2": 1200,  # assumed mapping coverage
    },
    "Your Drone": {
        "weight_kg": 2.0,
        "flight_time_min": total_time_map/60,
        "battery_wh": Wh_batt,
        "area_per_flight_m2": area_map,
    }
}

# === Compute Comparative Metrics ===
# for drone in comparison_drones.values():
#     drone["energy_per_m2"] = drone["battery_wh"] / drone["area_per_flight_m2"]
#     drone["flights_per_day"] = int(7*60 / (drone["flight_time_min"] + 10))
#     drone["daily_area_m2"] = drone["flights_per_day"] * drone["area_per_flight_m2"]

# # === Print Comparison Table ===
# print(f"\n{'Drone':<20} | {'Wt (kg)':<7} | {'Flight (min)':<12} | {'Wh/m²':<8} | {'Daily area (m²)':<15}")
# print("-"*70)
# for name, d in comparison_drones.items():
#     print(f"{name:<20} | {d['weight_kg']:<7.2f} | {d['flight_time_min']:<12.1f} | "
#           f"{d['energy_per_m2']:<8.3f} | {d['daily_area_m2']:<15.1f}")