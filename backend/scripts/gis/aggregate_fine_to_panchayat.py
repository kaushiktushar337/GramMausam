from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

PANCHAYAT_FILE = (
    BASE_DIR
    / "data"
    / "gis"
    / "model_domain_panchayats_clean.gpkg"
)

FINE_PREDICTION_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "fine_predictions_july2025_test.csv"
)

CENTROID_PREDICTION_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "panchayat_predictions_july2025_test.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "panchayat_polygon_rainfall_july2025_test.csv"
)


# ============================================================
# CONSTANTS
# ============================================================

# CHIRPS/fine grid resolution used in this experiment.
CELL_SIZE = 0.05

HALF_CELL = CELL_SIZE / 2.0


# ============================================================
# LOAD PANCHAYATS
# ============================================================

print("=" * 60)
print("LOADING CLEAN PANCHAYAT POLYGONS")
print("=" * 60)

panchayats = gpd.read_file(
    PANCHAYAT_FILE,
    layer="panchayats",
)

print(
    f"Panchayats loaded: "
    f"{len(panchayats):,}"
)

# Normalize GP codes so merges work even when one source stores
# them as integers and another stores them as strings.
panchayats["gpcode"] = (
    panchayats["gpcode"]
    .astype("string")
    .str.strip()
)

required_panchayat_columns = [
    "gpcode",
    "gpname",
    "dt_lgd",
    "dtname",
    "blk_lgdcod",
    "blkname",
    "geometry",
]

missing = [
    c
    for c in required_panchayat_columns
    if c not in panchayats.columns
]

if missing:
    raise ValueError(
        f"Missing Panchayat columns: {missing}"
    )


# ============================================================
# LOAD FINE GRID PREDICTIONS
# ============================================================

print()
print("=" * 60)
print("LOADING FINE-GRID PREDICTIONS")
print("=" * 60)

fine = pd.read_csv(
    FINE_PREDICTION_FILE,
)

fine["date"] = pd.to_datetime(
    fine["date"]
)

for col in [
    "fine_lat",
    "fine_lon",
    "gfs_rainfall",
    "elevation_m",
    "downscaled_rainfall_mm",
]:
    fine[col] = pd.to_numeric(
        fine[col],
        errors="coerce",
    )


fine = fine.dropna(
    subset=[
        "date",
        "fine_lat",
        "fine_lon",
        "downscaled_rainfall_mm",
    ]
).copy()

fine["fine_lat"] = fine[
    "fine_lat"
].round(6)

fine["fine_lon"] = fine[
    "fine_lon"
].round(6)


print(
    f"Fine prediction rows: "
    f"{len(fine):,}"
)

fine_cell_count = (
    fine[
        [
            "fine_lat",
            "fine_lon",
        ]
    ]
    .drop_duplicates()
    .shape[0]
)

print(
    f"Fine cells: "
    f"{fine_cell_count:,}"
)

print(
    f"Dates: "
    f"{fine['date'].nunique()}"
)


# ============================================================
# CREATE FINE-CELL POLYGONS
# ============================================================

print()
print("=" * 60)
print("CREATING FINE-GRID CELL POLYGONS")
print("=" * 60)

fine_cells = (
    fine[
        [
            "fine_lat",
            "fine_lon",
        ]
    ]
    .drop_duplicates()
    .copy()
)

fine_cells["geometry"] = [
    box(
        lon - HALF_CELL,
        lat - HALF_CELL,
        lon + HALF_CELL,
        lat + HALF_CELL,
    )
    for lat, lon in zip(
        fine_cells["fine_lat"],
        fine_cells["fine_lon"],
    )
]

fine_gdf = gpd.GeoDataFrame(
    fine_cells,
    geometry="geometry",
    crs="EPSG:4326",
)

print(
    f"Fine-cell polygons: "
    f"{len(fine_gdf):,}"
)


# ============================================================
# PREPARE PROJECTED DATA
# ============================================================

print()
print("=" * 60)
print("PROJECTING GEOMETRIES")
print("=" * 60)

# Equal-area CRS for area-weighted calculations.
AREA_CRS = "EPSG:6933"

panchayats_area = panchayats[
    [
        "gpcode",
        "gpname",
        "dt_lgd",
        "dtname",
        "blk_lgdcod",
        "blkname",
        "geometry",
    ]
].copy()

