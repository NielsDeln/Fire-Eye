import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import root_mean_squared_error
from mpl_toolkits.mplot3d import Axes3D
from scipy import stats

from sklearn.model_selection import train_test_split

np.set_printoptions(precision=2)
import warnings
warnings.filterwarnings("ignore")

# === Load and preview data ===
#file_path = r'C:\Users\olivi\OneDrive\Aerospace\DSE\DJI_Drones_Compare.csv'
#file_path = r"C:\Users\olivi\OneDrive\Aerospace\DSE\Quadcopter Database Randomised.csv"
#file_path = r"C:\Users\olivi\OneDrive\Aerospace\DSE\Quadcopter database 0-2 kg.csv"
file_path = r"C:\Users\olivi\OneDrive\Aerospace\DSE\DJI Quadcopter database 0-2kg.csv"
raw = pd.read_csv(file_path)
print(raw.head(5))

# === Statistical summary of raw data ===
# Clean column names
raw.columns = raw.columns.str.strip().str.lower()

# Columns to summarize
cols_map = {
    'weight (kg)': 'Weight (kg)',
    'price ($)': 'Price ($)',
    'advertised flight time (min)': 'Advertised Flight Time (min)',
    'battery capacity (mah)': 'Battery capacity (mAh)',
    'propeller area': 'Propeller Area (m^2)'
} 

summary_data = []
for col_key, label in cols_map.items():
    data = pd.to_numeric(raw[col_key], errors='coerce').dropna()
    print(len(data))
    #3
    mean = np.mean(data)
    std_dev = np.std(data, ddof=1)
    conf_int = stats.t.interval(0.95, len(data)-1, loc=mean, scale=stats.sem(data))
    
    summary_data.append({
        'Parameter': label,
        'Mean': mean,
        '95% CI Lower': conf_int[0],
        '95% CI Upper': conf_int[1],
        'Standard Deviation': std_dev
    })

summary_df = pd.DataFrame(summary_data)
print("\nStatistical Summary:")
print(summary_df)

# === Transform to array for regression ===
# raw_array = np.array(raw)
# train_data = raw_array[:15, :]
# val_data = raw_array[15:, :]

# train_weight, train_price, train_ft, train_bp = train_data[:,2], train_data[:,1], train_data[:,4], train_data[:,5]
# val_weight, val_price, val_ft, val_bp = val_data[:,2], val_data[:,1], val_data[:,4], val_data[:,5]
# Convert necessary columns to numeric
raw['weight (kg)'] = pd.to_numeric(raw['weight (kg)'], errors='coerce')
raw['price ($)'] = pd.to_numeric(raw['price ($)'], errors='coerce')
raw['advertised flight time (min)'] = pd.to_numeric(raw['advertised flight time (min)'], errors='coerce')
raw['battery capacity (mah)'] = pd.to_numeric(raw['battery capacity (mah)'], errors='coerce')
raw['propeller area'] = pd.to_numeric(raw['propeller area'], errors='coerce')

# Drop rows with missing values in the relevant columns
clean_raw = raw.dropna(subset=['weight (kg)', 'price ($)', 'advertised flight time (min)', 'battery capacity (mah)', 'propeller area'])

# Extract the features and targets
weights = clean_raw['weight (kg)'].values
prices = clean_raw['price ($)'].values
flight_times = clean_raw['advertised flight time (min)'].values
battery_powers = clean_raw['battery capacity (mah)'].values
propeller_areas = clean_raw['propeller area'].values

# Use train_test_split to split the data (60% train, 40% validation)
train_weight, val_weight, train_price, val_price = train_test_split(weights, prices, test_size=0.4, random_state=42)
_, _, train_ft, val_ft = train_test_split(weights, flight_times, test_size=0.4, random_state=42)
_, _, train_bp, val_bp = train_test_split(weights, battery_powers, test_size=0.4, random_state=42)
_, _, train_prop_area, val_prop_area = train_test_split(weights, propeller_areas, test_size=0.4, random_state=42)

