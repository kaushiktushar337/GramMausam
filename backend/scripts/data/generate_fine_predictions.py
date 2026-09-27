from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

TRAINING_FILE = BASE_DIR / "data" / "processed" / (
    "gfs_chirps_training_up_2025-07.csv"
)

ELEVATION_FILE = BASE_DIR / "data" / "processed" / (
    "fine_grid_elevation_up_complete.csv"
)

MODEL_FILE = BASE_DIR / "models" / (
    "grammausam_rainfall_downscaler.joblib"
)

OUTPUT_FILE = BASE_DIR / "data" / "processed" / (
    "fine_predictions_july2025_test.csv"
)


# ============================================================
# TEST DATES
# ============================================================

TEST_START = pd.Timestamp("2025-07-27")
TEST_END = pd.Timestamp("2025-07-31")


# ============================================================
# LOAD MODEL
# ============================================================

print("=" * 60)
print("Loading trained downscaling model...")
print("=" * 60)

bundle = joblib.load(MODEL_FILE)

model = bundle["model"]
FEATURES = bundle["features"]

print("Model loaded.")
print(f"Features: {FEATURES}")


# ============================================================
# LOAD TRAINING GRID
# ============================================================

print()
print("=" * 60)
print("Loading fine-grid forecast data...")
print("=" * 60)

training = pd.read_csv(
    TRAINING_FILE,
    usecols=[
        "date",
        "coarse_lat",
        "coarse_lon",
        "fine_lat",
        "fine_lon",
        "gfs_rainfall",
    ],
)

training["date"] = pd.to_datetime(
    training["date"]
)

for col in [
    "coarse_lat",
    "coarse_lon",
    "fine_lat",
    "fine_lon",
    "gfs_rainfall",
]:
    training[col] = pd.to_numeric(
        training[col],
        errors="coerce"
    )


# Keep only test dates
prediction = training[
    (training["date"] >= TEST_START)
    &
    (training["date"] <= TEST_END)
].copy()


print(
    f"Test-period rows: {len(prediction):,}"
)

print(
    f"Test dates: {prediction['date'].nunique()}"
)


# ============================================================
# LOAD ELEVATION
# ============================================================

print()
print("=" * 60)
print("Loading elevation...")
print("=" * 60)

elevation = pd.read_csv(
    ELEVATION_FILE
)

elevation = elevation[
    [
        "fine_lat",
        "fine_lon",
        "elevation_m",
        "elevation_source",
        "nearest_known_distance_deg",
    ]
].copy()

for col in [
    "fine_lat",
    "fine_lon",
    "elevation_m",
    "nearest_known_distance_deg",
]:
    elevation[col] = pd.to_numeric(
        elevation[col],
        errors="coerce"
    )

elevation["fine_lat"] = elevation[
    "fine_lat"
].round(6)

elevation["fine_lon"] = elevation[
    "fine_lon"
].round(6)

elevation = elevation.drop_duplicates(
    subset=[
        "fine_lat",
        "fine_lon",
    ]
)


# ============================================================
# ROBUST GRID-KEY MERGE
# ============================================================

print()
print("=" * 60)
print("Merging elevation using grid keys...")
print("=" * 60)


# Normalize coordinates to exactly six decimal places.
prediction["fine_lat"] = pd.to_numeric(
    prediction["fine_lat"],
    errors="coerce"
).round(6)

prediction["fine_lon"] = pd.to_numeric(
    prediction["fine_lon"],
    errors="coerce"
).round(6)

elevation["fine_lat"] = pd.to_numeric(
    elevation["fine_lat"],
    errors="coerce"
).round(6)

elevation["fine_lon"] = pd.to_numeric(
    elevation["fine_lon"],
    errors="coerce"
).round(6)


def make_grid_key(lat, lon):
    return f"{lat:.6f}|{lon:.6f}"


prediction["_grid_key"] = [
    make_grid_key(lat, lon)
    for lat, lon in zip(
        prediction["fine_lat"],
        prediction["fine_lon"]
    )
]

