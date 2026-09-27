from pathlib import Path
import json
from collections import Counter


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "gis"
    / "model_domain_panchayats.geojsonl"
)


print("=" * 60)
print("INSPECTING BLANK GP-CODE RECORDS")
print("=" * 60)

blank_count = 0

geometry_types = Counter()

field_values = {
    "stname": Counter(),
    "dtname": Counter(),
    "blkname": Counter(),
    "gpname": Counter(),
    "gp_code": Counter(),
    "gpcode": Counter(),
    "d_pan_name": Counter(),
    "b_pan_name": Counter(),
    "pan_local": Counter(),
}

samples = []


with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:

    for line in f:

        line = line.strip()

        if not line:
            continue

        feature = json.loads(line)

        properties = feature.get(
            "properties",
            {}
        )

        gpcode = properties.get("gpcode")
        gp_code = properties.get("gp_code")

        gpcode_text = (
            ""
            if gpcode is None
            else str(gpcode).strip()
        )

        gp_code_text = (
            ""
            if gp_code is None
            else str(gp_code).strip()
        )

        # Treat both GP-code fields as blank if neither
        # contains a usable value.
        if not gpcode_text and not gp_code_text:

            blank_count += 1

            geometry = feature.get(
                "geometry",
                {}
            )

            geometry_types[
                geometry.get("type", "UNKNOWN")
            ] += 1

            for field in field_values:

                value = properties.get(field)

                if value is None:
                    value = "<NONE>"
                else:
                    value = str(value).strip()

                    if not value:
                        value = "<BLANK>"

                field_values[field][value] += 1

            if len(samples) < 10:

                samples.append(
                    {
                        "properties": properties,
                        "geometry_type": geometry.get(
                            "type",
                            "UNKNOWN"
                        ),
                    }
                )


print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)

print(
    f"Blank GP-code records: "
    f"{blank_count:,}"
)

print()
print("Geometry types:")

for key, value in geometry_types.items():
    print(
        f"  {key}: {value:,}"
    )


print()
print("=" * 60)
print("FIELD VALUES AMONG BLANK GP-CODE RECORDS")
print("=" * 60)


for field, counter in field_values.items():

    print()
    print(f"{field}:")

    for value, count in counter.most_common(15):

        print(
            f"  {repr(value)}: {count:,}"
        )


print()
print("=" * 60)
print("SAMPLE RECORDS")
print("=" * 60)


for i, sample in enumerate(samples, start=1):

    print()
    print(f"--- Sample {i} ---")

    print(
        f"Geometry: "
        f"{sample['geometry_type']}"
    )

    print(
        json.dumps(
            sample["properties"],
            indent=2,
            ensure_ascii=False
        )
    )


print()
print("=" * 60)
print("DONE")
print("=" * 60)