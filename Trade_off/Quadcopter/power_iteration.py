from propulsion_iteration import converge_gtow_and_prop
from weight_estimation import m_pl
"""
Power Estimation:
Compute total power needed: motor + payload systems.
Use this to determine the required energy.
Battery Sizing Loop:
From energy requirement, compute needed battery capacity.
Re-estimate battery weight and update GTOW → back to step 1"""

def full_system_loop(m_pl, P_payload, t_flight, tol=1e-2, max_outer=10):
    prev_gtow = 0
    C_estimate = 4276  # Initial guess in mAh

    for i in range(max_outer):
        print(f"\n========================")
        print(f"   Outer Loop {i+1} - Weight + Power")
        print(f"========================")

        # Step 1: Run GTOW + motor/prop optimization
        result = converge_gtow_and_prop(m_pl, battery_capacity=C_estimate)

        # Step 2: Compute total power consumption
        T_motor = result['T_motor']
        motor = result['motor']
        motor_eff = motor['efficiency']
        P_motor = T_motor / motor_eff / 1000  # W
        P_total = 4 * P_motor + P_payload
        print(f"Estimated Power Use: {P_total:.2f} W")

        # Step 3: required energy
        E_required = P_total * t_flight  # Wh

        # Step 4: to battery capacity
        n = result['battery_cells']
        cell_voltage = 3.7  # nominal
        voltage = n * cell_voltage

        discharge_eff = 0.9
        C_required = (E_required / voltage) * 1000 / discharge_eff  # mAh
        print(f"New Estimated Battery Capacity: {C_required:.1f} mAh")

        # Step 5: Convergence Check
        if abs(result['GTOW'] - prev_gtow) < tol:
            print("\nSYSTEM CONVERGED")
            return {
                **result,
                'P_total': P_total,
                'E_required': E_required,
                'C_required': C_required,
            }

        # Update for next loop
        C_estimate = C_required
        prev_gtow = result['GTOW']

    raise RuntimeError("System did not converge after all iterations.")




result = full_system_loop(m_pl, P_payload=15, t_flight=20)