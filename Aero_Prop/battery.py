import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
#from Trade_off.datasets import battery_db as batteries
import pandas as pd
from itertools import combinations
from batt_mot_db import battery_dbx, motor_db
from XROTOR_auto.post_processing import required_thrust


def process_batteries(batteries):
    for battery in batteries:
        #if 'energy_capacity' not in battery:
        battery['energy_capacity'] = round((battery['capacity'] / 1000) * battery['voltage'], 2)
        #if 'energy_density' not in battery:
        battery['energy_density'] = round((battery['energy_capacity'] * 1000) / battery['mass'], 2)

process_batteries(battery_dbx)

def preprocess_motors(motors):
    for motor in motors:
        if motor.get('power') is None and motor.get('voltage') and motor.get('peak_current'):
            motor['power'] = motor['voltage'] * motor['peak_current']

preprocess_motors(motor_db)

def get_max_current(battery):
    c = battery.get("C-rating")
    if c is None:
        return None
    return (battery["capacity"] / 1000) * c  # A

# Define requirements
throttle = 0.5 

# motor_power = 260 * 4 * throttle   # W
# motor_peak_current = 21.7 * 4  # A
# motor_voltage = 12  # V
# max_motor_volt = 25.2  # V, max voltage for motor operation
# motor_energy_wh = motor_power * (20 / 60)  # 10 minutes operation

low_voltage_min = 7.0
low_voltage_max = 20
electronics_power_mode1 = 52.09 
electronics_power_mode2 = 59.38 
max_electronics_power = max(electronics_power_mode1, electronics_power_mode2)
electronics_energy_wh = max_electronics_power * (20 / 60)
electronics_current = 4.5  # A estimate from your table


def get_batteries_motor(motor_db, battery_dbx, required_thrust, throttle=0.5):
    motor_batt = {}
    for motor in motor_db:
        if motor["max_thrust"] < required_thrust / 9.81 * 1000:
            continue
        motor_power = motor['power'] * throttle * 4 # W
        #motor_peak_current = 4 * motor['peak_current']  # A
        motor_voltage = motor['voltage']  # V
        max_motor_volt = 30  # V, max voltage for motor operation
        motor_energy_wh = motor_power * (15 / 60)  # 20 minutes operation

        tot_power = motor_power + max_electronics_power
        tot_voltage_parallel = max(low_voltage_max, motor_voltage)  
        tot_voltage_series = motor_voltage + low_voltage_max
        tot_energy = motor_energy_wh + electronics_energy_wh
        print(motor['id'], tot_energy)


        single_motor_batteries = []
        for b in battery_dbx:
            m = b["mass"]
            v = b["voltage"]
            energy = b.get("energy_capacity")
            max_current = get_max_current(b)
            if max_motor_volt >= v >= motor_voltage and energy and energy >= motor_energy_wh:
                #if max_current is None or max_current >= motor_peak_current:
                single_motor_batteries.append({**b, "max_current_est": max_current})
        single_motor_batteries = sorted(single_motor_batteries, key=lambda x: x['mass'])

        # maybe do two 
        # In parallel: Same voltage, sum capacity, and sum max current.
        #In series: Sum voltage, same capacity, and same max current.
        combo_motor_batteries = []
        for b1, b2 in combinations(battery_dbx, 2):
            # Assume parallel or similar config
            combined_energy = b1['energy_capacity'] + b2['energy_capacity']
            avg_voltage = max(b1['voltage'], b2['voltage']) 

            # Series 
            # combined_energy = max(b1['energy_capacity'], b2['energy_capacity'])
            # avg_voltage = b1['voltage'] + b2['voltage']

            combined_mass = b1['mass'] + b2['mass']
            
            combined_energy_density = round((combined_energy * 1000) / combined_mass, 2)
            
            if motor_voltage <= avg_voltage <= max_motor_volt and combined_energy >= motor_energy_wh:
                combo_motor_batteries.append({
                    'ids': (b1['id'], b2['id']),
                    'voltage': avg_voltage,
                    'energy_capacity': combined_energy,
                    'mass': combined_mass,
                })
        combo_motor_batteries = sorted(combo_motor_batteries, key=lambda x: x['mass'])

        tot_batteries = []
        for b in battery_dbx:
            m = b["mass"]
            v = b["voltage"]
            energy = b.get("energy_capacity")
            max_current = get_max_current(b)
            if v >= tot_voltage_parallel and energy and energy >= tot_energy:
                #if max_current is None or max_current >= tot_power / v:
                tot_batteries.append({**b, "max_current_est": max_current})
        tot_batteries.sort(key=lambda x: -x.get("mass", 0))


        best_single_motor = min(single_motor_batteries, key=lambda x: x['mass'], default=None)
        best_combo_motor = min(combo_motor_batteries, key=lambda x: x['mass'], default=None)
        best_integrated = min(tot_batteries, key=lambda x: x['mass'], default=None)

        motor_batt[motor['id']] = {
            'single_batteries': best_single_motor,
            'combo_batteries': best_combo_motor,
            'total_batteries': tot_batteries
        }
    return motor_batt

