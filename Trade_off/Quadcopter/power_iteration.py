import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Trade_off.datasets import *
from Trade_off.Quadcopter.propulsion_iteration import converge_gtow_and_prop
from Trade_off.Quadcopter.weight_estimation import m_pl, m_payload, converge_gtow
import math
from prettytable import PrettyTable


def full_system_loop(m_pl, P_payload, t_flight, tol=1e-2, max_outer=10, max_gtow=5000):
    prev_gtow = 0
    battery_guess = battery_db[0]
    n_batt = 1

    throttle = 0.38 # percentage of max throttle

    discharge_eff = 0.9

    for i in range(max_outer):
        #print(f"\n========================")
        #print(f"   Outer Loop {i+1} - Weight + Power")
        #print(f"========================")

        # Step 1: GTOW + motor/prop optimization with current battery guess
        result = converge_gtow_and_prop(
            m_pl,
            battery_capacity=battery_guess['capacity'],
            n_cells=battery_guess['cells'], 
            battery_override=battery_guess,
            #n_batteries=n_batt,
        )

        # Step 2: total power consumption
        motor = result['motor']
        #T_motor = result['T_motor']  
        T_motor = motor["thrust"]  # thrust per motor [g]
        #print(f"Motor Thrust: {T_motor:.2f} g")
        motor_eff = motor['efficiency'] 
        #print(f"Motor Efficiency: {motor_eff:.2f}")

        #P_motor = T_motor / motor_eff   # watts
        P_motor = motor["power"] * throttle
        #print(f"Motor Power: {P_motor:.2f} W")
        P_total = 4 * P_motor + P_payload
        #print(f"Estimated Power Use: {P_total:.2f} W")

        # Step 3: Required energy
        E_required = P_total  * t_flight  #* throttle  # Wh
        #print(f"Required Energy: {E_required:.2f} Wh")


        # Step 4: Find best battery from database
        best_battery = None
        min_mass = float('inf')
        

        P_required = P_total #* throttle  # or any specific power required for the system
        #print(f"Required Power: {P_required:.2f} W")
        #print(f"total Power: {P_total:.2f} W")
        for b in battery_db:
            usable_energy = (b['voltage'] * b['capacity'] / 1000) * discharge_eff  # Wh
            if b['C-rating'] is None:
                continue
            max_discharge_power = b['capacity'] * b['C-rating'] * b['voltage'] / 1000  # in watts
            #print(f"Battery {b['id']} - Usable Energy: {usable_energy:.2f} Wh - Maximum discharge power: {max_discharge_power:.2f}W - Num needed: {math.ceil(E_required / usable_energy)} - Mass: {math.ceil(E_required / usable_energy)*b['mass']} g")
            #print(E_required)
            # Check if the battery can supply the required power (C-rating check)


            if usable_energy >= E_required and max_discharge_power >= P_required:
            #if b["voltage"] >= motor["voltage"] and b["capacity"] >= motor["capacity"]:
                if b['mass'] < min_mass:
                    best_battery = b
                    min_mass = b['mass']
                    n_batt = 1
            
        # if not best_battery:
        #     try:
        #         lightest_battery = min(battery_db, key=lambda x: x['mass'])
        #         n_batteries = math.ceil(E_required / ((lightest_battery['voltage'] * lightest_battery['capacity'] / 1000) * discharge_eff))
        #         print(f"Using {n_batteries} batteries of {lightest_battery[b'id']} to meet energy requirements.")
        #         print(f"Total mass of batteries: {n_batteries * lightest_battery['mass']} g")
        #         best_battery = lightest_battery
        #     except:
        #         raise RuntimeError("No suitable battery found in the database.")

        if not best_battery:
            try:
                # Step 1: Get top 3 batteries with highest discharge power
                top_batteries = sorted(
                    [b for b in battery_db if b.get('C-rating') is not None],
                    key=lambda b: b['capacity'] * b['C-rating'] * b['voltage'] / 1000,
                    reverse=True
                )[:3]

                best_combination = None
                min_total_mass = float('inf')

                for b in top_batteries:
                    usable_energy = (b['voltage'] * b['capacity'] / 1000) * discharge_eff  # Wh
                    max_discharge_power = b['capacity'] * b['C-rating'] * b['voltage'] / 1000  # W
                    n_needed_energy = math.ceil(E_required / usable_energy)
                    n_needed_power = math.ceil(P_required / max_discharge_power)
                    n_batt = max(n_needed_energy, n_needed_power)
                    total_mass = n_batt * b['mass']

                    if total_mass < min_total_mass:
                        best_combination = b
                        best_battery = b
                        n_batt = n_batt
                        min_total_mass = total_mass

                if best_battery is not None:
                    print(f"Using {n_batt}x {best_battery['id']} in parallel.")
                    print(f"Total mass of batteries: {n_batt * best_battery['mass']} g")
                else:
                    raise RuntimeError("No suitable battery combination found.")

            except Exception as e:
                raise RuntimeError("Battery selection failed with error: " + str(e))

        #print(f"Selected Battery: {best_battery['id']} | {best_battery['capacity']} mAh | {best_battery['cells']}S | {best_battery['mass']} g")
        motor_guess = result["motor"]
        d_p = motor_guess['prop_diameter']  # cm
        #gtow, T_max, T_motor, motor, propeller, m_m, m_e, m_b, m_p, m_f, m_a, m_pl = converge_gtow_and_prop(m_pl, battery_capacity=battery_guess['capacity'], n_cells=battery_guess['cells'],  battery_override=battery_guess, motor_override=motor_guess,n_batteries=n_batt)
        gtow, T_max, T_motor, m_m, m_e, m_b, m_p, m_f, m_a, m_pl = converge_gtow(
            m_pl,
            d_p=d_p,
            battery_cells=best_battery['cells'],
            battery_capacity=best_battery['capacity'],
            n_batteries=n_batt,
            battery_override=best_battery,
            motor_override=motor_guess
        )
        #prev_gtow = gtow
        # Step 5: Convergence check
        if abs(result['GTOW'] - prev_gtow) < tol:
            #print("\nSYSTEM CONVERGED at iteration", i+1)
            return {
                **result,
                "GTOW": gtow,
                "T_max": T_max,
                "T_motor": T_motor,
                #'motor': motor,
                #'propeller': {'diameter': motor['prop_diameter']},
                "m_motor": m_m,
                "m_ESC": m_e,
                "m_battery": m_b,
                "m_propeller": m_p,
                "m_frame": m_f,
                "m_avionics": m_a,
                "m_payload": m_pl,
                'P_total': P_total,
                'E_required': E_required,
                'battery': best_battery,
                "m_battery": best_battery['mass'] * n_batt,
                "usable_energy": (best_battery['voltage'] * best_battery['capacity'] / 1000) * discharge_eff * n_batt,
                "power_discharge": best_battery['capacity'] * best_battery['C-rating'] * best_battery['voltage'] / 1000 * n_batt,
                
            }

        if result['GTOW'] > max_gtow:
            #print(f"GTOW exceeds the cap of {max_gtow} g. Stopping the iteration.")
            raise RuntimeError("GTOW exceeded the maximum limit.")
        
        battery_guess = best_battery 
        prev_gtow = result['GTOW']

    raise RuntimeError("System did not converge after all iterations.")



