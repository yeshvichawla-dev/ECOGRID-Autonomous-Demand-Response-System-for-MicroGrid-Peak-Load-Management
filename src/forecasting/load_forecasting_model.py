import pandas as pd
import joblib

# Load the saved forecasting model

model_path = "models/energy_forecasting_model.pkl"

loaded_model = joblib.load(model_path)

print("EcoGrid forecasting model loaded successfully!")
print("Model: Linear Regression")


# Load test data

data_path = "data/processed/cleaned_energy_data.csv"

df = pd.read_csv(data_path)

df["timestamp"] = pd.to_datetime(df["timestamp"])

df["hour"] = df["timestamp"].dt.hour
df["day"] = df["timestamp"].dt.day
df["month"] = df["timestamp"].dt.month
df["day_of_week"] = df["timestamp"].dt.day_of_8week

df["is_weekend"] = (
    df["day_of_week"] >= 5
).astype(int)

df["building"] = (
    df["building"].str.extract(r"(\d+)").astype(int)
)

df = df.sort_values(["sensor_id", "timestamp"])

df["previous_hour_energy"] = (
    df.groupby("sensor_id")["energy_kWh"].shift(1)
)

df = df.dropna(subset=["previous_hour_energy"])


# Prepare model features

features = [
    "hour",
    "day",
    "month",
    "day_of_week",
    "is_weekend",
    "building",
    "previous_hour_energy"
]

X = df[features]


# Generate prediction

prediction = loaded_model.predict(X.iloc[[0]])

print("\n========== ENERGY PREDICTION ==========")
print("Predicted Energy Consumption:", prediction[0], "kWh")
print("Actual Energy Consumption:", df["energy_kWh"].iloc[0], "kWh")