elevation["_grid_key"] = [
    make_grid_key(lat, lon)
    for lat, lon in zip(
        elevation["fine_lat"],
        elevation["fine_lon"]
    )
]


# Keep only the elevation information needed for the model.
elevation_lookup = elevation[
    [
        "_grid_key",
        "elevation_m",
        "elevation_source",
        "nearest_known_distance_deg",
    ]
].drop_duplicates(
    subset=["_grid_key"]
)


print(
    f"Unique elevation grid keys: "
    f"{len(elevation_lookup):,}"
)


prediction = prediction.merge(
    elevation_lookup,
    on="_grid_key",
    how="left",
    validate="many_to_one",
)


missing_elevation = (
    prediction["elevation_m"]
    .isna()
    .sum()
)

print(
    f"Missing elevation: "
    f"{missing_elevation:,}"
)


# Helpful diagnostic if anything still fails.
if missing_elevation > 0:

    unmatched = prediction[
        prediction["elevation_m"].isna()
    ][
        [
            "fine_lat",
            "fine_lon",
            "_grid_key",
        ]
    ].head(10)

    print()
    print("First unmatched coordinates:")
    print(unmatched.to_string(index=False))

    raise ValueError(
        "Some fine-grid coordinates still do not "
        "match the elevation grid."
    )


prediction = prediction.drop(
    columns=["_grid_key"]
)


# ============================================================
# FEATURE ENGINEERING
# ============================================================

prediction["elevation_interpolated"] = (
    prediction["elevation_source"]
    == "local_idw_interpolation"
).astype(np.int8)


prediction["nearest_known_distance_deg"] = (
    prediction["nearest_known_distance_deg"]
    .fillna(999.0)
)


prediction["fine_offset_lat"] = (
    prediction["fine_lat"]
    - prediction["coarse_lat"]
)

prediction["fine_offset_lon"] = (
    prediction["fine_lon"]
    - prediction["coarse_lon"]
)


# ============================================================
# CLEAN
# ============================================================

prediction = prediction.dropna(
    subset=FEATURES
).copy()


# ============================================================
# GENERATE MODEL PREDICTIONS
# ============================================================

print()
print("=" * 60)
print("Generating fine-grid predictions...")
print("=" * 60)

prediction["downscaled_rainfall_mm"] = model.predict(
    prediction[FEATURES]
)

prediction["downscaled_rainfall_mm"] = np.maximum(
    prediction["downscaled_rainfall_mm"],
    0
)


# ============================================================
# KEEP USEFUL COLUMNS
# ============================================================

prediction = prediction[
    [
        "date",
        "coarse_lat",
        "coarse_lon",
        "fine_lat",
        "fine_lon",
        "gfs_rainfall",
        "elevation_m",
        "downscaled_rainfall_mm",
    ]
].copy()


prediction = prediction.sort_values(
    [
        "date",
        "fine_lat",
        "fine_lon",
    ]
).reset_index(drop=True)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("FINE-GRID PREDICTION SUMMARY")
print("=" * 60)

print(
    f"Rows: {len(prediction):,}"
)

print(
    f"Dates: {prediction['date'].nunique()}"
)

print(
    f"Fine cells: "
    f"{prediction[['fine_lat', 'fine_lon']].drop_duplicates().shape[0]:,}"
)

print(
    f"GFS rainfall min: "
    f"{prediction['gfs_rainfall'].min():.2f} mm"
)

print(
    f"GFS rainfall max: "
    f"{prediction['gfs_rainfall'].max():.2f} mm"
)

print(
    f"Downscaled min: "
    f"{prediction['downscaled_rainfall_mm'].min():.2f} mm"
)

print(
    f"Downscaled max: "
    f"{prediction['downscaled_rainfall_mm'].max():.2f} mm"
)

print(
    f"Downscaled mean: "
    f"{prediction['downscaled_rainfall_mm'].mean():.2f} mm"
)


# ============================================================
# SAVE
# ============================================================

prediction.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("=" * 60)
print("DONE")
print("=" * 60)

print(
    f"Output: {OUTPUT_FILE}"
)