panchayats_area = (
    panchayats_area
    .to_crs(AREA_CRS)
)

fine_area = fine_gdf.to_crs(
    AREA_CRS
)


# ============================================================
# SPATIAL JOIN CANDIDATES
# ============================================================

print()
print("=" * 60)
print("FINDING FINE CELLS INTERSECTING PANCHAYATS")
print("=" * 60)

candidate_matches = gpd.sjoin(
    fine_area,
    panchayats_area[
        [
            "gpcode",
            "geometry",
        ]
    ],
    how="inner",
    predicate="intersects",
)

print(
    f"Candidate cell/Panchayat matches: "
    f"{len(candidate_matches):,}"
)


if len(candidate_matches) == 0:

    raise RuntimeError(
        "No fine-grid cells intersect any Panchayat."
    )


# ============================================================
# ADD PANCHAYAT GEOMETRY
# ============================================================

# sjoin keeps the fine-cell geometry.
# Attach the matching Panchayat geometry separately.

right_geometry = (
    panchayats_area[
        [
            "gpcode",
            "geometry",
        ]
    ]
    .rename(
        columns={
            "geometry": "panchayat_geometry",
        }
    )
)

candidate_matches = candidate_matches.drop(
    columns=["index_right"],
    errors="ignore",
)

candidate_matches = candidate_matches.merge(
    right_geometry,
    on="gpcode",
    how="left",
    validate="many_to_one",
)


# ============================================================
# CALCULATE OVERLAP AREA
# ============================================================

print()
print(
    "Calculating polygon overlap areas..."
)

candidate_matches["intersection_area_m2"] = (
    candidate_matches.geometry
    .intersection(
        candidate_matches["panchayat_geometry"]
    )
    .area
)


candidate_matches = candidate_matches[
    candidate_matches[
        "intersection_area_m2"
    ] > 0
].copy()


print(
    f"Positive-overlap matches: "
    f"{len(candidate_matches):,}"
)


# ============================================================
# FINE-CELL AREA
# ============================================================

candidate_matches["cell_area_m2"] = (
    candidate_matches
    .geometry
    .area
)

candidate_matches["overlap_weight"] = (
    candidate_matches[
        "intersection_area_m2"
    ]
    /
    candidate_matches[
        "cell_area_m2"
    ]
)


# ============================================================
# CONVERT BACK TO WGS84
# ============================================================

print()
print("Preparing rainfall values...")

# Build spatial mapping:
#
# fine_lat + fine_lon → gpcode + overlap weight

mapping = candidate_matches[
    [
        "fine_lat",
        "fine_lon",
        "gpcode",
        "overlap_weight",
    ]
].copy()

mapping["fine_lat"] = mapping[
    "fine_lat"
].round(6)

mapping["fine_lon"] = mapping[
    "fine_lon"
].round(6)


# ============================================================
# MERGE RAINFALL VALUES
# ============================================================

fine_for_merge = fine[
    [
        "date",
        "fine_lat",
        "fine_lon",
        "downscaled_rainfall_mm",
    ]
].copy()


joined = mapping.merge(
    fine_for_merge,
    on=[
        "fine_lat",
        "fine_lon",
    ],
    how="inner",
)

print(
    f"Rainfall mapping rows: "
    f"{len(joined):,}"
)


if len(joined) == 0:

    raise RuntimeError(
        "Fine predictions could not be matched "
        "to spatial mapping."
    )


# ============================================================
# WEIGHTED RAINFALL
# ============================================================

joined["weighted_rainfall"] = (
    joined[
        "downscaled_rainfall_mm"
    ]
    *
    joined[
        "overlap_weight"
    ]
)


# ============================================================
# AGGREGATE BY PANCHAYAT + DATE
# ============================================================

print()
print("=" * 60)
print("AGGREGATING RAINFALL TO PANCHAYATS")
print("=" * 60)


joined["weighted_rainfall"] = (
    joined["downscaled_rainfall_mm"]
    * joined["overlap_weight"]
)

