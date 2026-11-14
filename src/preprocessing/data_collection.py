import csv
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

# ==========================================
# ECOGRID DATA COLLECTION & VALIDATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "raw" / "society_energy_data.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "collection_summary.json"

REQUIRED_COLUMNS = [
    "society", "sensor_id", "building", "flat",
    "sensor_type", "timestamp", "voltage_V",
    "current_A", "power_W", "energy_kWh",
    "power_factor"
]


def collect_data():

    print("\n====================================")
    print("       ECOGRID DATA COLLECTION")
    print("====================================")

    # 1. READ DATA
    with open(INPUT_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        missing_columns = [
            col for col in REQUIRED_COLUMNS
            if col not in (reader.fieldnames or [])
        ]

        if missing_columns:
            raise ValueError(f"Missing CSV columns: {missing_columns}")

        records = list(reader)

    print("\n1. DATA COLLECTION")
    print("Total records collected:", len(records))

    # 2. SENSOR AND BUILDING INFORMATION
    sensors = Counter(row["sensor_id"] for row in records)
    buildings = Counter(row["building"] for row in records)

    print("\n2. SENSOR INFORMATION")
    print("Unique sensors:", len(sensors))
    print("Total buildings:", len(buildings))

    # 3. MISSING VALUES
    missing_values = {}

    for column in REQUIRED_COLUMNS:
        count = sum(
            1 for row in records
            if not (row.get(column) or "").strip()
        )
        missing_values[column] = count

    total_missing = sum(missing_values.values())

    print("\n3. MISSING VALUE VALIDATION")
    print("Total missing values:", total_missing)

    for column, count in missing_values.items():
        print(f"{column}: {count}")

    # 4. DUPLICATE READINGS
    seen = set()
    duplicates = 0

    for row in records:
        key = (row["sensor_id"], row["timestamp"])

        if key in seen:
            duplicates += 1
        else:
            seen.add(key)

    print("\n4. DUPLICATE VALIDATION")
    print("Total duplicate readings:", duplicates)

    # 5. TIMESTAMP VALIDATION
    invalid_timestamps = 0

    for row in records:
        try:
            datetime.fromisoformat(row["timestamp"])
        except (ValueError, TypeError):
            invalid_timestamps += 1

    print("\n5. TIMESTAMP VALIDATION")
    print("Invalid timestamps:", invalid_timestamps)

    # 6. FINAL DATA QUALITY STATUS
    print("\n====================================")
    print("       DATA QUALITY REPORT")
    print("====================================")

    print("Missing values:", total_missing)
    print("Duplicate readings:", duplicates)
    print("Invalid timestamps:", invalid_timestamps)

    status = (
        "SUCCESS"
        if records and total_missing == 0
        and duplicates == 0 and invalid_timestamps == 0
        else "REVIEW REQUIRED"
    )

    print("\nFINAL STATUS:", status)

    # 7. SAVE SUMMARY
    summary = {
        "project": "EcoGrid",
        "society": "EcoGrid Green Residency",
        "total_records": len(records),
        "unique_sensors": len(sensors),
        "total_buildings": len(buildings),
        "missing_values": missing_values,
        "total_missing_values": total_missing,
        "duplicate_readings": duplicates,
        "invalid_timestamps": invalid_timestamps,
        "collection_status": status
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)

    print("\nSummary saved successfully!")
    print(OUTPUT_FILE)
    print("\nECOGRID DATA COLLECTION COMPLETED!")


if __name__ == "__main__":
    collect_data()