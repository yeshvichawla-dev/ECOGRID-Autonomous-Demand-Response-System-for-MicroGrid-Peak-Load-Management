from flask import Flask, jsonify, request, send_from_directory
import joblib
import pandas as pd
from pathlib import Path

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField


app = Flask(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "cleaned_energy_data.csv"
MODEL_FILE = PROJECT_ROOT / "models" / "energy_forecasting_model.pkl"
SCHEMA_FILE = PROJECT_ROOT / "src" / "sensors" / "sensor_schema.avsc"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"


# Load trained forecasting model
model = joblib.load(MODEL_FILE)


# Kafka Configuration
TOPIC = "ecogrid-sensor-data-avro"

schema_registry_client = SchemaRegistryClient({
    "url": "http://localhost:8081"
})

with open(SCHEMA_FILE, "r") as file:
    schema_str = file.read()

avro_serializer = AvroSerializer(
    schema_registry_client,
    schema_str
)

kafka_producer = Producer({
    "bootstrap.servers": "localhost:29092"
})

print("EcoGrid Kafka connection configured!")


# Home API
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "project": "EcoGrid",
        "message": "EcoGrid Forecasting API is Running!",
        "status": "Success"
    })


# Serve dashboard
@app.route("/dashboard", methods=["GET"])
def dashboard():
    return send_from_directory(DASHBOARD_DIR, "index.html")


# Serve dashboard files
@app.route("/dashboard/<path:filename>", methods=["GET"])
def dashboard_files(filename):
    return send_from_directory(DASHBOARD_DIR, filename)

# Dashboard Data API
@app.route("/api/dashboard-data", methods=["GET"])
def dashboard_data():

    try:
        if not DATA_FILE.exists():
            return jsonify({
                "status": "Error",
                "message": "Cleaned energy dataset not found."
            }), 404

        df = pd.read_csv(DATA_FILE)

        required_columns = [
            "sensor_id",
            "building",
            "timestamp",
            "voltage_V",
            "current_A",
            "power_W",
            "energy_kWh"
        ]

        missing_columns = [
            column for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            return jsonify({
                "status": "Error",
                "message": "Dataset is missing required columns.",
                "missing_columns": missing_columns
            }), 400

        # Prepare timestamps
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        df = df.dropna(subset=["timestamp"])

        if df.empty:
            return jsonify({
                "status": "Error",
            }), 400

        # Convert numerical columns
        numeric_columns = [
            "voltage_V",
            "current_A",
            "power_W",
            "energy_kWh"
        ]

        for column in numeric_columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        df = df.dropna(subset=numeric_columns)

        if df.empty:
            return jsonify({
                "status": "Error",
                "message": "No valid numerical sensor readings found."
            }), 400

        # Overall energy statistics
        total_energy = float(df["energy_kWh"].sum())

        # Aggregate energy by hour
        df["hour_timestamp"] = df["timestamp"].dt.floor("h")

        hourly_data = (
            df.groupby("hour_timestamp")["energy_kWh"]
            .sum()
            .sort_index()
        )

        hourly_labels = [
            timestamp.strftime("%H:%M")
            for timestamp in hourly_data.index
        ]

        hourly_energy = [
            float(value)
            for value in hourly_data.values
        ]

        peak_hourly_energy = (
            float(hourly_data.max()) if not hourly_data.empty else 0.0
        )

        # Latest reading for each sensor
        latest_sensors = (
            df.sort_values("timestamp")
            .drop_duplicates(subset=["sensor_id"], keep="last")
            .sort_values("timestamp", ascending=False)
            .head(10)
        )

        sensors = []

        for _, row in latest_sensors.iterrows():
            sensors.append({
                "sensor_id": str(row["sensor_id"]),
                "building": str(row["building"]),
                "voltage_V": float(row["voltage_V"]),
                "current_A": float(row["current_A"]),
                "power_W": float(row["power_W"]),
                "energy_kWh": float(row["energy_kWh"])
            })

        return jsonify({
            "project": "EcoGrid",
            "status": "Success",
            "total_energy_kwh": total_energy,
            "peak_hourly_energy_kwh": peak_hourly_energy,
            "active_sensors": int(df["sensor_id"].nunique()),
            "hourly_labels": hourly_labels,
            "hourly_energy": hourly_energy,
            "sensors": sensors
        })

    except Exception as error:
        return jsonify({
            "project": "EcoGrid",
            "status": "Error",
            "message": str(error)
        }), 500


# Energy Prediction API
@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    features = [
        "hour",
        "day",
        "month",
        "day_of_week",
        "is_weekend",
        "building",
        "previous_hour_energy"
    ]

    input_data = pd.DataFrame(
        [[data[feature] for feature in features]],
        columns=features
    )

    prediction = model.predict(input_data)

    return jsonify({
        "project": "EcoGrid",
        "predicted_energy_kWh": float(prediction[0]),
        "status": "Success"
    })


# Kafka Sensor Data API
@app.route("/sensor-data", methods=["POST"])
def receive_sensor_data():

    data = request.get_json(silent=True) or {}

    required_fields = [
        "society", "sensor_id", "building", "timestamp",
        "voltage_V", "current_A", "power_W",
        "energy_kWh", "power_factor"
    ]

    missing_fields = [
        field for field in required_fields if field not in data
    ]

    if missing_fields:
        return jsonify({
            "status": "Error",
            "missing_fields": missing_fields
        }), 400

    sensor_data = {
        "society": str(data["society"]),
        "sensor_id": str(data["sensor_id"]),
        "building": str(data["building"]),
        "timestamp": str(data["timestamp"]),
        "voltage_V": float(data["voltage_V"]),
        "current_A": float(data["current_A"]),
        "power_W": float(data["power_W"]),
        "energy_kWh": float(data["energy_kWh"]),
        "power_factor": float(data["power_factor"])
    }

    try:
        serialized_data = avro_serializer(
            sensor_data,
            SerializationContext(TOPIC, MessageField.VALUE)
        )

        kafka_producer.produce(
            TOPIC,
            value=serialized_data
        )

        remaining = kafka_producer.flush(10)

        if remaining:
            return jsonify({
                "status": "Error",
                "message": "Kafka delivery timed out"
            }), 503

        return jsonify({
            "project": "EcoGrid",
            "status": "Success",
            "message": "Sensor data sent to Kafka!",
            "topic": TOPIC
        }), 200

    except Exception as error:
        return jsonify({
            "status": "Error",
            "message": str(error)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)