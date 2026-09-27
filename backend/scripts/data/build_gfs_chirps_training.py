from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

GFS_FILE = BASE_DIR / "data" / "processed" / (
    "gfs_previous_day1_up_2025-07_complete.csv"
)

CHIRPS_FILE = BASE_DIR / "data" / "processed" / (
    "india_chirps_daily_2025-07.csv"
)

OUTPUT_FILE = BASE_DIR / "data" / "processed" / (
    "gfs_chirps_training_up_2025-07.csv"
)


# ============================================================
# UP WORKING DOMAIN
# ============================================================

LAT_MIN = 23.875
LAT_MAX = 30.375
LON_MIN = 77.125
LON_MAX = 84.375

GRID_STEP = 0.25


# ============================================================
# HELPER
# ============================================================

def find_column(df, candidates, label):
    """
    Find the first matching column from a list of candidates.
    """
    for col in candidates:
        if col in df.columns:
            return col

    raise ValueError(
        f"Could not find {label} column.\n"
        f"Available columns:\n{list(df.columns)}"
    )


# ============================================================
# LOAD GFS
# ============================================================

print("=" * 60)
print("Loading GFS forecast data...")
print("=" * 60)

gfs = pd.read_csv(GFS_FILE)

print(f"GFS rows: {len(gfs):,}")
print("GFS columns:")
print(list(gfs.columns))


gfs_date_col = find_column(
    gfs,
    ["date", "valid_date", "forecast_date"],
    "GFS date"
)

gfs_lat_col = find_column(
    gfs,
    ["requested_latitude", "latitude", "lat"],
    "GFS latitude"
)

gfs_lon_col = find_column(
    gfs,
    ["requested_longitude", "longitude", "lon"],
    "GFS longitude"
)

gfs_rain_col = find_column(
    gfs,
    [
        "forecast_rainfall_mm",
        "forecast_rainfall",
        "rainfall",
        "precipitation",
        "forecast_precipitation",
    ],
    "GFS rainfall"
)


gfs = gfs.rename(
    columns={
        gfs_date_col: "date",
        gfs_lat_col: "coarse_lat",
        gfs_lon_col: "coarse_lon",
        gfs_rain_col: "gfs_rainfall",
    }
)


gfs["date"] = pd.to_datetime(gfs["date"]).dt.strftime("%Y-%m-%d")

gfs["coarse_lat"] = pd.to_numeric(gfs["coarse_lat"], errors="coerce")
gfs["coarse_lon"] = pd.to_numeric(gfs["coarse_lon"], errors="coerce")
gfs["gfs_rainfall"] = pd.to_numeric(
    gfs["gfs_rainfall"],
    errors="coerce"
)


gfs = gfs.dropna(
    subset=["date", "coarse_lat", "coarse_lon", "gfs_rainfall"]
)


# Restrict to working domain
gfs = gfs[
    (gfs["coarse_lat"] >= LAT_MIN)
    & (gfs["coarse_lat"] <= LAT_MAX)
    & (gfs["coarse_lon"] >= LON_MIN)
    & (gfs["coarse_lon"] <= LON_MAX)
].copy()


# Avoid floating-point join problems
gfs["coarse_lat"] = gfs["coarse_lat"].round(6)
gfs["coarse_lon"] = gfs["coarse_lon"].round(6)


print(f"GFS rows after domain filter: {len(gfs):,}")
print(f"GFS unique grid points: "
      f"{gfs[['coarse_lat', 'coarse_lon']].drop_duplicates().shape[0]:,}")
print(f"GFS rainfall min: {gfs['gfs_rainfall'].min():.3f} mm")
print(f"GFS rainfall max: {gfs['gfs_rainfall'].max():.3f} mm")


# ============================================================
# LOAD CHIRPS
# ============================================================

print()
print("=" * 60)
print("Loading CHIRPS rainfall data...")
print("=" * 60)

chirps = pd.read_csv(CHIRPS_FILE)

print(f"CHIRPS rows: {len(chirps):,}")
print("CHIRPS columns:")
print(list(chirps.columns))


chirps_date_col = find_column(
    chirps,
    ["date", "valid_date"],
    "CHIRPS date"
)

chirps_lat_col = find_column(
    chirps,
    ["latitude", "lat"],
    "CHIRPS latitude"
)

chirps_lon_col = find_column(
    chirps,
    ["longitude", "lon"],
    "CHIRPS longitude"
)

chirps_rain_col = find_column(
    chirps,
    [
        "rainfall_mm",
        "rainfall",
        "precipitation",
    ],
    "CHIRPS rainfall"
)


chirps = chirps.rename(
    columns={
        chirps_date_col: "date",
        chirps_lat_col: "fine_lat",
        chirps_lon_col: "fine_lon",
        chirps_rain_col: "chirps_rainfall",
    }
)


chirps["date"] = pd.to_datetime(
    chirps["date"]
).dt.strftime("%Y-%m-%d")

chirps["fine_lat"] = pd.to_numeric(
    chirps["fine_lat"],
    errors="coerce"
)

chirps["fine_lon"] = pd.to_numeric(
    chirps["fine_lon"],
    errors="coerce"
)

