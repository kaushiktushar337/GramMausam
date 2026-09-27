from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parents[2]

FILE = BASE_DIR / "data" / "gis" / "up_panchayats.geojsonl"

print("=" * 60)
print("PANCHAYAT DATASET INSPECTION")
print("=" * 60)

print(f"File: {FILE}")
print(f"Exists: {FILE.exists()}")

if not FILE.exists():
    raise FileNotFoundError(FILE)

print(
    f"Size: "
    f"{FILE.stat().st_size / (1024 * 1024):.2f} MB"
)

total = 0
valid = 0
invalid = 0

geometry_types = {}
property_keys = set()

sample = None

with open(
    FILE,
    "r",
    encoding="utf-8"
) as f:

    for line in f:

        line = line.strip()

        if not line:
            continue

        total += 1

        try:
            feature = json.loads(line)

            if sample is None:
                sample = feature

            valid += 1

            geometry = feature.get(
                "geometry"
            )

            if geometry:
                geom_type = geometry.get(
                    "type",
                    "UNKNOWN"
                )

                geometry_types[geom_type] = (
                    geometry_types.get(
                        geom_type,
                        0
                    ) + 1
                )

            properties = feature.get(
                "properties",
                {}
            )

            if isinstance(properties, dict):
                property_keys.update(
                    properties.keys()
                )

        except Exception:
            invalid += 1


print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)

print(f"Total records : {total:,}")
print(f"Valid records : {valid:,}")
print(f"Invalid       : {invalid:,}")

print()
print("Geometry types:")

for geom_type, count in sorted(
    geometry_types.items()
):
    print(
        f"  {geom_type}: {count:,}"
    )

print()
print("Property fields:")

for key in sorted(property_keys):
    print(
        f"  {key}"
    )

print()
print("=" * 60)
print("SAMPLE RECORD")
print("=" * 60)

if sample:
    print(
        json.dumps(
            sample,
            indent=2,
            ensure_ascii=False
        )[:5000]
    )
else:
    print("No records found.")