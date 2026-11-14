import json
import requests

# Schema Registry URL
url = "http://localhost:8081/subjects/ecogrid-sensor-data-value/versions"

# Read Avro schema
with open("src/sensors/sensor_schema.avsc", "r") as file:
    schema = file.read()

# Prepare request
payload = {
    "schema": schema,
    "schemaType": "AVRO"
}

headers = {
    "Content-Type": "application/vnd.schemaregistry.v1+json"
}

# Register schema
response = requests.post(
    url,
    headers=headers,
    json=payload
)

print("Status Code:", response.status_code)
print("Response:", response.text)