chirps["chirps_rainfall"] = pd.to_numeric(
    chirps["chirps_rainfall"],
    errors="coerce"
)


chirps = chirps.dropna(
    subset=["date", "fine_lat", "fine_lon", "chirps_rainfall"]
)


# ============================================================
# FILTER CHIRPS TO GFS WORKING DOMAIN
# ============================================================

chirps = chirps[
    (chirps["fine_lat"] >= LAT_MIN)
    & (chirps["fine_lat"] <= LAT_MAX)
    & (chirps["fine_lon"] >= LON_MIN)
    & (chirps["fine_lon"] <= LON_MAX)
].copy()


print(f"CHIRPS rows after domain filter: {len(chirps):,}")
print(f"Fine grid points: "
      f"{chirps[['fine_lat', 'fine_lon']].drop_duplicates().shape[0]:,}")


# ============================================================
# MAP EACH CHIRPS FINE CELL TO THE NEAREST GFS COARSE CELL
# ============================================================

print()
print("=" * 60)
print("Mapping CHIRPS fine cells to GFS coarse cells...")
print("=" * 60)

gfs_lats = np.sort(gfs["coarse_lat"].unique())
gfs_lons = np.sort(gfs["coarse_lon"].unique())


def nearest_grid(value, grid):
    """
    Find nearest coordinate from the GFS grid.
    """
    idx = np.abs(grid - value).argmin()
    return grid[idx]


chirps["coarse_lat"] = chirps["fine_lat"].map(
    lambda x: nearest_grid(x, gfs_lats)
)

chirps["coarse_lon"] = chirps["fine_lon"].map(
    lambda x: nearest_grid(x, gfs_lons)
)


chirps["coarse_lat"] = chirps["coarse_lat"].round(6)
chirps["coarse_lon"] = chirps["coarse_lon"].round(6)


print("Spatial mapping complete.")


# ============================================================
# KEEP ONLY DATES + GRID POINTS PRESENT IN BOTH DATASETS
# ============================================================

print()
print("=" * 60)
print("Joining GFS forecasts with CHIRPS reference rainfall...")
print("=" * 60)


gfs_join = gfs[
    [
        "date",
        "coarse_lat",
        "coarse_lon",
        "gfs_rainfall",
    ]
].copy()


training = chirps.merge(
    gfs_join,
    on=["date", "coarse_lat", "coarse_lon"],
    how="inner",
)


# ============================================================
# FINAL DATASET
# ============================================================

training = training[
    [
        "date",
        "coarse_lat",
        "coarse_lon",
        "fine_lat",
        "fine_lon",
        "gfs_rainfall",
        "chirps_rainfall",
    ]
].copy()


training = training.sort_values(
    ["date", "coarse_lat", "coarse_lon", "fine_lat", "fine_lon"]
).reset_index(drop=True)


# ============================================================
# VALIDATION
# ============================================================

print()
print("=" * 60)
print("TRAINING DATASET SUMMARY")
print("=" * 60)

print(f"Training rows: {len(training):,}")

print(
    f"Unique dates: "
    f"{training['date'].nunique()}"
)

print(
    f"Unique coarse cells: "
    f"{training[['coarse_lat', 'coarse_lon']].drop_duplicates().shape[0]:,}"
)

print(
    f"Unique fine cells: "
    f"{training[['fine_lat', 'fine_lon']].drop_duplicates().shape[0]:,}"
)

print(
    f"Date range: "
    f"{training['date'].min()} → {training['date'].max()}"
)

print()
print("Missing values:")
print(training.isna().sum())


# ============================================================
# BASELINE
# ============================================================

print()
print("=" * 60)
print("COARSE-FORECAST BASELINE")
print("=" * 60)

y_true = training["chirps_rainfall"]
y_pred = training["gfs_rainfall"]


mae = mean_absolute_error(y_true, y_pred)

rmse = np.sqrt(
    mean_squared_error(y_true, y_pred)
)


print(f"Baseline MAE : {mae:.4f} mm")
print(f"Baseline RMSE: {rmse:.4f} mm")


# Rain-event classification baseline
threshold = 1.0

actual_event = y_true >= threshold
predicted_event = y_pred >= threshold

hits = ((actual_event == True) &
        (predicted_event == True)).sum()

false_alarms = ((actual_event == False) &
                (predicted_event == True)).sum()

misses = ((actual_event == True) &
          (predicted_event == False)).sum()

correct_negative = ((actual_event == False) &
                    (predicted_event == False)).sum()


total = len(training)

accuracy = (
    (hits + correct_negative) / total
    if total > 0 else 0
)

precision = (
    hits / (hits + false_alarms)
    if (hits + false_alarms) > 0 else 0
)

recall = (
    hits / (hits + misses)
    if (hits + misses) > 0 else 0
)


print()
print(f"Rain event threshold: {threshold} mm")

print(f"Event Accuracy : {accuracy:.4f}")
print(f"Event Precision: {precision:.4f}")
print(f"Event Recall   : {recall:.4f}")


# ============================================================
# SAVE
# ============================================================

training.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("=" * 60)
print("DONE")
print("=" * 60)
print(f"Output: {OUTPUT_FILE}")