from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "india_chirps_daily_2025-07.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "india_chirps_coarse_0.25_daily_2025-07.csv"
)

COARSE_RESOLUTION = 0.25


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    print("Reading:", INPUT_FILE)

    df = pd.read_csv(INPUT_FILE)

    print("Fine rows:", len(df))

    # Assign every 0.05° cell to a 0.25° coarse cell.
    df["lat_index"] = np.floor(
        df["latitude"] / COARSE_RESOLUTION
    ).astype(int)

    df["lon_index"] = np.floor(
        df["longitude"] / COARSE_RESOLUTION
    ).astype(int)

    # Calculate the mean rainfall of the 0.05° cells
    # inside each 0.25° cell for each date.
    coarse = (
        df.groupby(
            [
                "date",
                "lat_index",
                "lon_index",
            ],
            as_index=False,
        )
        .agg(
            rainfall_mm=("rainfall_mm", "mean"),
            fine_cell_count=(
                "rainfall_mm",
                "count",
            ),
        )
    )

    # Convert grid indices back to approximate
    # coarse-cell center coordinates.
    coarse["latitude"] = (
        coarse["lat_index"]
        * COARSE_RESOLUTION
        + COARSE_RESOLUTION / 2
    )

    coarse["longitude"] = (
        coarse["lon_index"]
        * COARSE_RESOLUTION
        + COARSE_RESOLUTION / 2
    )

    coarse = coarse[
        [
            "date",
            "latitude",
            "longitude",
            "lat_index",
            "lon_index",
            "rainfall_mm",
            "fine_cell_count",
        ]
    ]

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    coarse.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print("Coarse grid created.")
    print("Output:", OUTPUT_FILE)
    print("Coarse rows:", len(coarse))

    print(
        "Number of dates:",
        coarse["date"].nunique(),
    )

    print(
        "Complete coarse cells:",
        int(
            (
                coarse["fine_cell_count"] == 25
            ).sum()
        ),
    )

    print("\nRainfall statistics:")

    print(
        "Minimum:",
        coarse["rainfall_mm"].min(),
    )

    print(
        "Maximum:",
        coarse["rainfall_mm"].max(),
    )

    print(
        "Mean:",
        coarse["rainfall_mm"].mean(),
    )

    print("\nRows per date:")

    print(
        coarse.groupby("date")
        .size()
        .to_string()
    )

    print("\nSample:")

    print(
        coarse.head(10).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()