import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error
from mpl_toolkits.mplot3d import Axes3D
from scipy import stats
from sklearn.model_selection import train_test_split

np.set_printoptions(precision=2)
import warnings
warnings.filterwarnings("ignore")

# === Load and preview data ===
file_path = r"C:\Users\olivi\OneDrive\Aerospace\DSE\DJI Quadcopter database 0-2kg.csv"
raw = pd.read_csv(file_path)
print(raw.head(5))

# === Statistical summary of raw data ===
raw.columns = raw.columns.str.strip().str.lower()

# Clean and convert
for col in ['weight (kg)', 'price ($)', 'advertised flight time (min)',
            'battery capacity (mah)', 'propeller area', 'downwash']:
    raw[col] = pd.to_numeric(raw[col], errors='coerce')

# Drop missing rows for all relevant variables
clean_raw = raw.dropna(subset=['weight (kg)', 'price ($)', 'advertised flight time (min)',
                               'battery capacity (mah)', 'propeller area', 'downwash'])

# Extract individual variables
weights = clean_raw['weight (kg)'].values
prices = clean_raw['price ($)'].values
flight_times = clean_raw['advertised flight time (min)'].values
battery_powers = clean_raw['battery capacity (mah)'].values
propeller_areas = clean_raw['propeller area'].values
downwash = clean_raw['downwash'].values

# === Train-test split ===
train_weight, val_weight, train_price, val_price = train_test_split(weights, prices, test_size=0.4, random_state=42)
_, _, train_ft, val_ft = train_test_split(weights, flight_times, test_size=0.4, random_state=42)
_, _, train_bp, val_bp = train_test_split(weights, battery_powers, test_size=0.4, random_state=42)
_, _, train_prop_area, val_prop_area = train_test_split(weights, propeller_areas, test_size=0.4, random_state=42)
_, _, train_downwash, val_downwash = train_test_split(weights, downwash, test_size=0.4, random_state=42)

# === Polynomial regression analysis ===
params = ['price', 'battery capacity', 'propeller area', 'downwash']
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
    # elif param == 'flight time':
    #     train_param = train_ft
    #     val_param = val_ft
    #     X1 = train_bp
    #     X2 = val_bp
    #     xaxis_label = 'Battery capacity (mAh)'
    #     yaxis_label = 'Flight Time (min)'
    elif param == 'battery capacity':
        train_param = train_bp
        val_param = val_bp
        X1 = train_weight
        X2 = val_weight
        xaxis_label = 'Weight (kg)'
        yaxis_label = 'Battery capacity (mAh)'
    elif param == 'downwash':
        X1 = train_weight
        X2 = val_weight
        train_param = train_downwash
        val_param = val_downwash
        xaxis_label = 'Weight (kg)'
        yaxis_label = 'Downwash (m/s)'
    elif param == 'propeller area':
        train_param = train_prop_area
        val_param = val_prop_area
        X1 = train_weight
        X2 = val_weight
        xaxis_label = 'Weight (kg)'
        yaxis_label = 'Propeller Area (m^2)'

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
        X_val_poly = poly.transform(X2.reshape(-1, 1))

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

# === New Section: Flight Time Prediction from Weight & Battery ===
print("\n=== Flight Time Prediction: Weight & Battery Capacity ===")
X_full = clean_raw[['weight (kg)', 'battery capacity (mah)']].values
y_full = clean_raw['advertised flight time (min)'].values

X_train, X_val, y_train, y_val = train_test_split(X_full, y_full, test_size=0.4, random_state=42)

for degree in [1, 2]:
    poly = PolynomialFeatures(degree=degree)
    X_train_poly = poly.fit_transform(X_train)
    X_val_poly = poly.transform(X_val)

    model = LinearRegression()
    model.fit(X_train_poly, y_train)

    y_train_pred = model.predict(X_train_poly)
    y_val_pred = model.predict(X_val_poly)

    rmse_train = mean_squared_error(y_train, y_train_pred, squared=False)
    rmse_val = mean_squared_error(y_val, y_val_pred, squared=False)
    r2_train = model.score(X_train_poly, y_train)
    r2_val = model.score(X_val_poly, y_val)

    print(f"\nPolynomial Degree {degree}:")
    print(f"  Train RMSE = {rmse_train:.2f}, R² = {r2_train:.2f}")
    print(f"  Validation RMSE = {rmse_val:.2f}, R² = {r2_val:.2f}")

    # Equation
    feature_names = poly.get_feature_names_out(['weight', 'battery'])
    coefs = model.coef_
    coefs[0] = model.intercept_
    equation = " + ".join([f"{coef:.3e}*{name}" if name != "1" else f"{coef:.3e}" 
                           for coef, name in zip(coefs, feature_names)])
    print(f"  Equation: y = {equation}")

    # 3D plot
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X_val[:, 0], X_val[:, 1], y_val, c='red', marker='^', label='Validation Data')
    ax.scatter(X_train[:, 0], X_train[:, 1], y_train_pred, c='green', marker='o', label='Predicted (Train)')

    ax.set_xlabel('Weight (kg)')
    ax.set_ylabel('Battery Capacity (mAh)')
    ax.set_zlabel('Flight Time (min)')
    ax.set_title(f'Flight Time Prediction (Degree {degree})')
    ax.legend()
    plt.tight_layout()
    plt.show()

# === Summary Tables ===
rmse_df = pd.DataFrame(rmse_results)
equation_df = pd.DataFrame(equation_results)

print("\nRMSE Results:")
print(rmse_df)

print("\nPolynomial Equations and R²:")
print(equation_df)
