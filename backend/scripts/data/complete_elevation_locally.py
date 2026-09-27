from pathlib import Path
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

TRAINING_FILE = BASE_DIR / "data" / "processed" / (
    "gfs_chirps_training_up_2025-07.csv"
)

ELEVATION_FILE = BASE_DIR / "data" / "processed" / (
    "fine_grid_elevation_up.csv"
)

OUTPUT_FILE = BASE_DIR / "data" / "processed" / (
    "fine_grid_elevation_up_complete.csv"
)


# ============================================================
# SETTINGS
# ============================================================

# Number of nearby known points used for interpolation
K_NEIGHBORS = 8

EPSILON = 1e-10


# ============================================================
# LOAD REQUIRED FINE GRID
# ============================================================

print("=" * 60)
print("Loading complete fine grid...")
print("=" * 60)

fine_grid = pd.read_csv(
    TRAINING_FILE,
    usecols=["fine_lat", "fine_lon"]
)

fine_grid = (
    fine_grid
    .drop_duplicates()
    .reset_index(drop=True)
)

fine_grid["fine_lat"] = pd.to_numeric(
    fine_grid["fine_lat"],
    errors="coerce"
)

fine_grid["fine_lon"] = pd.to_numeric(
    fine_grid["fine_lon"],
    errors="coerce"
)

fine_grid = fine_grid.dropna(
    subset=["fine_lat", "fine_lon"]
)

fine_grid["fine_lat"] = fine_grid["fine_lat"].round(6)
fine_grid["fine_lon"] = fine_grid["fine_lon"].round(6)

print(
    f"Required fine-grid points: {len(fine_grid):,}"
)


# ============================================================
# LOAD EXISTING ELEVATION
# ============================================================

print()
print("=" * 60)
print("Loading downloaded elevation points...")
print("=" * 60)

elevation = pd.read_csv(
    ELEVATION_FILE
)

required_columns = {
    "fine_lat",
    "fine_lon",
    "elevation_m"
}

missing_columns = required_columns - set(
    elevation.columns
)

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
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

elevation = elevation.dropna(
    subset=[
        "fine_lat",
        "fine_lon",
        "elevation_m"
    ]
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
        "fine_lon"
]
).reset_index(drop=True)

print(
    f"Downloaded elevation points: "
    f"{len(elevation):,}"
)


# ============================================================
# MARK REAL API VALUES
# ============================================================

elevation["elevation_source"] = "open_meteo_api"


# ============================================================
# FIND MISSING FINE GRID POINTS
# ============================================================

merged = fine_grid.merge(
    elevation[
        [
            "fine_lat",
            "fine_lon",
            "elevation_m",
            "elevation_source",
        ]
    ],
    on=[
        "fine_lat",
        "fine_lon",
    ],
    how="left"
)

known_mask = merged["elevation_m"].notna()

known = merged[known_mask].copy()
missing = merged[~known_mask].copy()

print()
print(
    f"Known elevations: {len(known):,}"
)

print(
    f"Missing elevations: {len(missing):,}"
)


# ============================================================
# NOTHING TO DO
# ============================================================

if len(missing) == 0:

    print()
    print("All elevation points already exist.")

    merged = merged.sort_values(
        ["fine_lat", "fine_lon"]
    ).reset_index(drop=True)

    merged.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    raise SystemExit


# ============================================================
# BUILD SPATIAL TREE
# ============================================================

print()
print("=" * 60)
print("Building spatial index...")
print("=" * 60)

# Use a latitude-adjusted longitude so that
# Euclidean distance is a better approximation
# of geographic distance over Uttar Pradesh.

reference_lat = fine_grid["fine_lat"].mean()

longitude_scale = np.cos(
    np.radians(reference_lat)
)

known_points = np.column_stack(
    [
        known["fine_lat"].to_numpy(),
        known["fine_lon"].to_numpy()
        * longitude_scale,
    ]
)

missing_points = np.column_stack(
    [
        missing["fine_lat"].to_numpy(),
        missing["fine_lon"].to_numpy()
        * longitude_scale,
    ]
)

