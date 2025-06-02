import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# Data
actual_weight_g = np.array([
    0.57, 0.595, 0.6, 0.72, 0.724, 0.75, 0.75, 0.835, 0.895, 0.895, 0.895,
    0.898, 0.898, 0.907, 0.958, 1.15, 1.388, 1.42, 1.5, 1.62, 1.063, 2.2, 2.3, 2.5
]) * 1000

actual_downwash_m_s = [
    9.315214482, 9.517303392, 9.355577808, 8.669229404, 8.693277243,
    9.094916006, 9.057002971, 9.556461538, 8.945069434, 8.945069434,
    8.945069434, None, None, 9.730993784, 9.254542473, 10.59203031,
    11.08383398, 9.808288257, None, 10.28578936, None, 14.65013529,
    None, None
]

advertised_flight_time_min = np.array([
    34, 31, 40, 46, 45, 47, 47, 40, 46, 46, 46,
    32, 32, 31, 43, 40, 30, 49, 20, 42, 45, 32, 65, 6
])

estimated_weight_g = np.array([
    1046.106, 1057.47, 1059.742, 1322.81, 1324.629, 1336.447, 1336.447,
    1384.629, 1699.402, 1699.402, 1699.402, 1204.742, 1413.266, 1208.833,
    1138.265, 1826.491, 1647.172, 1949.218, 1489.56, 1973.548, 2237.185,
    2671.276, 3754.231, 2101.96
])

estimated_downwash_m_s = np.array([
    18.184, 18.283, 18.302, 20.448, 20.462, 20.553, 20.553, 20.92, 23.177,
    23.177, 23.177, 19.514, 21.136, 19.547, 18.968, 15.017, 14.261, 15.514,
    13.562, 12.488, 13.296, 14.529, 17.224, 12.888
])

estimated_flight_time_min = np.array([
    34.517, 34.461, 34.677, 46, 34.407, 47, 47, 34.198, 46, 46, 46,
    34.893, 33.737, 34.075, 34.151, 33.988, 33.421, 38.781, 15.683,
    37.163, 37.399, 26.866, 53.333, 4.979
])

# Filter valid data
actual_weight_filtered = []
actual_downwash_filtered = []
actual_flight_time_filtered = []
for w, d, f in zip(actual_weight_g, actual_downwash_m_s, advertised_flight_time_min):
    if d is not None:
        actual_weight_filtered.append(w)
        actual_downwash_filtered.append(d)
        actual_flight_time_filtered.append(f)

actual_weight_filtered = np.array(actual_weight_filtered)
actual_downwash_filtered = np.array(actual_downwash_filtered)
actual_flight_time_filtered = np.array(actual_flight_time_filtered)

# Dataset pairs to process
datasets = [
    ("Downwash (m/s)", actual_downwash_filtered, estimated_downwash_m_s),
    ("Flight Time (min)", actual_flight_time_filtered, estimated_flight_time_min)
]

# Plotting and RMSE calculation
for i, (ylabel, actual_data, estimated_data) in enumerate(datasets):
    # Polynomial features
    poly = PolynomialFeatures(degree=1)
    X_train_poly = poly.fit_transform(actual_weight_filtered.reshape(-1, 1))
    X_val_poly = poly.transform(estimated_weight_g.reshape(-1, 1))

    # Linear regression
    linear_mod = LinearRegression()
    linear_mod.fit(X_train_poly, actual_data)

    # Predictions
    train_predictions = linear_mod.predict(X_train_poly)
    val_predictions = linear_mod.predict(X_val_poly)

    # RMSE
    train_rmse = np.std(train_predictions - actual_data, ddof=1)
    validation_rmse = np.std(val_predictions - estimated_data, ddof=1)

    print(f"--- {ylabel} ---")
    print(f"RMSE of actual data: {train_rmse:.3f}")
    print(f"RMSE of simulated data: {validation_rmse:.3f}")

    # Plot
    sorted_indices = np.argsort(actual_weight_filtered)
    sorted_weight = actual_weight_filtered[sorted_indices]
    sorted_predictions = train_predictions[sorted_indices]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(actual_weight_filtered, actual_data, label='Actual', color='orange', alpha=0.7)
    ax.scatter(estimated_weight_g, estimated_data, label='Estimated', color='pink', alpha=0.7)
    ax.plot(sorted_weight, sorted_predictions, color='b', label='Degree 1 Fit')

    ax.set_title(f'Weight vs. {ylabel}')
    ax.set_xlabel('Weight (g)')
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.show()
