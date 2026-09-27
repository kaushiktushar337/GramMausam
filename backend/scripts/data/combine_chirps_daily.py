from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import from_bounds


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_DIR = (
    BASE_DIR
    / "data"
    / "raw"
    / "chirps"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "india_chirps_daily_2025-07.csv"
)


WEST = 68.0
SOUTH = 6.0
EAST = 98.0
NORTH = 38.0


def process_file(file_path):
    with rasterio.open(file_path) as src:
        window = from_bounds(
            WEST,
            SOUTH,
            EAST,
            NORTH,
            transform=src.transform,
        )

        window = (
            window
            .round_offsets()
            .round_lengths()
        )

        rainfall = src.read(
            1,
            window=window,
        ).astype(float)

        transform = src.window_transform(
            window
        )

        # Remove CHIRPS missing-value sentinel.
        rainfall[rainfall < -9000] = np.nan

        height, width = rainfall.shape

        # Pixel-center coordinates.
        columns = np.arange(width)
        rows = np.arange(height)

        longitudes = (
            transform.c
            + (columns + 0.5) * transform.a
        )

        latitudes = (
            transform.f
            + (rows + 0.5) * transform.e
        )

        longitude_grid = np.tile(
            longitudes,
            height,
        )

        latitude_grid = np.repeat(
            latitudes,
            width,
        )

        rainfall_values = rainfall.ravel()

        valid_mask = np.isfinite(
            rainfall_values
        )

        date_value = (
            file_path.stem
            .replace(
                "chirps-v3.0.sat.",
                "",
            )
        )

        data = pd.DataFrame(
            {
                "date": date_value,
                "latitude": latitude_grid[
                    valid_mask
                ],
                "longitude": longitude_grid[
                    valid_mask
                ],
                "rainfall_mm": rainfall_values[
                    valid_mask
                ],
            }
        )

        return data


def main():
    files = sorted(
        INPUT_DIR.glob(
            "chirps-v3.0.sat.2025.07.*.tif"
        )
    )

    if not files:
        raise FileNotFoundError(
            "No July 2025 CHIRPS files found."
        )

    print(
        f"Found {len(files)} CHIRPS files."
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Remove an old output file so a rerun
    # does not duplicate rows.
    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    total_rows = 0

    for index, file_path in enumerate(
        files,
        start=1,
    ):
        print(
            f"[{index}/{len(files)}] "
            f"Processing {file_path.name}"
        )

        daily = process_file(file_path)

        daily.to_csv(
            OUTPUT_FILE,
            mode="a",
            header=not OUTPUT_FILE.exists(),
            index=False,
        )

        total_rows += len(daily)

        print(
            f"  Valid cells: {len(daily)}"
        )

    print("\nProcessing complete.")
    print("Days processed:", len(files))
    print("Total rows:", total_rows)
    print("Output:", OUTPUT_FILE)


if __name__ == "__main__":
    main()