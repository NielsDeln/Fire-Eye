import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.preprocessing import PolynomialFeatures


# Convert actual weight and downwash to NumPy arrays and filter out None values
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

actual_weight_filtered = []
actual_downwash_filtered = []
for w, d in zip(actual_weight_g, actual_downwash_m_s):
    if d is not None:
        actual_weight_filtered.append(w)
        actual_downwash_filtered.append(d)

# Convert to numpy arrays
actual_weight_filtered = np.array(actual_weight_filtered)
actual_downwash_filtered = np.array(actual_downwash_filtered)

# Estimated values
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


#Linear features
linear = PolynomialFeatures(degree=1)
X_train_poly = linear.fit_transform(actual_weight_filtered.reshape(-1,1))
X_val_poly = linear.transform(estimated_weight_g.reshape(-1,1))

#linear regressor
linear_mod = LinearRegression()
linear_mod.fit(X_train_poly, actual_downwash_filtered)

#RMSE
train_predictions = linear_mod.predict(X_train_poly)
val_predictions = linear_mod.predict(X_val_poly)

train_rmse = np.std(train_predictions - actual_downwash_filtered, ddof=1)
validation_rmse =np.std(val_predictions - estimated_downwash_m_s, ddof=1)

print(f'RMSE of actual data is {train_rmse}')
print(f'RMSE of simulated data is {validation_rmse}')

sorted_indices = np.argsort(actual_weight_filtered)
slope = actual_weight_filtered[sorted_indices]
predictions = train_predictions[sorted_indices]

# fig, ax = plt.subplots(figsize=(10, 6))
# ax.scatter(actual_weight_g, estimated_weight_g, label='Actual', color='orange', alpha=0.7)
# plt.show()

fig, ax = plt.subplots(figsize=(10, 6))

ax.scatter(actual_weight_filtered, actual_downwash_filtered, label='Actual', color='orange', alpha=0.7)
ax.scatter(estimated_weight_g, estimated_downwash_m_s, label='Estimated', color='pink', alpha=0.7)
ax.plot(slope, predictions, color='b', label=f"Degree 1")

ax.set_title('Weight vs. Downwash')
ax.set_xlabel('Weight (g)')
ax.set_ylabel('Downwash (m/s)')
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()


# fig, ax = plt.subplots(figsize=(10, 6))

# ax.scatter(actual_weight_g, advertised_flight_time_min, label='Actual', color='orange', alpha=0.7)
# ax.scatter(estimated_weight_g, estimated_flight_time_min, label='Estimated', color='pink', alpha=0.7)

# ax.set_title('Weight vs. Flight Time')
# ax.set_xlabel('Weight (g)')
# ax.set_ylabel('Flight Time (min)')
# ax.legend()
# ax.grid(True)
# plt.tight_layout()
# plt.show()