def analyze_performance(result, n_rotors=4, cruise_speed_kmh=7.2, rho=1.225, tilt_angle=None):
    g = 9.81  # m/s²
    W_takeoff = result['GTOW'] / 1000 * g  # N
    T_max = result['T_max'] / 1000 * g  # N
    T_W = T_max / W_takeoff

    battery = result['battery']
    energy_batt = (battery['voltage'] * battery['capacity'] / 1000) * 0.9
    discharg_p = battery['capacity'] * battery['C-rating'] * battery['voltage'] / 1000 # W 

    # adding this in case there's more than 1 battery 
    n_needed_energy = math.ceil(result["E_required"] / energy_batt)
    n_needed_power = math.ceil((result["P_total"] / 2) / discharg_p)
    #n_batt = max(n_needed_energy, n_needed_power)
    n_batt = result['m_battery'] / battery['mass']  # sanity check
    #print("POOPIE ENERGY BAT " , n_batt * energy_batt)
    #print("POOPIE P req" , result['P_total'] / 2)
    flight_duration_hr = energy_batt * n_batt / (result["P_total"] / 1)  # h

    # wrong ones:
    # flight_duration_hr1 = result["E_required"] / discharg_p  # h
    # flight_duration_hr1 = result["E_required"] / result["P_total"]  # h
    # flight_duration_hr1 = energy_batt / discharg_p  # h

    range_km = cruise_speed_kmh * flight_duration_hr
    

    # disk loading
    A_prop = (math.pi * (result["propeller"]['diameter'] / 200) ** 2) 
    A_tot_prop = n_rotors * A_prop  # m²
    disk_loading = result['GTOW'] / 1000 / A_tot_prop  # kg/m²

    inverse_W_takeoff = 1 / (result['GTOW'] / 1000)  # 1/kg

    #v2
    

    V1 = math.sqrt((W_takeoff/ n_rotors) / (2 * rho * A_prop))
    
    if tilt_angle:
        V2 = 2 * V1 * math.cos(math.radians(tilt_angle))
    else: 
        V2 = 2 * V1


    # total power to horsepower (1 HP = 745.7 W)
    power_hp = result['P_total'] / 745.7

    # hover power 
    P_hover = n_rotors * (result['motor']["thrust"] * 9.81 / 1000) ** (3/2) /( (2*rho*A_prop)**0.5) # W

    #duav
    ratio = 0.325 / 0.13
    #d = result["motor"]["diameter"] / 100  # m
    #duav = d + 12.667 / 100
    #duav = d * ratio

    return {
        'T/W': T_W,
        'Range (R) m': range_km*1000,
        'Flight Duration min': flight_duration_hr*60,
        'Cruising Speed (V_crs) km/h': cruise_speed_kmh,
        'Disk Loading downwash': disk_loading,
        '1/W_takeoff': inverse_W_takeoff,
        'Power Plant Parameter (N_take-off) w': power_hp,
        'Downwash velocity m/s': V2,
        "Power to hover W": P_hover,
        #"duav": duav,
    }

