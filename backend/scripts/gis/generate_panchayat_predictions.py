from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CENTROIDS_FILE = (
    BASE_DIR
    / "data"
    / "gis"
    / "panchayat_centroids.csv"
)

GFS_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gfs_previous_day1_up_2025-07_complete.csv"
)

ELEVATION_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "fine_grid_elevation_up_complete.csv"
)

MODEL_FILE = (
    BASE_DIR
    / "models"
    / "grammausam_rainfall_downscaler.joblib"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "panchayat_predictions_july2025_test.csv"
)


# ============================================================
# TEST DATES
# ============================================================

TEST_START = pd.Timestamp("2025-07-27")
TEST_END = pd.Timestamp("2025-07-31")


# ============================================================
# MODEL DOMAIN
# ============================================================

MIN_LAT = 23.875
MAX_LAT = 30.375
MIN_LON = 77.125
MAX_LON = 84.375


# ============================================================
# LOAD MODEL
# ============================================================

print("=" * 60)
print("LOADING DOWNSCALING MODEL")
print("=" * 60)

bundle = joblib.load(
    MODEL_FILE
)

model = bundle["model"]
FEATURES = bundle["features"]

print("Model loaded.")

print(
    "Features:"
)

for feature in FEATURES:
    print(f"  - {feature}")


# ============================================================
# LOAD PANCHAYAT CENTROIDS
# ============================================================

print()
print("=" * 60)
print("LOADING PANCHAYAT CENTROIDS")
print("=" * 60)

panchayats = pd.read_csv(
    CENTROIDS_FILE
)

required_panchayat_columns = [
    "gpcode",
    "gpname",
    "district_code",
    "district",
    "block_code",
    "block",
    "centroid_lat",
    "centroid_lon",
]

missing = [
    col
    for col in required_panchayat_columns
    if col not in panchayats.columns
]

if missing:
    raise ValueError(
        f"Missing Panchayat columns: {missing}"
    )


for col in [
    "centroid_lat",
    "centroid_lon",
]:

    panchayats[col] = pd.to_numeric(
        panchayats[col],
        errors="coerce"
    )


panchayats = panchayats.dropna(
    subset=[
        "gpcode",
        "centroid_lat",
        "centroid_lon",
    ]
).copy()


print(
    f"Total Panchayats: "
    f"{len(panchayats):,}"
)


# ============================================================
# CHECK CENTROID DOMAIN
# ============================================================

inside_domain = (
    (panchayats["centroid_lat"] >= MIN_LAT)
    &
    (panchayats["centroid_lat"] <= MAX_LAT)
    &
    (panchayats["centroid_lon"] >= MIN_LON)
    &
    (panchayats["centroid_lon"] <= MAX_LON)
)

outside_count = (~inside_domain).sum()

print(
    f"Centroids inside model domain: "
    f"{inside_domain.sum():,}"
)

print(
    f"Centroids outside model domain: "
    f"{outside_count:,}"
)

# We only make predictions inside the region
# represented by our training experiment.
panchayats = panchayats[
    inside_domain
].copy().reset_index(drop=True)


# ============================================================
# LOAD GFS
# ============================================================

print()
print("=" * 60)
print("LOADING GFS TEST FORECASTS")
print("=" * 60)

gfs = pd.read_csv(
    GFS_FILE
)

gfs["date"] = pd.to_datetime(
    gfs["date"]
)

for col in [
    "requested_latitude",
    "requested_longitude",
    "forecast_rainfall_mm",
]:

    gfs[col] = pd.to_numeric(
        gfs[col],
        errors="coerce"
    )


gfs = gfs[
    (gfs["date"] >= TEST_START)
    &
    (gfs["date"] <= TEST_END)
].copy()


print(
    f"GFS test rows: "
    f"{len(gfs):,}"
)

print(
    f"GFS test dates: "
    f"{gfs['date'].nunique()}"
)

gfs_grid_points = (
    gfs[
        [
            "requested_latitude",
            "requested_longitude",
        ]
    ]
    .drop_duplicates()
    .shape[0]
)

print(
    f"GFS grid points: "
    f"{gfs_grid_points:,}"
)


# ============================================================
# PREPARE COARSE GRID
# ============================================================

coarse_grid = (
    gfs[
        [
            "requested_latitude",
            "requested_longitude",
        ]
    ]
    .drop_duplicates()
    .copy()
)

coarse_grid["requested_latitude"] = (
    coarse_grid["requested_latitude"]
    .round(6)
)

coarse_grid["requested_longitude"] = (
    coarse_grid["requested_longitude"]
    .round(6)
)


