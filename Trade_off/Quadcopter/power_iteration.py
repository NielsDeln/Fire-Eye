from propulsion_iteration import converge_gtow_and_prop
from weight_estimation import m_pl

# battery database
battery_db = [
    {'id': 'GAONENG GNB 4S 14.8V', 'type': 'Li-ion', 'cells': 4, 'capacity': 4000, 'mass': 434, 'voltage': 14.8,
     'energy_capacity': 88.8, 'C-rating': 10, 'energy_density': 204.61},
    
    {'id': 'GNB', 'type': 'LiPo 6s', 'cells': 6, 'capacity': 1100, 'mass': 177, 'voltage': 22.8,
     'energy_capacity': 25.08, 'C-rating': 5, 'energy_density': 141.69},

    {'id': 'DJI 200 TB55 (for Matrice)', 'type': 'Lipo', 'cells': 6, 'capacity': 7660, 'mass': 885, 'voltage': 22.8,
     'energy_capacity': 174.6, 'C-rating': None, 'energy_density': 197},

    {'id': 'DJI TB51 (for Inspire 3)', 'type': 'LiPo 4s', 'cells': 4, 'capacity': 4280, 'mass': 470, 'voltage': 23.1,
     'energy_capacity': 98.8, 'C-rating': None, 'energy_density': 210},

    {'id': 'DJI Mavic 3 intelligent battery', 'type': 'LiPo 4s', 'cells': 4, 'capacity': 5000, 'mass': 335.5, 'voltage': 15.4,
     'energy_capacity': 77, 'C-rating': None, 'energy_density': 230},

    {'id': 'DJI Air 3s intelligent battery', 'type': 'LiHv', 'cells': 4, 'capacity': 4241, 'mass': 267, 'voltage': 14.67,
     'energy_capacity': 62.6, 'C-rating': None, 'energy_density': 234},

    {'id': 'GRPB042104', 'type': 'LiHv', 'cells': 1, 'capacity': 7100, 'mass': 102, 'voltage': 4.4,
     'energy_capacity': 31.24, 'C-rating': 5, 'energy_density': 306},

    {'id': 'GRP8674133', 'type': 'Li-Ion 4s', 'cells': 4, 'capacity': 12000, 'mass': 176, 'voltage': 4.4,
    'energy_capacity': 52.8, 'C-rating': 5, 'energy_density': 300},

    {'id': 'DJI Air 3s', 'type': 'LiPo 4s', 'cells': 4, 'capacity': 4276, 'mass': 247, 'voltage': 14.6,
     'energy_capacity': 62.5, 'C-rating': None, 'energy_density': 253},

    {'id': 'CNHL LiPo 6s (1300mAh)', 'type': 'LiPo 6s', 'cells': 6, 'capacity': 1300, 'mass': 246, 'voltage': 22.2,
     'energy_capacity': 28.86, 'C-rating': 70, 'energy_density': 117.32},

    {'id': 'CNHL LiPo 6s (1200mAh)', 'type': 'LiPo 6s', 'cells': 6, 'capacity': 1200, 'mass': 204, 'voltage': 22.2,
     'energy_capacity': 26.64, 'C-rating': 30, 'energy_density': 130.59},

    {'id': 'Tattu Low Temp 14500mAh', 'type': 'LiPo 6s', 'cells': 6, 'capacity': 14500, 'mass': 1961, 'voltage': 22.2,
     'energy_capacity': 321.9, 'C-rating': 3, 'energy_density': 164.15},

    {'id': 'Tattu 80.4Ah 4S', 'type': 'LiPo 4s', 'cells': 4, 'capacity': 80400, 'mass': 3500, 'voltage': 11.51,
     'energy_capacity': 1189.92, 'C-rating': 3, 'energy_density': 339},

    {'id': 'Grepow 6S 17000mAh semi-solid', 'type': '6S semi solid', 'cells': 6, 'capacity': 17000, 'mass': 1444, 'voltage': 22.2,
     'energy_capacity': 377.4, 'C-rating': 3, 'energy_density': 300},

    {'id': 'Tattu G-Tech 6S1P', 'type': '6S1P LLiPi', 'cells': 6, 'capacity': 12000, 'mass': 1532, 'voltage': 22.2,
     'energy_capacity': 266.4, 'C-rating': 3, 'energy_density': 173.89},

    {'id': 'Tattu G-Tech 4S 5200mAh', 'type': '4s lipo', 'cells': 4, 'capacity': 5200, 'mass': 436.5, 'voltage': 14.8,
     'energy_capacity': 76.96, 'C-rating': 35, 'energy_density': 176.31},

    {'id': 'S 6750mAh 14.8V', 'type': '4s lipo', 'cells': 4, 'capacity': 6750, 'mass': 620, 'voltage': 14.8,
     'energy_capacity': 99.9, 'C-rating': 25, 'energy_density': 161.13}
]




