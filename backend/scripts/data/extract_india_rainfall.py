from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds


INPUT_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "chirps"
    / "chirps-v3.0.sat.2025.04.24.tif"
)

OUTPUT_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "india_rainfall_2025-04-24.csv"
)


def main():
    # Approximate bounding box covering India
    west = 68.0
    south = 6.0
    east = 98.0
    north = 38.0

    with rasterio.open(INPUT_FILE) as src:
        window = from_bounds(
            west,
            south,
            east,
            north,
            transform=src.transform,
        )

        window = (
            window
            .round_offsets()
            .round_lengths()
        )

        rainfall = src.read(1, window=window)

        transform = src.window_transform(window)

        # Create row/column indices
        rows, cols = np.indices(rainfall.shape)

        # Flatten them before converting to coordinates
        row_indices = rows.ravel()
        col_indices = cols.ravel()

        xs, ys = rasterio.transform.xy(
            transform,
            row_indices,
            col_indices,
            offset="center",
        )

        longitude = np.asarray(xs)
        latitude = np.asarray(ys)

        # Flatten rainfall to match coordinate arrays
        rainfall_values = rainfall.astype(float).ravel()

        # CHIRPS missing-value sentinel
        rainfall_values[rainfall_values < -9000] = np.nan

        valid_mask = np.isfinite(rainfall_values)

        df = pd.DataFrame(
            {
                "latitude": latitude[valid_mask],
                "longitude": longitude[valid_mask],
                "rainfall_mm": rainfall_values[valid_mask],
            }
        )

        OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        df.to_csv(
            OUTPUT_FILE,
            index=False,
        )

        print("Input:", INPUT_FILE.name)
        print("Subset shape:", rainfall.shape)
        print("Valid grid cells:", len(df))
        print("Output:", OUTPUT_FILE)

        print(
            "Rainfall min:",
            float(df["rainfall_mm"].min()),
        )

        print(
            "Rainfall max:",
            float(df["rainfall_mm"].max()),
        )

        print(
            "Rainfall mean:",
            float(df["rainfall_mm"].mean()),
        )


if __name__ == "__main__":
    main()