# Create spatial index
coarse_points = np.column_stack(
    [
        coarse_grid["requested_latitude"].to_numpy(),
        coarse_grid["requested_longitude"].to_numpy(),
    ]
)

coarse_tree = cKDTree(
    coarse_points
)


# ============================================================
# ASSIGN EACH PANCHAYAT TO NEAREST GFS CELL
# ============================================================

print()
print("=" * 60)
print("ASSIGNING PANCHAYATS TO COARSE GFS CELLS")
print("=" * 60)

panchayat_points = np.column_stack(
    [
        panchayats["centroid_lat"].to_numpy(),
        panchayats["centroid_lon"].to_numpy(),
    ]
)

_, nearest_indices = coarse_tree.query(
    panchayat_points,
    k=1
)

panchayats["coarse_lat"] = (
    coarse_grid.iloc[
        nearest_indices
    ]["requested_latitude"]
    .to_numpy()
)

panchayats["coarse_lon"] = (
    coarse_grid.iloc[
        nearest_indices
    ]["requested_longitude"]
    .to_numpy()
)


# ============================================================
# LOAD ELEVATION
# ============================================================

print()
print("=" * 60)
print("LOADING FINE-GRID ELEVATION")
print("=" * 60)

elevation = pd.read_csv(
    ELEVATION_FILE
)

elevation["fine_lat"] = pd.to_numeric(
    elevation["fine_lat"],
    errors="coerce"
)

elevation["fine_lon"] = pd.to_numeric(
    elevation["fine_lon"],
    errors="coerce"
)

elevation["elevation_m"] = pd.to_numeric(
    elevation["elevation_m"],
    errors="coerce"
)

elevation[
    "nearest_known_distance_deg"
] = pd.to_numeric(
    elevation[
        "nearest_known_distance_deg"
    ],
    errors="coerce"
)


elevation = elevation.dropna(
    subset=[
        "fine_lat",
        "fine_lon",
        "elevation_m",
    ]
).copy()


elevation["fine_lat"] = (
    elevation["fine_lat"]
    .round(6)
)

elevation["fine_lon"] = (
    elevation["fine_lon"]
    .round(6)
)


elevation = elevation.drop_duplicates(
    subset=[
        "fine_lat",
        "fine_lon",
    ]
)


print(
    f"Elevation cells: "
    f"{len(elevation):,}"
)


# ============================================================
# BUILD ELEVATION SPATIAL INDEX
# ============================================================

reference_lat = (
    elevation["fine_lat"].mean()
)

longitude_scale = np.cos(
    np.radians(reference_lat)
)

elevation_points = np.column_stack(
    [
        elevation["fine_lat"].to_numpy(),
        elevation["fine_lon"].to_numpy()
        * longitude_scale,
    ]
)

elevation_tree = cKDTree(
    elevation_points
)


# ============================================================
# FIND NEAREST ELEVATION CELL
# ============================================================

print()
print(
    "Assigning nearest fine-grid elevation..."
)

centroid_points_scaled = np.column_stack(
    [
        panchayats[
            "centroid_lat"
        ].to_numpy(),

        panchayats[
            "centroid_lon"
        ].to_numpy()
        * longitude_scale,
    ]
)


_, elevation_indices = elevation_tree.query(
    centroid_points_scaled,
    k=1
)


nearest_elevation = (
    elevation.iloc[
        elevation_indices
    ]
    .reset_index(drop=True)
)


panchayats["elevation_m"] = (
    nearest_elevation[
        "elevation_m"
    ].to_numpy()
)

nearest_elevation_source = (
    nearest_elevation[
        "elevation_source"
    ]
    .fillna("local_idw_interpolation")
    .astype(str)
    .str.strip()
)

panchayats[
    "elevation_interpolated"
] = (
    nearest_elevation_source
    .eq("local_idw_interpolation")
    .to_numpy(dtype=np.int8)
)

panchayats[
    "nearest_known_distance_deg"
] = (
    nearest_elevation[
        "nearest_known_distance_deg"
    ].to_numpy()
)


# ============================================================
# CREATE PANCHAYAT × DATE DATASET
# ============================================================

print()
print("=" * 60)
print("CREATING PANCHAYAT × DATE DATASET")
print("=" * 60)


dates = pd.DataFrame(
    {
        "date": sorted(
            gfs["date"].unique()
        )
    }
)

panchayats["_join_key"] = 1
dates["_join_key"] = 1

prediction = panchayats.merge(
    dates,
    on="_join_key"
).drop(
    columns="_join_key"
)