def print_final_summary(result, performance):
    print("\n=========== FINAL SYSTEM SUMMARY ===========")
    print(f"GTOW                      : {result['GTOW']:.2f} g")
    print(f"Payload Mass            : {result['m_payload']:.2f} g")
    print(f"Frame Mass               : {result['m_frame']:.2f} g")
    print(f"Avionics Mass            : {result['m_avionics']:.2f} g")
    print(f"Propeller Mass           : {result['m_propeller']:.2f} g")
    print(f"Motor Mass               : {result['m_motor']:.2f} g")
    print(f"ESC Mass                 : {result['m_ESC']:.2f} g")
    print(f"Battery Mass            : {result['m_battery']:.2f} g")

    print(f"Total Required Thrust     : {result['T_max']:.2f} g")
    print(f"Per Motor Thrust          : {result['T_motor']:.2f} g")
    
    motor = result['motor']
    print(f"Selected Motor            : {motor['id']}")
    print(f" - Mass                   : {motor['mass']} g")
    print(f" - Max Thrust             : {motor['thrust']} g")
    print(f" - Efficiency             : {motor['efficiency']}")
    print(f" - Diameter               : {motor['diameter']} mm")
    print(f" -  Motor Power           : {motor['power']} W")
    
    
    prop = result['propeller']
    print(f"Selected Propeller        : {prop['diameter']} cm")
    
    print("============================================")
    print(f"Total Power               : {result['P_total']:.2f} W")
    print(f"Energy Required           : {result['E_required']:.2f} Wh")
    
    battery = result['battery']
    print(f"Selected Battery          : {battery['id']}")
    print(f" - Capacity               : {battery['capacity']} mAh")
    print(f" - Voltage                : {battery['voltage']} V")
    print(f" - C-rating               : {battery['C-rating']}")
    print(f" - Mass                   : {battery['mass']} g")
    print(f"Number of Batteries       : {result['m_battery'] / battery['mass']:.2f}")
    print(f"Max discharge Power       : {battery['capacity'] * battery['C-rating'] * battery['voltage'] / 1000:.2f} W")
    print(f"Usable Energy             : {(battery['voltage'] * battery['capacity'] / 1000) * 0.9:.2f} Wh")
    print(f"Total Usable Energy       : {result['usable_energy']:.2f} Wh")
    print(f"Total Discharge Power     : {result['power_discharge']:.2f} W")
    
    
    print("============================================")
    print("Performance Metrics:")
    for key, val in performance.items():
        print(f"{key:<30}: {val:.3f}")
    print("============================================\n")


