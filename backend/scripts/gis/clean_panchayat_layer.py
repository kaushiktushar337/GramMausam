from pathlib import Path
import json

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "gis"
    / "model_domain_panchayats.geojsonl"
)

OUTPUT_GPKG = (
    BASE_DIR
    / "data"
    / "gis"
    / "model_domain_panchayats_clean.gpkg"
)

OUTPUT_CENTROIDS = (
    BASE_DIR
    / "data"
    / "gis"
    / "panchayat_centroids.csv"
)


# ============================================================
# LOAD VALID PANCHAYAT RECORDS
# ============================================================

print("=" * 60)
print("LOADING PANCHAYAT GEOMETRIES")
print("=" * 60)

records = []
skipped_blank = 0
invalid = 0


with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:

    for line in f:

        line = line.strip()

        if not line:
            continue

        try:
            feature = json.loads(line)

            props = feature.get(
                "properties",
                {}
            )

            geometry_data = feature.get(
                "geometry"
            )

            gpcode = (
                props.get("gpcode")
                or props.get("gp_code")
            )

            gpname = (
                props.get("gpname")
                or props.get("gp_name")
            )

            if gpcode is None:
                skipped_blank += 1
                continue

            gpcode = str(gpcode).strip()

            if not gpcode:
                skipped_blank += 1
                continue

            if gpname is None:
                skipped_blank += 1
                continue

            gpname = str(gpname).strip()

            if not gpname:
                skipped_blank += 1
                continue

            if not geometry_data:
                invalid += 1
                continue

            geometry = shape(
                geometry_data
            )

            if geometry.is_empty:
                invalid += 1
                continue

            records.append(
                {
                    "gpcode": gpcode,
                    "gpname": gpname,
                    "dt_lgd": props.get("dt_lgd"),
                    "dtname": props.get("dtname"),
                    "blk_lgdcod": props.get(
                        "blk_lgdcod"
                    ),
                    "blkname": props.get(
                        "blkname"
                    ),
                    "sdt_lgd": props.get(
                        "sdt_lgd"
                    ),
                    "sdtname": props.get(
                        "sdtname"
                    ),
                    "st_lgd": props.get(
                        "st_lgd"
                    ),
                    "stname": props.get(
                        "stname"
                    ),
                    "geometry": geometry,
                }
            )

        except Exception:
            invalid += 1


print(
    f"Valid GP geometry records: "
    f"{len(records):,}"
)

print(
    f"Blank/invalid GP records excluded: "
    f"{skipped_blank + invalid:,}"
)


# ============================================================
# BUILD GEODATAFRAME
# ============================================================

gdf = gpd.GeoDataFrame(
    records,
    geometry="geometry",
    crs="EPSG:4326",
)


# ============================================================
# FIX INVALID GEOMETRIES
# ============================================================

print()
print("=" * 60)
print("CHECKING GEOMETRIES")
print("=" * 60)

invalid_mask = ~gdf.geometry.is_valid

print(
    f"Invalid geometries: "
    f"{invalid_mask.sum():,}"
)

if invalid_mask.any():

    print("Attempting make_valid()...")

    gdf.loc[
        invalid_mask,
        "geometry"
    ] = gdf.loc[
        invalid_mask,
        "geometry"
    ].make_valid()


# Remove empty geometries after repair
gdf = gdf[
    ~gdf.geometry.is_empty
].copy()


# ============================================================
# DISSOLVE GEOMETRY PIECES BY GP CODE
# ============================================================

print()
print("=" * 60)
print("DISSOLVING GEOMETRY PIECES")
print("=" * 60)

print(
    f"Before dissolve: "
    f"{len(gdf):,} geometry records"
)

gdf = gdf.dissolve(
    by="gpcode",
    as_index=False,
    aggfunc={
        "gpname": "first",
        "dt_lgd": "first",
        "dtname": "first",
        "blk_lgdcod": "first",
        "blkname": "first",
        "sdt_lgd": "first",
        "sdtname": "first",
        "st_lgd": "first",
        "stname": "first",
    },
)


print(
    f"After dissolve: "
    f"{len(gdf):,} logical Panchayats"
)


# ============================================================
# CLEAN INDEX
# ============================================================

gdf = gdf[
    [
        "gpcode",
        "gpname",
        "dt_lgd",
        "dtname",
        "blk_lgdcod",
        "blkname",
        "sdt_lgd",
        "sdtname",
        "st_lgd",
        "stname",
        "geometry",
    ]
].copy()


# ============================================================
# SAVE LOCAL GIS LAYER
# ============================================================

print()
print("=" * 60)
print("SAVING CLEAN PANCHAYAT LAYER")
print("=" * 60)

if OUTPUT_GPKG.exists():
    OUTPUT_GPKG.unlink()

gdf.to_file(
    OUTPUT_GPKG,
    layer="panchayats",
    driver="GPKG",
)


print(
    f"GeoPackage: {OUTPUT_GPKG}"
)


# ============================================================
# CREATE ACCURATE CENTROIDS
# ============================================================

print()
print("=" * 60)
print("CALCULATING PANCHAYAT CENTROIDS")
print("=" * 60)

# Use an equal-area projected CRS for centroid calculation.
projected = gdf.to_crs(
    "EPSG:6933"
)

projected["centroid_geometry"] = (
    projected.geometry.centroid
)

centroids = projected[
    [
        "gpcode",
        "gpname",
        "dt_lgd",
        "dtname",
        "blk_lgdcod",
        "blkname",
        "centroid_geometry",
    ]
].copy()

centroids = gpd.GeoDataFrame(
    centroids,
    geometry="centroid_geometry",
    crs="EPSG:6933",
)

centroids = centroids.to_crs(
    "EPSG:4326"
)


centroids["centroid_lon"] = (
    centroids.geometry.x
)

centroids["centroid_lat"] = (
    centroids.geometry.y
)


# ============================================================
# SAVE SMALL DEPLOYMENT-FRIENDLY TABLE
# ============================================================

centroid_table = pd.DataFrame(
    {
        "gpcode": centroids["gpcode"],
        "gpname": centroids["gpname"],
        "district_code": centroids["dt_lgd"],
        "district": centroids["dtname"],
        "block_code": centroids["blk_lgdcod"],
        "block": centroids["blkname"],
        "centroid_lat": centroids[
            "centroid_lat"
        ].round(6),
        "centroid_lon": centroids[
            "centroid_lon"
        ].round(6),
    }
)


centroid_table.to_csv(
    OUTPUT_CENTROIDS,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 60)
print("CLEAN PANCHAYAT DATASET COMPLETE")
print("=" * 60)

print(
    f"Logical Panchayats: "
    f"{len(gdf):,}"
)

print(
    f"Centroid records: "
    f"{len(centroid_table):,}"
)

print(
    f"Missing GP codes: "
    f"{centroid_table['gpcode'].isna().sum():,}"
)

print(
    f"Missing GP names: "
    f"{centroid_table['gpname'].isna().sum():,}"
)

print()
print(
    f"GIS layer: {OUTPUT_GPKG}"
)

print(
    f"Centroid table: {OUTPUT_CENTROIDS}"
)