import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Trade_off.Tilted_Octocopter.propulsion_iteration_octo import converge_gtow_and_prop
from Trade_off.Tilted_Octocopter.weight_estimation_poop import m_pl, m_payload
from Trade_off.datasets import *
from Trade_off.Quadcopter.power_iteration import analyze_performance, full_system_loop



if __name__ == "__main__":
    base_m_pl = m_payload(198, 19, 230, 0, 150)  # g
    base_P_payload = 65  # watts
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
                performance = analyze_performance(results, n_rotors=8)
                for k, v in performance.items():
                    print(f"{k}: {v:.3f}")
            except RuntimeError as e:
                print(f"Failed to converge: {e}")