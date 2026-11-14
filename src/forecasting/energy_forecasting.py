# ==========================================
# ECOGRID - ENERGY FORECASTING
# ==========================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

import joblib

print("EcoGrid Forecasting Libraries Imported Successfully!")
# ==========================================
# STEP 2: LOAD CLEANED DATASET
# ==========================================

data_path = "data/processed/cleaned_energy_data.csv"

df = pd.read_csv(data_path)

print("\nDataset Loaded Successfully!")
print("Dataset Shape:", df.shape)

print("\nFirst 5 Records:")
print(df.head())

print("\nDataset Information:")
print(df.info())
# ==========================================
# STEP 3: TIMESTAMP FEATURE ENGINEERING
# ==========================================

df["timestamp"] = pd.to_datetime(df["timestamp"])

df["hour"] = df["timestamp"].dt.hour
df["day"] = df["timestamp"].dt.day
df["month"] = df["timestamp"].dt.month
df["day_of_week"] = df["timestamp"].dt.dayofweek
df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

print("\nTimestamp Features Created Successfully!")

print(df[["timestamp", "hour", "day", "month",
          "day_of_week", "is_weekend"]].head())
          # ==========================================
# STEP 4: EXPLORATORY DATA ANALYSIS (EDA)
# DESCRIPTIVE STATISTICS
# ==========================================

print("\n========== ECOGRID EDA ==========")

print("\n1. Numerical Data Summary:")
print(df.describe())

print("\n2. Average Energy Consumption:")
print(df["energy_kWh"].mean())

print("\n3. Maximum Energy Consumption:")
print(df["energy_kWh"].max())

print("\n4. Minimum Energy Consumption:")
print(df["energy_kWh"].min())

print("\n5. Total Energy Consumption:")
print(df["energy_kWh"].sum())
# ==========================================
# STEP 5: BUILDING-WISE ENERGY ANALYSIS
# ==========================================

building_energy = df.groupby("building")["energy_kWh"].sum()

print("\nBuilding-wise Energy Consumption:")
print(building_energy)

print("\nHighest Energy Consuming Building:")
print(building_energy.idxmax())

print("\nLowest Energy Consuming Building:")
print(building_energy.idxmin())
# ==========================================
# STEP 6: BUILDING-WISE ENERGY VISUALIZATION
# ==========================================

plt.figure(figsize=(10, 6))

plt.bar(
    building_energy.index,
    building_energy.values,
    color="skyblue",
    edgecolor="black"
)

plt.title("EcoGrid - Building-wise Energy Consumption")
plt.xlabel("Building")
plt.ylabel("Energy Consumption (kWh)")

plt.ylim(400, 420)

plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig("reports/building_energy.png")
# plt.show()

print("Building Energy Graph Saved Successfully!")

print("Building Energy Graph Saved Successfully!")
# ==========================================
# STEP 7: HOURLY ENERGY CONSUMPTION ANALYSIS
# ==========================================

# Hourly Energy Consumption Analysis

hourly_energy = df.groupby("hour")["energy_kWh"].sum()

print("\nHourly Energy Consumption:")
print(hourly_energy.round(3))

print("\nPeak Consumption Hour:")
print(hourly_energy.idxmax())

print("\nLowest Consumption Hour:")
print(hourly_energy.idxmin())
# Hourly Energy Visualization

plt.figure(figsize=(12, 6))

plt.plot(hourly_energy.index, hourly_energy.values, marker="o")

plt.title("EcoGrid - Hourly Energy Consumption")
plt.xlabel("Hour of the Day")
plt.ylabel("Energy Consumption (kWh)")

plt.xticks(range(24))
plt.grid(True)
plt.tight_layout()

plt.savefig("reports/hourly_energy.png")

print("Hourly Energy Graph Saved Successfully!")
# Correlation Analysis

correlation = df[
    ["voltage_V", "current_A", "power_W",
     "energy_kWh", "power_factor"]
].corr()

print("\n========== CORRELATION ANALYSIS ==========")
print(correlation.round(5))

plt.figure(figsize=(10, 7))

sns.heatmap(
    correlation,
    annot=True,
    cmap="coolwarm",
    fmt=".2f"
)

plt.title("EcoGrid - Feature Correlation Heatmap")
plt.tight_layout()

plt.savefig("reports/correlation_heatmap.png")

print("Correlation Heatmap Saved Successfully!")
# Correlation Data Investigation