if __name__ == "__main__":
    """    base_m_pl = m_payload(198, 19, 230, 0, 150)  # g
    base_P_payload = 65  # wattsh
    t_flight = 0.25  # hours

    # Margins: -20%, baseline, +20%
    margin_factors = [0.8, 1.0, 1.2]

    for margin in margin_factors:

        adjusted_m_pl = base_m_pl * margin
        adjusted_P_payload = base_P_payload * margin
        print(f"\n==== Running Analysis for m_pl {int(margin*100)}%, P_payload {int(margin*100)}% ====")
        try:
            results = full_system_loop(
                adjusted_m_pl,
                adjusted_P_payload,
                t_flight=t_flight,
                tol=1e-2,
                max_outer=10,
                max_gtow=5000
            )
            #print(results)
            print_final_summary(results, analyze_performance(results))
        except RuntimeError as e:
            print(f"Failed to converge: {e}")"""
    
    """VALIDATION"""
    """payload_data = [
    (228, 41.4), (238, 40.425), (240, 38.85), (288, 62.6), (289.6, 62.5),
    (300, 51.3), (300, 72), (334, 68.7), (358, 77), (358, 77),
    (358, 77), (359.2, 20.52), (359.2, 78.54), (362.8, 59.29), (383.2, 77),
    (460, 82), (555.2, 89.2), (568, 99.5), (600, 111), (648, 119.4),
    (880, 95.3), (920, 78.54), (1000, 24.42), (1000, 133.2), (1000, 12.92)]"""

    payload_data = [
    (228, 6.21, 34), (238, 6.06375, 31), (240, 5.8275, 40), (288, 9.39, 46), (289.6, 9.375, 45),
    (300, 7.695, 47), (300, 10.8, 47), (334, 10.305, 40), (358, 11.55, 46), (358, 11.55, 46),
    (358, 11.55, 46), (359.2, 3.078, 32), (359.2, 11.781, 32), (362.8, 8.8935, 31), (383.2, 11.55, 43),
    (460, 12.3, 40), (555.2, 13.38, 30), (568, 14.925, 49), (600, 16.65, 20), (648, 17.91, 42),
    (880, 11.781, 45), (920, 3.663, 32), (1000, 19.98, 65), (1000, 1.938, 24), (1000, 12.92, 6)
]
     # mass, power, time flight min

    table = PrettyTable()
    table.field_names = ["Tot Weight (g)", "Flight Time (min)", "Downwash (m/s)", "Battery Mass (g)", "Battery Capacity (mAh)", "Num batt", "Thrust req (g)", "Diameter prop (cm)"]

    #t_flight = 0.25  

    for m_payload_grams, P_payload, t_flight in payload_data:
        print(f"\n==== Running Analysis for Payload {m_payload_grams} g, Payload Power {P_payload} W ====")
        base_m_pl = m_payload(m_payload_grams, 0, 0, 0, 0)
        t_flight = t_flight / 60  # convert minutes to hours
        
        try:
            results = full_system_loop(
                base_m_pl,
                P_payload/t_flight,
                t_flight=t_flight,
                tol=1e-2,
                max_outer=10,
                max_gtow=5000
            )
            performance = analyze_performance(results)
            #print_final_summary(results, performance)
            battery = results['battery']
            num_batt = results['m_battery'] / battery['mass']
            table.add_row([
            round(results['GTOW'], 2),
            round(performance['Flight Duration min'], 2),
            round(performance['Downwash velocity m/s'], 2),
            round(results['m_battery'], 2),
            results['battery']['capacity'],
            round(num_batt, 1),
            round(results["T_max"], 2),
            round(results["propeller"]["diameter"], 2)
        ])
        except RuntimeError as e:
            print(f"Failed to converge for payload {m_payload_grams} g: {e}")
            table.add_row([
                m_payload_grams,
                t_flight * 60,  # convert back to minutes
                "N/A",
                "N/A",
                "N/A",
                "N/A"
            ])
    print("\n poop Table ")
    print(table)  

    """
    m_pl = m_payload(198, 19, 230, 0, 150)  # g
    P_payload = 65  # watts
    t_flight = 0.416  # hours

    results = full_system_loop(m_pl, P_payload, t_flight=t_flight)
    print(results)
    performance = analyze_performance(results, n_rotors=4)
    for k, v in performance.items():
        print(f"{k}: {v:.3f}")"""



    