import argparse
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "panchayat",
    "date",
    "coarse_rainfall",
    "coarse_max_temp",
    "coarse_min_temp",
    "coarse_humidity",
    "coarse_wind_speed",
    "elevation",
    "ndvi",
    "soil_moisture",
    "land_cover_code",
    "observed_rainfall",
    "observed_max_temp",
    "observed_min_temp",
    "observed_humidity",
    "observed_wind_speed",
}

parser = argparse.ArgumentParser(description="Validate a GramMausam training CSV.")
parser.add_argument("csv", type=Path)
args = parser.parse_args()

if not args.csv.exists():
    raise SystemExit(f"File not found: {args.csv}")

frame = pd.read_csv(args.csv)
missing = sorted(REQUIRED_COLUMNS - set(frame.columns))
if missing:
    raise SystemExit(f"Missing columns: {', '.join(missing)}")

if frame.empty:
    raise SystemExit("Dataset is empty")

print(f"Dataset OK: {len(frame)} rows, {len(frame.columns)} columns")
