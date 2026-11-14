import pandas as pd
import numpy as np
import json
from pathlib import Path

# PROJECT PATHS
BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "raw" / "Society_energy_data.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# LOAD DATA
df = pd.read_csv(INPUT_FILE)

print("\n========== ECOGRID DATA PROCESSING ==========")

# 1. INITIAL INFORMATION
original_records = len(df)

print("\n1. ORIGINAL DATA")
print("Total records:", original_records)
print("Columns:", df.columns.tolist())

# 2. MISSING VALUE ANALYSIS
missing_before = int(df.isnull().sum().sum())

print("\n2. MISSING VALUES")
print(df.isnull().sum())

# Fill missing numerical values with column median
for col in df.select_dtypes(include=np.number).columns:
    df[col] = df[col].fillna(df[col].median())

# Fill missing text values
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].fillna("Unknown")

missing_after = int(df.isnull().sum().sum())

# 3. DUPLICATE REMOVAL
duplicates_before = int(df.duplicated().sum())
df = df.drop_duplicates()
duplicates_removed = original_records - len(df) if duplicates_before else 0

# 4. TIMESTAMP VALIDATION
timestamp_col = next(
    (c for c in df.columns if "timestamp" in c.lower() or "datetime" in c.lower()),
    None
)

invalid_timestamps = 0

if timestamp_col:
    df[timestamp_col] = pd.to_datetime(
        df[timestamp_col], errors="coerce"
    )
    invalid_timestamps = int(df[timestamp_col].isna().sum())
    df = df.dropna(subset=[timestamp_col])

# 5. OUTLIER DETECTION
numeric_cols = df.select_dtypes(include=np.number).columns
outlier_summary = {}

for col in numeric_cols:
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outlier_summary[col] = int(
        ((df[col] < lower) | (df[col] > upper)).sum()
    )

# 6. BUILDING-WISE ANALYSIS
building_col = next(
    (c for c in df.columns if "building" in c.lower()),
    None
)

energy_col = next(
    (c for c in df.columns
     if "energy" in c.lower() and "kwh" in c.lower()),
    None
)

building_summary = {}

if building_col and energy_col:
    building_summary = (
        df.groupby(building_col)[energy_col]
        .sum()
        .round(2)
        .to_dict()
    )

# 7. SAVE CLEAN DATA
CLEAN_FILE = OUTPUT_DIR / "cleaned_energy_data.csv"
df.to_csv(CLEAN_FILE, index=False)

# 8. PROCESSING REPORT
summary = {
    "project": "EcoGrid",
    "status": "success",
    "original_records": original_records,
    "processed_records": len(df),
    "missing_values_before": missing_before,
    "missing_values_after": missing_after,
    "duplicates_found": duplicates_before,
    "duplicates_removed": duplicates_before,
    "invalid_timestamps": invalid_timestamps,
    "outliers_detected": outlier_summary,
    "building_energy_consumption": building_summary,
    "cleaned_dataset": str(CLEAN_FILE)
}

REPORT_FILE = OUTPUT_DIR / "processing_report.json"

with open(REPORT_FILE, "w", encoding="utf-8") as file:
    json.dump(summary, file, indent=4, default=str)

print("\n========== PROCESSING SUMMARY ==========")
print(json.dumps(summary, indent=4, default=str))
print("\nCLEANED DATA SAVED SUCCESSFULLY!")
print("ECOGRID DATA PROCESSING COMPLETED!")