print("\n========== DATA RELATIONSHIP CHECK ==========")

print("\nCurrent vs Power:")
print(df[["current_A", "power_W"]].head(10))

print("\nPower vs Energy:")
print(df[["power_W", "energy_kWh"]].head(10))

print("\nVoltage Statistics:")
print(df["voltage_V"].describe())

print("\nCurrent Statistics:")
print(df["current_A"].describe())

print("\nPower Statistics:")
print(df["power_W"].describe())

print("\nEnergy Statistics:")
print(df["energy_kWh"].describe())
# ==========================================
# MACHINE LEARNING - FEATURE SELECTION
# ==========================================

df["building"] = df["building"].str.extract(r"(\d+)").astype(int)
# Previous Hour Energy Consumption

df = df.sort_values(["sensor_id", "timestamp"])

df["previous_hour_energy"] = (
    df.groupby("sensor_id")["energy_kWh"].shift(1)
)

df = df.dropna(subset=["previous_hour_energy"])
features = [
    "hour",
    "day",
    "month",
    "day_of_week",
    "is_weekend",
    "building",
    "previous_hour_energy"
]
target = "energy_kWh"

X = df[features]
y = df[target]

print("\n========== FEATURE SELECTION ==========")
print("Input Features:", X.shape)
print("Target Shape:", y.shape)
print("Features Selected:", features)
# ==========================================
#  CHRONOLOGICAL TRAIN-TEST SPLIT
# ==========================================

unique_times = sorted(df["timestamp"].unique())

split_index = int(len(unique_times) * 0.8)
split_time = unique_times[split_index]

train_mask = df["timestamp"] < split_time
test_mask = df["timestamp"] >= split_time

X_train = X.loc[train_mask]
X_test = X.loc[test_mask]

y_train = y.loc[train_mask]
y_test = y.loc[test_mask]

print("\n========== TRAIN-TEST SPLIT ==========")
print("Training Features:", X_train.shape)
print("Testing Features:", X_test.shape)
print("Training Target:", y_train.shape)
print("Testing Target:", y_test.shape)
print("First 10 Actual Values:")
print(y_test.head(10).values)

# ==========================================
# MODEL 1 - LINEAR REGRESSION
# ==========================================

print("\n========== LINEAR REGRESSION MODEL ==========")

# Create the model
linear_model = LinearRegression()

# Train the model
linear_model.fit(X_train, y_train)

print("Linear Regression Training Completed Successfully!")

# Generate predictions
linear_predictions = linear_model.predict(X_test)

print("\nFirst 10 Predicted Values:")
print(linear_predictions[:10])


# ==========================================
# LINEAR REGRESSION MODEL EVALUATION
# ==========================================

linear_mae = mean_absolute_error(y_test, linear_predictions)

linear_mse = mean_squared_error(y_test, linear_predictions)

linear_rmse = np.sqrt(linear_mse)

linear_r2 = r2_score(y_test, linear_predictions)

print("\n========== LINEAR REGRESSION EVALUATION ==========")

print("MAE:", linear_mae)
print("MSE:", linear_mse)
print("RMSE:", linear_rmse)
print("R2 Score:", linear_r2)


# ==========================================
# BASELINE MODEL - PERSISTENCE
# ==========================================

print("\n========== BASELINE MODEL ==========")

# Use previous hour energy as the prediction
baseline_predictions = X_test["previous_hour_energy"]

# Evaluate baseline
baseline_mae = mean_absolute_error(y_test, baseline_predictions)

baseline_mse = mean_squared_error(y_test, baseline_predictions)

baseline_rmse = np.sqrt(baseline_mse)

baseline_r2 = r2_score(y_test, baseline_predictions)

print("\n========== BASELINE EVALUATION ==========")

print("Baseline MAE:", baseline_mae)
print("Baseline MSE:", baseline_mse)
print("Baseline RMSE:", baseline_rmse)
print("Baseline R2 Score:", baseline_r2)
# ==========================================
# MODEL 2 - DECISION TREE REGRESSOR
# ==========================================

print("\n========== DECISION TREE REGRESSOR ==========")

# Create the model
decision_tree_model = DecisionTreeRegressor(random_state=42)

# Train the model
decision_tree_model.fit(X_train, y_train)

print("Decision Tree Training Completed Successfully!")

# Generate predictions
decision_tree_predictions = decision_tree_model.predict(X_test)

