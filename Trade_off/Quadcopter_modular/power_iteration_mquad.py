import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Trade_off.Quadcopter_modular.propulsion_iteration_mquad import converge_gtow_and_prop
from Trade_off.Quadcopter_modular.weight_estimation_mquad import m_pl, m_payload
from Trade_off.datasets import *
from Trade_off.Quadcopter.power_iteration import analyze_performance



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


if __name__ == "__main__":
    base_m_pl = m_payload(198, 0, 230, 0, 150)  # g
    base_P_payload = 29.45  # watts
    t_flight = 0.416  # hours

    # Margins: -20%, baseline, +20%
    margin_factors = [0.8, 1.0, 1.2]

    for m_margin in margin_factors:
        for p_margin in margin_factors:
            adjusted_m_pl = base_m_pl * m_margin
            adjusted_P_payload = base_P_payload * p_margin
            print(f"\n==== Running Analysis for m_pl {int(m_margin*100)}%, P_payload {int(p_margin*100)}% ====")
            try:
                results = full_system_loop(adjusted_m_pl, adjusted_P_payload, t_flight=t_flight)
                performance = analyze_performance(results)
                for k, v in performance.items():
                    print(f"{k}: {v:.3f}")
            except RuntimeError as e:
                print(f"Failed to converge: {e}")