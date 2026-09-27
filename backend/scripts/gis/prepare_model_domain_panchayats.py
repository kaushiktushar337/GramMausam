from pathlib import Path
import json

from shapely.geometry import shape, box


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "gis"
    / "up_panchayats.geojsonl"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "gis"
    / "model_domain_panchayats.geojsonl"
)


# ============================================================
# MODEL DOMAIN
# ============================================================

MIN_LON = 77.125
MAX_LON = 84.375
MIN_LAT = 23.875
MAX_LAT = 30.375

DOMAIN = box(
    MIN_LON,
    MIN_LAT,
    MAX_LON,
    MAX_LAT,
)


# ============================================================
# SOURCE FIELDS
# ============================================================

KEEP_FIELDS = [
    "gpcode",
    "gpname",
    "gp_code",
    "gp_name",
    "dt_lgd",
    "dtname",
    "blk_lgdcod",
    "blkname",
    "block_name",
    "sdt_lgd",
    "sdtname",
    "st_lgd",
    "stname",
]


# ============================================================
# START
# ============================================================

print("=" * 60)
print("PREPARING MODEL-DOMAIN PANCHAYAT DATA")
print("=" * 60)

print(
    f"Input:  {INPUT_FILE}"
)

print(
    f"Output: {OUTPUT_FILE}"
)

print()
print("Model domain:")
print(
    f"Longitude: {MIN_LON} → {MAX_LON}"
)

print(
    f"Latitude : {MIN_LAT} → {MAX_LAT}"
)


if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Input file not found:\n{INPUT_FILE}"
    )


# Remove old output
if OUTPUT_FILE.exists():
    OUTPUT_FILE.unlink()


# ============================================================
# COUNTERS
# ============================================================

records_read = 0
records_kept = 0
invalid_records = 0

polygon_count = 0
multipolygon_count = 0

gp_codes = set()


# ============================================================
# STREAM SOURCE FILE
# ============================================================

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8",
) as source, open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8",
) as target:

    for line in source:

        line = line.strip()

        if not line:
            continue

        records_read += 1

        try:

            feature = json.loads(line)

            geometry_data = feature.get(
                "geometry"
            )

            properties = feature.get(
                "properties",
                {}
            )

            if not geometry_data:
                invalid_records += 1
                continue

            geometry = shape(
                geometry_data
            )

            if geometry.is_empty:
                invalid_records += 1
                continue

            # Quick spatial test
            if not geometry.intersects(DOMAIN):
                continue

            # ------------------------------------------------
            # Keep only useful attributes
            # ------------------------------------------------

            filtered_properties = {}

            for field in KEEP_FIELDS:

                if field in properties:
                    filtered_properties[field] = (
                        properties[field]
                    )

            # ------------------------------------------------
            # Track GP code
            # ------------------------------------------------

            gp_code = (
                properties.get("gpcode")
                or properties.get("gp_code")
            )

            if gp_code is not None:
                gp_codes.add(
                    str(gp_code)
                )

            # ------------------------------------------------
            # Geometry count
            # ------------------------------------------------

            if geometry.geom_type == "Polygon":
                polygon_count += 1

            elif geometry.geom_type == "MultiPolygon":
                multipolygon_count += 1

            # ------------------------------------------------
            # Output feature
            # ------------------------------------------------

            output_feature = {
                "type": "Feature",
                "geometry": geometry_data,
                "properties": filtered_properties,
            }

            target.write(
                json.dumps(
                    output_feature,
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                + "\n"
            )

            records_kept += 1

        except Exception:
            invalid_records += 1


# ============================================================
# OUTPUT SIZE
# ============================================================

output_size_mb = (
    OUTPUT_FILE.stat().st_size
    / (1024 * 1024)
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("MODEL-DOMAIN EXTRACTION COMPLETE")
print("=" * 60)

print(
    f"Records read          : {records_read:,}"
)

print(
    f"Records kept          : {records_kept:,}"
)

print(
    f"Unique GP codes       : {len(gp_codes):,}"
)

print(
    f"Polygon features      : {polygon_count:,}"
)

print(
    f"MultiPolygon features : {multipolygon_count:,}"
)

print(
    f"Invalid during filter : {invalid_records:,}"
)

print(
    f"Output size           : "
    f"{output_size_mb:.2f} MB"
)

print()
print(
    f"Output: {OUTPUT_FILE}"
)

print()
print(
    "The national Panchayat dataset remains "
    "outside the project working dataset."
)