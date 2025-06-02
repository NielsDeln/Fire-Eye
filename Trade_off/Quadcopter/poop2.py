import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Trade_off.Quadcopter.weight_estimation import m_payload
from power_iteration import full_system_loop, analyze_performance  

# INPUT FROM DATABASE: Payload (g), Payload Power (W), Flight Time (min
payload_data = [
    (228, 6.21, 34), (238, 6.06375, 31), (240, 5.8275, 40), (288, 9.39, 46), (289.6, 9.375, 45),
    (300, 7.695, 47), (300, 10.8, 47), (334, 10.305, 40), (358, 11.55, 46), (358, 11.55, 46),
    (358, 11.55, 46), (359.2, 3.078, 32), (359.2, 11.781, 32), (362.8, 8.8935, 31), (383.2, 11.55, 43),
    (460, 12.3, 40), (555.2, 13.38, 30), (568, 14.925, 49), (600, 16.65, 20), (648, 17.91, 42),
    (880, 11.781, 45), (920, 3.663, 32), (1000, 19.98, 65), (1000, 1.938, 24), (1000, 12.92, 6)
]

results_list = []
performance_list = []

for m_payload_grams, P_payload, t_flight_min in payload_data:
    try:
        m_pl = m_payload(m_payload_grams, 0, 0, 0, 0)
        t_flight_hr = t_flight_min / 60
        P_payload_scaled = P_payload / t_flight_hr

        result = full_system_loop(m_pl, P_payload_scaled, t_flight=t_flight_hr)
        perf = analyze_performance(result)

        results_list.append(result)
        performance_list.append(perf)

    except RuntimeError as e:
        print(f"[FAIL] Payload {m_payload_grams}g: {e}")

# get data poop
payloads = [r["m_payload"] for r in results_list]
gtow = [r["GTOW"] for r in results_list]
duav = [p["duav"] for p in performance_list]
downwash = [p["Downwash velocity m/s"] for p in performance_list]
flight_time = [p["Flight Duration min"] for p in performance_list]


def make_plot_estimated(x, y, xlabel, ylabel, title, color='blue', marker='o', degree=1):
    x = np.array(x).reshape(-1, 1)
    y = np.array(y)

    # polynomial (deg 1 for linear)
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(x)

    # model fit
    model = LinearRegression()
    model.fit(X_poly, y)
    y_pred = model.predict(X_poly)

    # RMSE
    rmse = np.std(y - y_pred, ddof=1)

    # Sorted for clean line plot
    sorted_idx = np.argsort(x.flatten())
    x_sorted = x[sorted_idx].flatten()
    y_pred_sorted = y_pred[sorted_idx]

    # ploot
    plt.figure(figsize=(8, 5))
    plt.scatter(x, y, color=color, label='Estimated')
    plt.plot(x_sorted, y_pred_sorted, linestyle='--', color='black', label='Fit')
    plt.title(f"{title}\nRMSE = {rmse:.2f}")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# make_plot_estimated(payloads, gtow, "Payload (g)", "GTOW (g)", "GTOW vs. Payload", color='blue')
# make_plot_estimated(payloads, flight_time, "Payload (g)", "Flight Time (min)", "Flight Time vs. Payload", color='green')
# make_plot_estimated(gtow, duav, "GTOW (g)", "Motor-to-Motor Distance (m)", "DUAV vs. GTOW", color='orange')
# make_plot_estimated(payloads, downwash, "Payload (g)", "Downwash Velocity (m/s)", "Downwash vs. Payload", color='teal')


# ACTUAL DATABASE DATA (validation) 
actual_payloads = [
    228, 238, 240, 288, 289.6, 300, 300, 334, 358, 358,
    358, 359.2, 359.2, 362.8, 383.2, 460, 555.2, 568, 600, 648,
    880, 920, 1000
]

actual_gtow = [
    0.57, 0.595, 0.6, 0.72, 0.724, 0.75, 0.75, 0.835, 0.895, 0.895, 0.895,
    0.898, 0.898, 0.907, 0.958, 1.15, 1.388, 1.42, 1.5, 1.62, 2.2, 2.3, 2.5
]

actual_gtow = [x * 1000 for x in actual_gtow]  #  grams

actual_flight_time = [
    34, 31, 40, 46, 45, 47, 47, 40, 46, 46,
    46, 32, 32, 31, 43, 40, 30, 49, 20, 42,
    32, 65, 6
]

actual_downwash = [
    9.3152, 9.5173, 9.3556, 8.6692, 8.6933, 9.0949, 9.0570, 9.5565,
    8.9451, 8.9451, 8.9451, None, None, 9.7310, 9.2545, 10.5920, 11.0838,
    9.8083, None, 10.2858, None, None, None, None, None
]

def make_plot(x_est, y_est, x_actual=None, y_actual=None, xlabel='', ylabel='', title='', color='blue', degree=1):
    x_est = np.array(x_est).reshape(-1, 1)
    y_est = np.array(y_est)

    # regression
    poly = PolynomialFeatures(degree=degree)
    X_poly_est = poly.fit_transform(x_est)
    model_est = LinearRegression().fit(X_poly_est, y_est)
    y_pred_est = model_est.predict(X_poly_est)
    est_rmse = np.std(y_est - y_pred_est, ddof=1)

    # sort for plotting
    idx = np.argsort(x_est.flatten())
    x_sorted = x_est[idx].flatten()
    y_sorted = y_pred_est[idx]

    plt.figure(figsize=(8, 5))
    plt.scatter(x_est, y_est, color=color, label='Estimated')
    plt.plot(x_sorted, y_sorted, color='black', linestyle='--', label=f'Est Fit (RMSE={est_rmse:.2f})')

    if x_actual is not None and y_actual is not None:
        x_act = np.array(x_actual).reshape(-1, 1)
        y_act = np.array(y_actual)
        poly_act = PolynomialFeatures(degree=degree)
        X_poly_act = poly_act.fit_transform(x_act)
        model_act = LinearRegression().fit(X_poly_act, y_act)
        y_pred_act = model_act.predict(X_poly_act)
        act_rmse = np.std(y_act - y_pred_act, ddof=1)

        idx_act = np.argsort(x_actual)
        x_sorted_act = np.array(x_actual)[idx_act]
        y_sorted_act = y_pred_act[idx_act]

        plt.scatter(x_actual, y_actual, color='orange', label='Actual')
        plt.plot(x_sorted_act, y_sorted_act, color='red', linestyle=':', label=f'Act Fit (RMSE={act_rmse:.2f})')

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


make_plot(payloads, gtow, actual_payloads, actual_gtow, "Payload (g)", "GTOW (g)", "GTOW vs. Payload", color='blue')
make_plot(payloads, flight_time, actual_payloads, actual_flight_time, "Payload (g)", "Flight Time (min)", "Flight Time vs. Payload", color='green')
#make_plot(gtow, duav, None, None, "GTOW (g)", "Motor-to-Motor Distance (m)", "DUAV vs. GTOW", color='orange')


# Downwash filtering
filtered_actual_dw = [d for d in actual_downwash if d is not None]
filtered_actual_dw_payloads = [p for i, p in enumerate(actual_payloads) if actual_downwash[i] is not None]

make_plot(payloads[:len(filtered_actual_dw)], downwash[:len(filtered_actual_dw)],
          filtered_actual_dw_payloads, filtered_actual_dw,
          "Payload (g)", "Downwash (m/s)", "Downwash vs. Payload", color='teal')