from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

# Connect to Schema Registry
schema_registry_client = SchemaRegistryClient({
    "url": "http://localhost:8081"
})

# Create Avro deserializer
avro_deserializer = AvroDeserializer(schema_registry_client)

# Configure Kafka consumer
consumer = Consumer({
    "bootstrap.servers": "localhost:29092",
    "group.id": "ecogrid-flask-verification",
    "auto.offset.reset": "latest"
})

TOPIC = "ecogrid-sensor-data-avro"

consumer.subscribe([TOPIC])

print("EcoGrid Avro Consumer Started!")

try:
    count = 0

    while count < 1:
        message = consumer.poll(1.0)

        if message is None:
            continue

        if message.error():
            print("Consumer error:", message.error())
            continue

        sensor_data = avro_deserializer(
            message.value(),
            SerializationContext(TOPIC, MessageField.VALUE)
        )

        print("\nReceived Sensor Data:")
        print(sensor_data)

        count += 1

    print("\nTotal messages consumed:", count)

finally:
    consumer.close()