motor_batt = get_batteries_motor(motor_db, battery_dbx, required_thrust, throttle)

  
min_mass = 10000
best = []
best_options = {}

for motor_id, options in motor_batt.items():
    mass = min(
        [b['mass'] for b in options.values() if b is not None and 'mass' in b],
        default=None
    )
    if mass is not None and mass < min_mass:
        min_mass = mass
        # best = [motor_id]  # Reset to only this best motor
        # best_options = {motor_id: options}
        best.append(motor_id)
        best_options[motor_id] = options
    elif mass == min_mass:
        best.append(motor_id)
        best_options[motor_id] = options

print("\n--- Best Motor Battery Options ---")
for motor_id in best[::-1]:
    print(f"\n=== Motor: {motor_id} ===")
    options = best_options[motor_id]

    single = options.get('single_batteries')
    if single:
        print(f"Single Battery Option: ID: {single['id']}, Voltage: {single['voltage']}V, "
              f"Energy: {single['energy_capacity']}Wh, Mass: {single['mass']}g, "
              f"Max Current: {single.get('max_current_est', 'N/A')}A")
    else:
        print("No suitable single battery found.")

    combo = options.get('combo_batteries')
    if combo:
        ids = ', '.join(combo['ids'])
        print(f"Combo Battery Option: IDs: {ids}, Average Voltage: {combo['voltage']}V, "
              f"Combined Energy: {combo['energy_capacity']}Wh, Combined Mass: {combo['mass']}g")
    else:
        print("No suitable combo battery found.")

    total = options.get('total_batteries')
    if total:
        for bat in total:
            print(f"Total Battery Option: ID: {bat['id']}, Voltage: {bat['voltage']}V, "
                f"Energy: {bat['energy_capacity']}Wh, Mass: {bat['mass']}g, "
                f"Max Current: {bat.get('max_current_est', 'N/A')}A")
    else:
        print("No suitable total battery found.")

# Electronics   
low_volt_batteries = []
for b in battery_dbx:
    m = b["mass"]
    v = b["voltage"]
    energy = b.get("energy_capacity")
    max_current = get_max_current(b)
    if low_voltage_min <= v <= low_voltage_max and energy and energy >= electronics_energy_wh:
        #if max_current is None or max_current >= electronics_current:
        low_volt_batteries.append({**b, "max_current_est": max_current})

low_volt_batteries.sort(key=lambda x: -x.get("mass", 0))

print("\n--- Selected Electronics Battery ---")
for b in low_volt_batteries[:-6:-1]:
    print(f"ID: {b['id']}, Voltage: {b['voltage']}V, Energy: {b['energy_capacity']}Wh, "
          f"Mass: {b['mass']}g, Energy Density: {b['energy_density']} Wh/kg, Max Current: {b['max_current_est']}A")
    

#best_electronics_battery = min(low_volt_batteries, key=lambda x: x['mass'], default=None)

# high_volt_batteries.sort(key=lambda x: -x.get("energy_density", 0))
# low_volt_batteries.sort(key=lambda x: -x.get("energy_density", 0))





# Output
# Print results nicely


# print("\n=== Single Battery Options for Motor ===")
# for b in single_motor_batteries[::4]:
#     print(f"- ID: {b['id']}")
#     print(f"  Voltage: {b['voltage']} V, Energy: {b['energy_capacity']} Wh, Mass: {b['mass']} g, Max Current: {b['max_current_est']} A\n")

# print("\n=== Two-Battery Combo Options for Motor ===")
# for c in combo_motor_batteries[:4]:
#     print(f"- IDs: {c['ids'][0]} + {c['ids'][1]}")
#     print(f"  Average Voltage: {c['voltage']:.2f} V, Combined Energy: {c['energy_capacity']} Wh, Combined Mass: {c['mass']} g\n")
    
# print("\n--- Selected Motor Battery Options ---")
# for b in all_options_sorted[::-1]:
#     ids = ', '.join(b['ids'])
#     print(f"IDs: {ids}, Voltage: {b['voltage']}V, Energy: {b['energy_capacity']}Wh, "
#           f"Mass: {b['mass']}g, Energy Density: {b['energy_density']} Wh/kg")
    


# print("\n--- Total Battery Options ---")
# for b in tot_batteries[:-5:-1]:
#     print(f"ID: {b['id']}, Voltage: {b['voltage']}V, Energy: {b['energy_capacity']}Wh, "
#           f"Mass: {b['mass']}g, Energy Density: {b['energy_density']} Wh/kg, Max Current: {b['max_current_est']}A")