# Avoid pandas GroupBy.apply so the script does not rely on
# deprecated grouping-column behavior.
aggregated = (
    joined
    .groupby(
        [
            "date",
            "gpcode",
        ],
        as_index=False,
    )
    .agg(
        weighted_rainfall_sum=(
            "weighted_rainfall",
            "sum",
        ),
        total_overlap_weight=(
            "overlap_weight",
            "sum",
        ),
        min_rainfall_mm=(
            "downscaled_rainfall_mm",
            "min",
        ),
        max_rainfall_mm=(
            "downscaled_rainfall_mm",
            "max",
        ),
        grid_cells_used=(
            "fine_lat",
            "count",
        ),
    )
)

aggregated["polygon_mean_rainfall_mm"] = np.where(
    aggregated["total_overlap_weight"] > 0,
    aggregated["weighted_rainfall_sum"]
    / aggregated["total_overlap_weight"],
    np.nan,
)

aggregated = aggregated.drop(
    columns=["weighted_rainfall_sum"]
)


# ============================================================
# ADD PANCHAYAT METADATA
# ============================================================

metadata = panchayats[
    [
        "gpcode",
        "gpname",
        "dt_lgd",
        "dtname",
        "blk_lgdcod",
        "blkname",
    ]
].copy()

metadata["gpcode"] = (
    metadata["gpcode"]
    .astype("string")
    .str.strip()
)

metadata = metadata.rename(
    columns={
        "dt_lgd": "district_code",
        "dtname": "district",
        "blk_lgdcod": "block_code",
        "blkname": "block",
    }
)


aggregated["gpcode"] = (
    aggregated["gpcode"]
    .astype("string")
    .str.strip()
)

aggregated = aggregated.merge(
    metadata,
    on="gpcode",
    how="left",
    validate="many_to_one",
)


# ============================================================
# IDENTIFY PREDICTIONS WITH NO POLYGON COVERAGE
# ============================================================

print()
print("=" * 60)
print("CHECKING PANCHAYAT COVERAGE")
print("=" * 60)

all_panchayats = metadata[
    ["gpcode"]
].drop_duplicates()

all_panchayats["gpcode"] = (
    all_panchayats["gpcode"]
    .astype("string")
    .str.strip()
)

all_dates = pd.DataFrame(
    {
        "date": sorted(
            fine["date"].unique()
        )
    }
)

all_panchayats["_key"] = 1
all_dates["_key"] = 1

expected = (
    all_panchayats
    .merge(
        all_dates,
        on="_key",
    )
    .drop(
        columns="_key"
    )
)

expected = expected.merge(
    metadata,
    on="gpcode",
    how="left",
)


aggregated["date"] = pd.to_datetime(
    aggregated["date"]
)

expected["gpcode"] = (
    expected["gpcode"]
    .astype("string")
    .str.strip()
)

aggregated["gpcode"] = (
    aggregated["gpcode"]
    .astype("string")
    .str.strip()
)

complete = expected.merge(
    aggregated[
        [
            "date",
            "gpcode",
            "polygon_mean_rainfall_mm",
            "min_rainfall_mm",
            "max_rainfall_mm",
            "grid_cells_used",
            "total_overlap_weight",
        ]
    ],
    on=[
        "date",
        "gpcode",
    ],
    how="left",
    validate="one_to_one",
)


# ============================================================
# CENTROID FALLBACK
# ============================================================

print()
print(
    "Loading centroid predictions for fallback..."
)

centroid = pd.read_csv(
    CENTROID_PREDICTION_FILE
)

# Normalize GP codes on the centroid prediction side as well.
centroid["gpcode"] = (
    centroid["gpcode"]
    .astype("string")
    .str.strip()
)

centroid["date"] = pd.to_datetime(
    centroid["date"]
)

centroid = centroid[
    [
        "date",
        "gpcode",
        "downscaled_rainfall_mm",
    ]
].rename(
    columns={
        "downscaled_rainfall_mm":
            "centroid_rainfall_mm",
    }
)

# ------------------------------------------------------------
# Restrict the final product to Panchayats for which the
# centroid ML pipeline produced a valid prediction.
#
# This keeps the final model-domain dataset internally
# consistent and avoids creating blank records for Panchayats
# outside the trained/evaluated spatial domain.
# ------------------------------------------------------------

eligible_gp_codes = set(
    centroid["gpcode"]
    .astype("string")
    .str.strip()
)