# === Polynomial regression analysis ===
# Polynomial regression analysis with equations and R^2
params = ['price', 'flight time', 'battery capacity', 'propeller area']
rmse_results = []
equation_results = []

for param in params:
    if param == 'price':
        train_param = train_price
        val_param = val_price
        X1 = train_weight
        X2 = val_weight
        xaxis_label = 'Weight (kg)'
        yaxis_label = 'Price ($)'
    elif param == 'flight time':
        train_param = train_ft
        val_param = val_ft
        X1 = train_bp
        X2 = val_bp
        xaxis_label = 'Battery capacity (mAh)'
        yaxis_label = 'Flight Time (min)'
    elif param == 'battery capacity':
        train_param = train_bp
        val_param = val_bp
        X1 = train_weight
        X2 = val_weight
        xaxis_label = 'Weight (kg)'
        yaxis_label = 'Battery capacity (mAh)'
    elif param == 'propeller area':
        train_param = train_weight
        val_param = val_weight
        X1 = train_prop_area
        X2 = val_prop_area
        xaxis_label = 'Propeller Area (m²)'
        yaxis_label = 'Weight (kg)'

    degrees = [1, 2]
    colors = ['green', 'blue']
    train_rmse = []
    validation_rmse = []

    fig, axes = plt.subplots(1, len(degrees), figsize=(6 * len(degrees), 5), sharey=True)
    fig.suptitle(f"Polynomial Regression Models for {param.title()}", fontsize=16)

    for idx, i in enumerate(degrees):
        ax = axes[idx] if len(degrees) > 1 else axes

        ax.scatter(X1, train_param, label='Training data')
        ax.scatter(X2, val_param, color='red', marker='^', label='Validation data')

        poly = PolynomialFeatures(degree=i)
        X_train_poly = poly.fit_transform(X1.reshape(-1, 1))
        X_val_poly = poly.fit_transform(X2.reshape(-1, 1))

        model = LinearRegression()
        model.fit(X_train_poly, train_param)

        train_predictions = model.predict(X_train_poly)
        val_predictions = model.predict(X_val_poly)

        train_rmse.append(np.std(train_predictions - train_param, ddof=1))
        validation_rmse.append(np.std(val_predictions - val_param, ddof=1))
        r2_score = model.score(X_train_poly, train_param)
        r2_score_val = model.score(X_val_poly, val_param)

        sorted_indices = np.argsort(X1)
        X_test_polynomial = X1[sorted_indices]
        predictions = train_predictions[sorted_indices]

        ax.plot(X_test_polynomial, predictions, color=colors[idx], label=f"Degree {i}")
        ax.set_xlabel(xaxis_label)
        ax.set_ylabel(yaxis_label)
        ax.set_title(f"Degree {i}\n$R^2$ train: {r2_score:.2f}, val: {r2_score_val:.2f}")
        ax.legend()

        # Save equation
        coefs = model.coef_
        coefs[0] = model.intercept_
        terms = [f"{coef:.3f}" if power == 0 else f"{coef:.3f}·x^{power}" 
                 for power, coef in enumerate(coefs)]
        equation = " + ".join(terms).replace('+ -', '- ')

        equation_results.append({
            'Parameter': param,
            'Degree': i,
            'Equation': f"y = {equation}",
            'R^2 (Train)': round(r2_score, 4),
            'R^2 (val)': round(r2_score_val, 4)
        })

    for deg, tr_rmse, val_rmse in zip(degrees, train_rmse, validation_rmse):
        rmse_results.append({
            'Parameter': param,
            'Degree': deg,
            'Train_RMSE': tr_rmse,
            'Validation_RMSE': val_rmse
        })

    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.show()

# === Final Tables ===
rmse_df = pd.DataFrame(rmse_results)
equation_df = pd.DataFrame(equation_results)

print("\nRMSE Results:")
print(rmse_df)

print("\nPolynomial Equations and R²:")
print(equation_df)