from propulsion_iteration import converge_gtow_and_prop
from weight_estimation import m_pl, m_battery
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
    n_cells = 4  # Initial guess

    cell_voltage = 3.7  # Nominal voltage per cell
    discharge_eff = 0.9
    valid_cells = [3, 4, 6]

    for i in range(max_outer):
        print(f"\n========================")
        print(f"   Outer Loop {i+1} - Weight + Power")
        print(f"========================")

        # Step 1: Run GTOW + motor/prop optimization
        result = converge_gtow_and_prop(m_pl, battery_capacity=C_estimate, n_cells=n_cells)

        # Step 2: Compute total power consumption
        T_motor = result['T_motor']
        motor = result['motor']
        motor_eff = motor['efficiency']
        P_motor = T_motor / motor_eff / 1000  # W P_motor = T_motor * hover_power_coeff / motor_eff

        P_total = 4 * P_motor + P_payload
        print(f"Estimated Power Use: {P_total:.2f} W")

        # Step 3: Required energy
        E_required = P_total * t_flight  # Wh

        # Step 4: Determine best battery cell count (3, 4, or 6)
        best_config = None
        min_mass = float('inf')

        for nc in valid_cells:
            voltage = nc * cell_voltage
            C_temp = (E_required / voltage) * 1000 / discharge_eff  # mAh
            m_temp = m_battery(nc, C_temp)

            if m_temp < min_mass:
                min_mass = m_temp
                best_config = {
                    'n_cells': nc,
                    'C_required': C_temp
                }

        # Update battery parameters
        n_cells = best_config['n_cells']
        C_required = best_config['C_required']
        print(f"Selected Cells: {n_cells} | New Estimated Capacity: {C_required:.1f} mAh")

        # Step 5: Convergence Check
        if abs(result['GTOW'] - prev_gtow) < tol:
            print("\nSYSTEM CONVERGED")
            return {
                **result,
                'P_total': P_total,
                'E_required': E_required,
                'C_required': C_required,
                'n_cells': n_cells
            }

        # Update for next loop
        C_estimate = C_required
        prev_gtow = result['GTOW']

    raise RuntimeError("System did not converge after all iterations.")



if __name__ == "__main__":
    result = full_system_loop(m_pl, P_payload=15, t_flight=20)