print(
    f"Expected prediction rows: "
    f"{len(prediction):,}"
)


# ============================================================
# ADD GFS RAINFALL
# ============================================================

gfs_lookup = gfs[
    [
        "date",
        "requested_latitude",
        "requested_longitude",
        "forecast_rainfall_mm",
    ]
].copy()


gfs_lookup = gfs_lookup.rename(
    columns={
        "requested_latitude": "coarse_lat",
        "requested_longitude": "coarse_lon",
    }
)


gfs_lookup["coarse_lat"] = (
    gfs_lookup["coarse_lat"]
    .round(6)
)

gfs_lookup["coarse_lon"] = (
    gfs_lookup["coarse_lon"]
    .round(6)
)


prediction = prediction.merge(
    gfs_lookup,
    on=[
        "date",
        "coarse_lat",
        "coarse_lon",
    ],
    how="left",
    validate="many_to_one",
)


prediction = prediction.rename(
    columns={
        "forecast_rainfall_mm":
            "gfs_rainfall"
    }
)


print(
    f"Missing GFS rainfall: "
    f"{prediction['gfs_rainfall'].isna().sum():,}"
)


# ============================================================
# FEATURE ENGINEERING
# ============================================================

prediction["fine_lat"] = (
    prediction["centroid_lat"]
)

prediction["fine_lon"] = (
    prediction["centroid_lon"]
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

# ============================================================
# CHECK FOR MISSING MODEL FEATURES
# ============================================================

missing_feature_mask = prediction[FEATURES].isna().any(axis=1)

missing_rows = prediction[
    missing_feature_mask
].copy()

if len(missing_rows) > 0:

    print()
    print("=" * 60)
    print("MISSING FEATURE DIAGNOSTIC")
    print("=" * 60)

    print(
        f"Rows with missing features: "
        f"{len(missing_rows):,}"
    )

    print(
        f"Affected Panchayats: "
        f"{missing_rows['gpcode'].nunique():,}"
    )

    missing_counts = (
        missing_rows[FEATURES]
        .isna()
        .sum()
    )

    print()
    print("Missing values by feature:")

    print(
        missing_counts[
            missing_counts > 0
        ].to_string()
    )

    print()
    print("Affected Panchayats:")

    print(
        missing_rows[
            [
                "gpcode",
                "gpname",
                "district",
                "block",
                "centroid_lat",
                "centroid_lon",
            ]
        ]
        .drop_duplicates()
        .head(20)
        .to_string(index=False)
    )

    raise ValueError(
        "Missing model features found. "
        "Fix them before generating final predictions."
    )

prediction = prediction.copy()


# ============================================================
# GENERATE PREDICTIONS
# ============================================================

print()
print("=" * 60)
print("GENERATING PANCHAYAT RAINFALL PREDICTIONS")
print("=" * 60)

prediction[
    "downscaled_rainfall_mm"
] = model.predict(
    prediction[FEATURES]
)

prediction[
    "downscaled_rainfall_mm"
] = np.maximum(
    prediction[
        "downscaled_rainfall_mm"
    ],
    0
)


# ============================================================
# FINAL COLUMNS
# ============================================================

prediction = prediction[
    [
        "date",
        "gpcode",
        "gpname",
        "district_code",
        "district",
        "block_code",
        "block",
        "centroid_lat",
        "centroid_lon",
        "coarse_lat",
        "coarse_lon",
        "gfs_rainfall",
        "elevation_m",
        "downscaled_rainfall_mm",
    ]
].copy()


prediction = prediction.sort_values(
    [
        "date",
        "district",
        "block",
        "gpname",
    ]
).reset_index(drop=True)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("PANCHAYAT PREDICTION SUMMARY")
print("=" * 60)

print(
    f"Prediction rows: "
    f"{len(prediction):,}"
)

print(
    f"Unique Panchayats: "
    f"{prediction['gpcode'].nunique():,}"
)

print(
    f"Unique dates: "
    f"{prediction['date'].nunique()}"
)

print(
    f"Date range: "
    f"{prediction['date'].min().date()} → "
    f"{prediction['date'].max().date()}"
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
    f"Downscaled rainfall min: "
    f"{prediction['downscaled_rainfall_mm'].min():.2f} mm"
)

print(
    f"Downscaled rainfall max: "
    f"{prediction['downscaled_rainfall_mm'].max():.2f} mm"
)

print(
    f"Downscaled rainfall mean: "
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

print()
print(
    "Method: ML downscaling evaluated at "
    "each Panchayat centroid."
)