def full_system_loop(m_pl, P_payload, t_flight, tol=1e-2, max_outer=10):
    prev_gtow = 0
    battery_guess = battery_db[0]

    discharge_eff = 0.9

    for i in range(max_outer):
        print(f"\n========================")
        print(f"   Outer Loop {i+1} - Weight + Power")
        print(f"========================")

        # Step 1: GTOW + motor/prop optimization with current battery guess
        result = converge_gtow_and_prop(
            m_pl,
            battery_capacity=battery_guess['capacity'],
            n_cells=battery_guess['cells'], 
            battery_override=battery_guess,
        )

        # Step 2: total power consumption
        motor = result['motor']
        T_motor = result['T_motor']  
        print(f"Motor Thrust: {T_motor:.2f} g")
        motor_eff = motor['efficiency'] 
        print(f"Motor Efficiency: {motor_eff:.2f}")

        P_motor = T_motor / motor_eff   # watts
        print(f"Motor Power: {P_motor:.2f} W")
        P_total = 4 * P_motor + P_payload
        print(f"Estimated Power Use: {P_total:.2f} W")

        # Step 3: Required energy
        E_required = P_total * t_flight  # Wh

        # Step 4: Find best battery from database
        best_battery = None
        min_mass = float('inf')

        P_required = P_total  # or any specific power required for the system
        for b in battery_db:
            usable_energy = (b['voltage'] * b['capacity'] / 1000) * discharge_eff  # Wh

            # Check if the battery can supply the required power (C-rating check)
            if b['C-rating'] is None:
                continue
            max_discharge_power = b['capacity'] * b['C-rating'] * b['voltage'] / 1000  # in watts
            if usable_energy >= E_required and b['mass'] < min_mass and max_discharge_power >= P_required:
                best_battery = b
                min_mass = b['mass']

        if not best_battery:
            raise RuntimeError("No suitable battery found in the database.")
        print(f"Selected Battery: {best_battery['id']} | {best_battery['capacity']} mAh | {best_battery['cells']}S | {best_battery['mass']} g")

        # Step 5: Convergence check
        if abs(result['GTOW'] - prev_gtow) < tol:
            print("\nSYSTEM CONVERGED")
            return {
                **result,
                'P_total': P_total,
                'E_required': E_required,
                'battery': best_battery
            }

        battery_guess = best_battery
        prev_gtow = result['GTOW']

    raise RuntimeError("System did not converge after all iterations.")



def analyze_performance(result, cruise_speed_kmh=40):
    g = 9.81  # m/s²
    W_takeoff = result['GTOW'] / 1000 * g  # N
    T_max = result['T_max'] / 1000 * g  # N
    T_W = T_max / W_takeoff

    flight_duration_hr = result['E_required'] / result['P_total']  # h
    range_km = cruise_speed_kmh * flight_duration_hr

    fuel_weight_kg = result['battery']['mass'] / 1000  # battery as energy source
    inverse_W_takeoff = 1 / (result['GTOW'] / 1000)  # 1/kg

    # total power to horsepower (1 HP = 745.7 W)
    power_hp = result['P_total'] / 745.7

    return {
        'T/W': T_W,
        'Range (L)': range_km,
        'Flight Duration (T)': flight_duration_hr,
        'Cruising Speed (V_crs)': cruise_speed_kmh,
        '1/W_takeoff': inverse_W_takeoff,
        'Fuel Weight (W_fuel)': fuel_weight_kg,
        'Power Plant Parameter (N_take-off)': power_hp
    }

if __name__ == "__main__":
    results = full_system_loop(m_pl, P_payload=29.45, t_flight=0.416) # hours
    performance = analyze_performance(results)
    for k, v in performance.items():
        print(f"{k}: {v:.3f}")