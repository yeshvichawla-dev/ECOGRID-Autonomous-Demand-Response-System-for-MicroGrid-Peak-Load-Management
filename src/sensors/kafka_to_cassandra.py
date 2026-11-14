from datetime import datetime, timezone

from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

from cassandra.cluster import Cluster


# 1. Connect to Cassandra
cluster = Cluster(["localhost"], port=9042)
session = cluster.connect("ecogrid")

insert_query = session.prepare("""
    INSERT INTO sensor_readings (
        sensor_id, reading_time, society, building,
        voltage_V, current_A, power_W, energy_kWh, power_factor
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""")

print("EcoGrid Cassandra connected!")


# 2. Connect to Schema Registry
schema_registry = SchemaRegistryClient({
    "url": "http://localhost:8081"
})

avro_deserializer = AvroDeserializer(schema_registry)


# 3. Connect to Kafka
TOPIC = "ecogrid-sensor-data-avro"

consumer = Consumer({
    "bootstrap.servers": "localhost:29092",
    "group.id": "ecogrid-cassandra-storage",
    "auto.offset.reset": "latest"
})

consumer.subscribe([TOPIC])

print("EcoGrid Kafka-to-Cassandra Consumer Started!")

try:
    while True:
        message = consumer.poll(1.0)

        if message is None:
            continue

        if message.error():
            print("Kafka error:", message.error())
            continue

        sensor_data = avro_deserializer(
            message.value(),
            SerializationContext(TOPIC, MessageField.VALUE)
        )

        timestamp = datetime.fromisoformat(
            sensor_data["timestamp"].replace("Z", "+00:00")
        )

        if timestamp.tzinfo is not None:
            timestamp = timestamp.astimezone(
                timezone.utc
            ).replace(tzinfo=None)

        session.execute(insert_query, (
            sensor_data["sensor_id"],
            timestamp,
            sensor_data["society"],
            sensor_data["building"],
            sensor_data["voltage_V"],
            sensor_data["current_A"],
            sensor_data["power_W"],
            sensor_data["energy_kWh"],
            sensor_data["power_factor"]
        ))

        print(
            "Saved sensor reading:",
            sensor_data["sensor_id"]
        )

except KeyboardInterrupt:
    print("\nConsumer stopped.")

finally:
    consumer.close()
    session.shutdown()
    cluster.shutdown()
    print("EcoGrid connections closed.")