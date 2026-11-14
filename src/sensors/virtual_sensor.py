import csv
import random
from datetime import datetime, timedelta

# ==========================================
# ECOGRID - RESIDENTIAL SOCIETY SIMULATOR
# ==========================================

random.seed(42)

SOCIETY_NAME = "EcoGrid Green Residency"

BUILDINGS = 5
FLATS_PER_BUILDING = 20
HOURS = 24

VOLTAGE = 230
POWER_FACTOR = 0.95

# Time-based residential demand profile.
# Higher demand in morning and evening.

HOURLY_LOAD_FACTOR = [
    0.30, 0.25, 0.22, 0.20, 0.22, 0.35,
    0.55, 0.75, 0.85, 0.60, 0.45, 0.40,
    0.42, 0.45, 0.40, 0.42, 0.50, 0.70,
    0.95, 1.00, 0.90, 0.75, 0.55, 0.40
]

COMMON_AREAS = [
    "Lift",
    "Corridor_Lights",
    "Water_Pump",
    "Security_System",
    "Clubhouse"
]

COMMON_BASE_POWER = {
    "Lift": 2500,
    "Corridor_Lights": 800,
    "Water_Pump": 3000,
    "Security_System": 400,
    "Clubhouse": 2000
}


def generate_residential_reading(
    building, flat, hour, timestamp
):

    # Each flat has a different typical load.
    base_load = random.uniform(700, 1800)

    load_factor = HOURLY_LOAD_FACTOR[hour]

    # Random variation between flats.
    variation = random.uniform(0.85, 1.15)

    power = base_load * load_factor * variation

    voltage = random.uniform(220, 240)

    current = power / (voltage * POWER_FACTOR)

    energy = power / 1000  # kWh for one hour

    return {
        "society": SOCIETY_NAME,
        "sensor_id": f"B{building}_F{flat}",
        "building": f"Building_{building}",
        "flat": f"Flat_{flat}",
        "sensor_type": "Residential",
        "timestamp": timestamp.isoformat(),
        "voltage_V": round(voltage, 2),
        "current_A": round(current, 2),
        "power_W": round(power, 2),
        "energy_kWh": round(energy, 3),
        "power_factor": POWER_FACTOR
    }


def generate_common_reading(
    building, area, hour, timestamp
):

    base_power = COMMON_BASE_POWER[area]

    variation = random.uniform(0.85, 1.15)

    # Common loads have different schedules.
    if area == "Water_Pump":
        load_factor = 1.0 if hour in [6, 7, 18, 19] else 0.15

    elif area == "Lift":
        load_factor = 0.85 if 6 <= hour <= 22 else 0.25

    elif area == "Corridor_Lights":
        load_factor = 1.0 if hour >= 18 or hour <= 6 else 0.25

    elif area == "Clubhouse":
        load_factor = 0.9 if 17 <= hour <= 22 else 0.1

    else:
        load_factor = 1.0

    power = base_power * load_factor * variation

    voltage = random.uniform(220, 240)

    current = power / (voltage * POWER_FACTOR)

    energy = power / 1000

    return {
        "society": SOCIETY_NAME,
        "sensor_id": f"B{building}_{area}",
        "building": f"Building_{building}",
        "flat": area,
        "sensor_type": "Common_Area",
        "timestamp": timestamp.isoformat(),
        "voltage_V": round(voltage, 2),
        "current_A": round(current, 2),
        "power_W": round(power, 2),
        "energy_kWh": round(energy, 3),
        "power_factor": POWER_FACTOR
    }


def main():

    all_readings = []

    start_time = datetime(2026, 11, 13, 0, 0)

    print("\n====================================")
    print("       ECOGRID SMART SOCIETY")
    print("====================================")

    print("Society:", SOCIETY_NAME)
    print("Buildings:", BUILDINGS)
    print("Flats:", BUILDINGS * FLATS_PER_BUILDING)

    print("\nGenerating virtual sensor readings...")

    for hour in range(HOURS):

        timestamp = start_time + timedelta(hours=hour)

        for building in range(1, BUILDINGS + 1):

            # Residential flat sensors
            for flat in range(1, FLATS_PER_BUILDING + 1):

                reading = generate_residential_reading(
                    building, flat, hour, timestamp
                )

                all_readings.append(reading)

            # Common-area sensors
            for area in COMMON_AREAS:

                reading = generate_common_reading(
                    building, area, hour, timestamp
                )

                all_readings.append(reading)

    # Save all sensor readings in CSV
    filename = "data/raw/society_energy_data.csv"

    with open(filename, "w", newline="") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=all_readings[0].keys()
        )

        writer.writeheader()
        writer.writerows(all_readings)

    # Society energy summary
    total_energy = sum(
        row["energy_kWh"] for row in all_readings
    )

    peak_reading = max(
        all_readings, key=lambda row: row["power_W"]
    )

    print("\n========== SIMULATION RESULTS ==========")

    print("Total virtual sensors:", 125)
    print("Total readings:", len(all_readings))

    print(
        "Total simulated energy:",
        round(total_energy, 2), "kWh"
    )

    print(
        "Highest individual sensor load:",
        peak_reading["power_W"], "W"
    )

    print("Peak sensor:", peak_reading["sensor_id"])

    print("\nCSV saved successfully:", filename)

    print("\nFirst 5 readings:")

    for reading in all_readings[:5]:
        print(reading)


if __name__ == "__main__":
    main()