print("\nFirst 10 Predicted Values:")
print(decision_tree_predictions[:10])


# ==========================================
# DECISION TREE MODEL EVALUATION
# ==========================================

dt_mae = mean_absolute_error(y_test, decision_tree_predictions)

dt_mse = mean_squared_error(y_test, decision_tree_predictions)

dt_rmse = np.sqrt(dt_mse)

dt_r2 = r2_score(y_test, decision_tree_predictions)

print("\n========== DECISION TREE EVALUATION ==========")

print("MAE:", dt_mae)
print("MSE:", dt_mse)
print("RMSE:", dt_rmse)
print("R2 Score:", dt_r2)
# ==========================================
# MODEL 3 - RANDOM FOREST REGRESSOR
# ==========================================

print("\n========== RANDOM FOREST REGRESSOR ==========")

# Create the model
random_forest_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

# Train the model
random_forest_model.fit(X_train, y_train)

print("Random Forest Training Completed Successfully!")

# Generate predictions
rf_predictions = random_forest_model.predict(X_test)

print("\nFirst 10 Predicted Values:")
print(rf_predictions[:10])


# ==========================================
# RANDOM FOREST MODEL EVALUATION
# ==========================================

rf_mae = mean_absolute_error(y_test, rf_predictions)

rf_mse = mean_squared_error(y_test, rf_predictions)

rf_rmse = np.sqrt(rf_mse)

rf_r2 = r2_score(y_test, rf_predictions)

print("\n========== RANDOM FOREST EVALUATION ==========")

print("MAE:", rf_mae)
print("MSE:", rf_mse)
print("RMSE:", rf_rmse)
print("R2 Score:", rf_r2)
# ==========================================
# MODEL 4 - GRADIENT BOOSTING REGRESSOR
# ==========================================

print("\n========== GRADIENT BOOSTING REGRESSOR ==========")

# Create the model
gradient_boosting_model = GradientBoostingRegressor(
    n_estimators=100,
    random_state=42
)

# Train the model
gradient_boosting_model.fit(X_train, y_train)

print("Gradient Boosting Training Completed Successfully!")

# Generate predictions
gb_predictions = gradient_boosting_model.predict(X_test)

print("\nFirst 10 Predicted Values:")
print(gb_predictions[:10])


# ==========================================
# GRADIENT BOOSTING MODEL EVALUATION
# ==========================================

gb_mae = mean_absolute_error(y_test, gb_predictions)

gb_mse = mean_squared_error(y_test, gb_predictions)

gb_rmse = np.sqrt(gb_mse)

gb_r2 = r2_score(y_test, gb_predictions)

print("\n========== GRADIENT BOOSTING EVALUATION ==========")

print("MAE:", gb_mae)
print("MSE:", gb_mse)
print("RMSE:", gb_rmse)
print("R2 Score:", gb_r2)
# ==========================================
# FINAL MODEL COMPARISON
# ==========================================

results = [
    {
        "Model": "Linear Regression",
        "MAE": linear_mae,
        "MSE": linear_mse,
        "RMSE": linear_rmse,
        "R2 Score": linear_r2
    },
    {
        "Model": "Decision Tree",
        "MAE": dt_mae,
        "MSE": dt_mse,
        "RMSE": dt_rmse,
        "R2 Score": dt_r2
    },
    {
        "Model": "Random Forest",
        "MAE": rf_mae,
        "MSE": rf_mse,
        "RMSE": rf_rmse,
        "R2 Score": rf_r2
    },
    {
        "Model": "Gradient Boosting",
        "MAE": gb_mae,
        "MSE": gb_mse,
        "RMSE": gb_rmse,
        "R2 Score": gb_r2
    },
    {
        "Model": "Persistence Baseline",
        "MAE": baseline_mae,
        "MSE": baseline_mse,
        "RMSE": baseline_rmse,
        "R2 Score": baseline_r2
    }
]

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="RMSE",
    ascending=True
)

print("\n========== FINAL MODEL COMPARISON ==========")
print(results_df.to_string(index=False))

best_model_name = results_df.iloc[0]["Model"]

print("\nBest Model based on RMSE:", best_model_name)
# ==========================================
# SAVE BEST MODEL
# ==========================================

best_model = linear_model

joblib.dump(
    best_model,
    "models/energy_forecasting_model.pkl"
)

print("\nBest model saved successfully!")