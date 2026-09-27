from pathlib import Path
from collections import Counter
import json


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "gis"
    / "model_domain_panchayats.geojsonl"
)


print("=" * 60)
print("PANCHAYAT KEY VALIDATION")
print("=" * 60)

print(f"File: {INPUT_FILE}")

if not INPUT_FILE.exists():
    raise FileNotFoundError(INPUT_FILE)


gp_code_counts = Counter()
gp_name_counts = Counter()

records = 0
missing_gp_code = 0
missing_gp_name = 0

code_name_pairs = set()

sample_duplicates = []


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

        gp_code = (
            properties.get("gpcode")
            or properties.get("gp_code")
        )

        gp_name = (
            properties.get("gpname")
            or properties.get("gp_name")
        )

        records += 1

        if gp_code is None:
            missing_gp_code += 1
        else:
            gp_code = str(gp_code).strip()
            gp_code_counts[gp_code] += 1

        if gp_name is None:
            missing_gp_name += 1
        else:
            gp_name = str(gp_name).strip()
            gp_name_counts[gp_name] += 1

        if gp_code and gp_name:
            code_name_pairs.add(
                (gp_code, gp_name)
            )


# ============================================================
# DUPLICATES
# ============================================================

duplicate_codes = {
    code: count
    for code, count in gp_code_counts.items()
    if count > 1
}


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)

print(
    f"Total geometry records : {records:,}"
)

print(
    f"Unique GP codes       : {len(gp_code_counts):,}"
)

print(
    f"Duplicate GP codes    : {len(duplicate_codes):,}"
)

print(
    f"Missing GP codes      : {missing_gp_code:,}"
)

print(
    f"Missing GP names      : {missing_gp_name:,}"
)

print(
    f"Unique GP code/name pairs: "
    f"{len(code_name_pairs):,}"
)


# ============================================================
# DUPLICATE DISTRIBUTION
# ============================================================

print()
print("=" * 60)
print("DUPLICATE CODE DISTRIBUTION")
print("=" * 60)

if duplicate_codes:

    distribution = Counter(
        duplicate_codes.values()
    )

    for number_of_features, number_of_codes in sorted(
        distribution.items()
    ):

        print(
            f"{number_of_codes:,} GP codes "
            f"have {number_of_features} geometry records"
        )

else:

    print(
        "No duplicate GP codes."
    )


# ============================================================
# TOP DUPLICATES
# ============================================================

print()
print("=" * 60)
print("SAMPLE DUPLICATE GP CODES")
print("=" * 60)

for code, count in sorted(
    duplicate_codes.items(),
    key=lambda x: x[1],
    reverse=True
)[:20]:

    print(
        f"{code}: {count} geometry records"
    )


# ============================================================
# CHECK WHETHER ONE CODE HAS MULTIPLE NAMES
# ============================================================

code_to_names = {}

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

        gp_code = (
            properties.get("gpcode")
            or properties.get("gp_code")
        )

        gp_name = (
            properties.get("gpname")
            or properties.get("gp_name")
        )

        if gp_code is None:
            continue

        gp_code = str(gp_code).strip()

        if gp_name is not None:
            code_to_names.setdefault(
                gp_code,
                set()
            ).add(
                str(gp_name).strip()
            )


multiple_name_codes = {
    code: names
    for code, names in code_to_names.items()
    if len(names) > 1
}


print()
print("=" * 60)
print("CODE → MULTIPLE NAME CHECK")
print("=" * 60)

print(
    f"Codes with multiple names: "
    f"{len(multiple_name_codes):,}"
)

for code, names in list(
    multiple_name_codes.items()
)[:20]:

    print(
        f"{code}: {sorted(names)}"
    )


print()
print("=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)