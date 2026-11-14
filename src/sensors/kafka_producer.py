import json
import pandas as pd

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField

# Kafka topic
TOPIC = "ecogrid-sensor-data-avro"

# Connect to Schema Registry
schema_registry_conf = {
    "url": "http://localhost:8081"
}

schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Load Avro schema
with open("src/sensors/sensor_schema.avsc", "r") as file:
    schema_str = file.read()

# Create Avro serializer
avro_serializer = AvroSerializer(
    schema_registry_client,
    schema_str
)

# Connect to Kafka
producer = Producer({
    "bootstrap.servers": "localhost:29092"
})

# Read cleaned sensor data
df = pd.read_csv("data/processed/cleaned_energy_data.csv")

# Send records
for _, row in df.iterrows():

    sensor_data = {
        "society": str(row["society"]),
        "sensor_id": str(row["sensor_id"]),
        "building": str(row["building"]),
        "timestamp": str(row["timestamp"]),
        "voltage_V": float(row["voltage_V"]),
        "current_A": float(row["current_A"]),
        "power_W": float(row["power_W"]),
        "energy_kWh": float(row["energy_kWh"]),
        "power_factor": float(row["power_factor"])
    }

    serialized_data = avro_serializer(
        sensor_data,
        SerializationContext(TOPIC, MessageField.VALUE)
    )

    producer.produce(
        TOPIC,
        value=serialized_data
    )

    producer.poll(0)

remaining = producer.flush(30)

if remaining == 0:
    print("EcoGrid Avro messages successfully sent!")
    print("Total records sent:", len(df))
else:
    print("Messages still waiting:", remaining)