tree = cKDTree(
    known_points
)


# ============================================================
# FIND K NEAREST KNOWN POINTS
# ============================================================

print(
    f"Finding {K_NEIGHBORS} nearest known "
    f"elevation points..."
)

distances, indices = tree.query(
    missing_points,
    k=min(K_NEIGHBORS, len(known))
)


# ============================================================
# HANDLE SINGLE-NEIGHBOR CASE
# ============================================================

if distances.ndim == 1:

    distances = distances[:, None]
    indices = indices[:, None]


# ============================================================
# INVERSE DISTANCE WEIGHTING
# ============================================================

print(
    "Calculating local elevation estimates..."
)

known_elevations = known[
    "elevation_m"
].to_numpy()

neighbor_elevations = known_elevations[
    indices
]

weights = 1.0 / (
    distances + EPSILON
)

weighted_elevation = (
    np.sum(
        weights * neighbor_elevations,
        axis=1
    )
    /
    np.sum(
        weights,
        axis=1
    )
)


# ============================================================
# ADD INTERPOLATED VALUES
# ============================================================

missing["elevation_m"] = weighted_elevation

missing["elevation_source"] = (
    "local_idw_interpolation"
)

# Useful diagnostic:
# distance to nearest real API elevation point.
missing["nearest_known_distance_deg"] = (
    distances[:, 0]
)


# ============================================================
# ADD DIAGNOSTIC TO KNOWN POINTS
# ============================================================

known["nearest_known_distance_deg"] = 0.0


# ============================================================
# COMBINE
# ============================================================

final = pd.concat(
    [
        known,
        missing,
    ],
    ignore_index=True
)


# ============================================================
# VALIDATE
# ============================================================

final = final[
    [
        "fine_lat",
        "fine_lon",
        "elevation_m",
        "elevation_source",
        "nearest_known_distance_deg",
    ]
].copy()

final["fine_lat"] = final[
    "fine_lat"
].round(6)

final["fine_lon"] = final[
    "fine_lon"
].round(6)

final["elevation_m"] = final[
    "elevation_m"
].round(2)

final = final.drop_duplicates(
    subset=[
        "fine_lat",
        "fine_lon",
    ],
    keep="first"
)

final = final.sort_values(
    [
        "fine_lat",
        "fine_lon",
    ]
).reset_index(drop=True)


# ============================================================
# CHECK COUNTS
# ============================================================

api_count = (
    final["elevation_source"]
    == "open_meteo_api"
).sum()

interpolated_count = (
    final["elevation_source"]
    == "local_idw_interpolation"
).sum()

missing_count = (
    final["elevation_m"]
    .isna()
    .sum()
)


print()
print("=" * 60)
print("FINAL ELEVATION SUMMARY")
print("=" * 60)

print(
    f"Expected points      : {len(fine_grid):,}"
)

print(
    f"Final points         : {len(final):,}"
)

print(
    f"API elevations       : {api_count:,}"
)

print(
    f"Interpolated         : {interpolated_count:,}"
)

print(
    f"Missing elevations   : {missing_count:,}"
)

print(
    f"Elevation minimum    : "
    f"{final['elevation_m'].min():.2f} m"
)

print(
    f"Elevation maximum    : "
    f"{final['elevation_m'].max():.2f} m"
)

print(
    f"Elevation mean       : "
    f"{final['elevation_m'].mean():.2f} m"
)


if len(missing) > 0:

    print()
    print(
        "Interpolation nearest-point "
        "distance statistics:"
    )

    print(
        f"Minimum: "
        f"{missing['nearest_known_distance_deg'].min():.6f}°"
    )

    print(
        f"Maximum: "
        f"{missing['nearest_known_distance_deg'].max():.6f}°"
    )

    print(
        f"Mean: "
        f"{missing['nearest_known_distance_deg'].mean():.6f}°"
    )


# ============================================================
# SAVE
# ============================================================

final.to_csv(
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