# `complete` was constructed before the centroid file was loaded.
# Therefore, filter `complete` itself here; filtering only `expected`
# would not remove out-of-domain Panchayats already copied into it.
before_complete_rows = len(complete)

complete = complete[
    complete["gpcode"].isin(eligible_gp_codes)
].copy()

print()
print(
    f"Eligible model-domain Panchayats: "
    f"{len(eligible_gp_codes):,}"
)

print(
    f"Expected model-domain rows: "
    f"{len(expected):,}"
)

print(
    f"Rows retained in final product domain: "
    f"{len(complete):,}"
)

if before_complete_rows != len(complete):
    print(
        f"Rows excluded outside model domain: "
        f"{before_complete_rows - len(complete):,}"
    )


complete = complete.merge(
    centroid,
    on=[
        "date",
        "gpcode",
    ],
    how="left",
    validate="one_to_one",
)


missing_polygon = (
    complete[
        "polygon_mean_rainfall_mm"
    ].isna()
)


print(
    f"Rows with polygon coverage: "
    f"{(~missing_polygon).sum():,}"
)

print(
    f"Rows needing centroid fallback: "
    f"{missing_polygon.sum():,}"
)


# Use centroid estimate only when no fine-grid polygon
# overlap exists.

complete["final_rainfall_mm"] = (
    complete[
        "polygon_mean_rainfall_mm"
    ]
)

complete.loc[
    missing_polygon,
    "final_rainfall_mm"
] = complete.loc[
    missing_polygon,
    "centroid_rainfall_mm"
]


complete["prediction_method"] = (
    np.where(
        missing_polygon,
        "centroid_fallback",
        "polygon_area_weighted",
    )
)


# ============================================================
# FINAL COLUMNS
# ============================================================

complete = complete[
    [
        "date",
        "gpcode",
        "gpname",
        "district_code",
        "district",
        "block_code",
        "block",
        "polygon_mean_rainfall_mm",
        "min_rainfall_mm",
        "max_rainfall_mm",
        "grid_cells_used",
        "total_overlap_weight",
        "centroid_rainfall_mm",
        "final_rainfall_mm",
        "prediction_method",
    ]
].copy()


complete = complete.sort_values(
    [
        "date",
        "district",
        "block",
        "gpname",
    ]
).reset_index(drop=True)


# ============================================================
# VALIDATION
# ============================================================

print()
print("=" * 60)
print("FINAL PANCHAYAT RAINFALL SUMMARY")
print("=" * 60)

print(
    f"Rows: {len(complete):,}"
)

print(
    f"Unique Panchayats: "
    f"{complete['gpcode'].nunique():,}"
)

print(
    f"Unique dates: "
    f"{complete['date'].nunique()}"
)

missing_final_rainfall = (
    complete["final_rainfall_mm"].isna().sum()
)

print(
    f"Missing final rainfall: "
    f"{missing_final_rainfall:,}"
)

duplicate_final_keys = complete.duplicated(
    subset=["date", "gpcode"]
).sum()

print(
    f"Duplicate date/GP keys: "
    f"{duplicate_final_keys:,}"
)

print()
print("Prediction methods:")

print(
    complete[
        "prediction_method"
    ].value_counts()
)


print()
print(
    f"Final rainfall min: "
    f"{complete['final_rainfall_mm'].min():.2f} mm"
)

print(
    f"Final rainfall max: "
    f"{complete['final_rainfall_mm'].max():.2f} mm"
)

print(
    f"Final rainfall mean: "
    f"{complete['final_rainfall_mm'].mean():.2f} mm"
)


# ============================================================
# FINAL INTEGRITY CHECK
# ============================================================

if missing_final_rainfall != 0:
    raise RuntimeError(
        "Final dataset still contains missing rainfall values. "
        "Do not save an incomplete Panchayat product."
    )

if duplicate_final_keys != 0:
    raise RuntimeError(
        "Final dataset contains duplicate date/GP keys."
    )


# ============================================================
# SAVE
# ============================================================

complete.to_csv(
    OUTPUT_FILE,
    index=False,
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
    "Polygon estimates use area-weighted "
    "fine-grid rainfall."
)

print(
    "Centroid estimates are used only where "
    "no fine-grid polygon overlap exists."
)