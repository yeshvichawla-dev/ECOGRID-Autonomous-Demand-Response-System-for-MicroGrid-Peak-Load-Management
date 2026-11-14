import pandas as pd
import numpy as np
import casadi as ca

# 1. Load cleaned sensor data
df = pd.read_csv("data/processed/cleaned_energy_data.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.hour

# 2. Calculate total hourly energy demand
hourly_demand = (
    df.groupby("hour")["energy_kWh"]
    .sum()
    .reindex(range(24), fill_value=0)
)

baseline = hourly_demand.to_numpy(dtype=float)

if np.any(baseline <= 0):
    raise ValueError("Expected positive demand for all 24 hours.")

# 3. Define optimization variables
opti = ca.Opti()

optimized_load = opti.variable(24)
peak_load = opti.variable()

# 4. Define flexible-load limits (20% assumption)
lower_limit = 0.80 * baseline
upper_limit = 1.20 * baseline

opti.subject_to(optimized_load >= lower_limit)
opti.subject_to(optimized_load <= upper_limit)

# Preserve total energy consumption
opti.subject_to(ca.sum1(optimized_load) == float(baseline.sum()))

# Peak load must be at least every hourly load
opti.subject_to(optimized_load <= peak_load)

# 5. Objective: reduce peak demand while limiting load changes
deviation = optimized_load - ca.DM(baseline)

objective = (
    peak_load
    + 0.001 * ca.sumsqr(deviation)
)

opti.minimize(objective)

# 6. Solve optimization problem
opti.solver(
    "ipopt",
    {"print_time": False},
    {"print_level": 0}
)

solution = opti.solve()

optimized = np.array(
    solution.value(optimized_load)
).flatten()

# 7. Compare results
print("\n========== ECOGRID OPTIMIZATION ==========")

print("Original total energy:", round(baseline.sum(), 4), "kWh")
print("Optimized total energy:", round(optimized.sum(), 4), "kWh")

print("Original peak demand:", round(baseline.max(), 4), "kWh")
print("Optimized peak demand:", round(optimized.max(), 4), "kWh")

reduction = (
    (baseline.max() - optimized.max())
    / baseline.max()
) * 100

print("Peak demand reduction:", round(reduction, 2), "%")

# 8. Save optimization results
results = pd.DataFrame({
    "hour": range(24),
    "original_energy_kWh": baseline,
    "optimized_energy_kWh": optimized
})

results.to_csv(
    "data/processed/optimization_results.csv",
    index=False
)

print("\nOptimization results saved successfully!")