from pathlib import Path

import numpy as np
import pandas as pd


INPUT_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "india_rainfall_2025-04-24.csv"
)

OUTPUT_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "india_rainfall_coarse_0.25_2025-04-24.csv"
)


COARSE_RESOLUTION = 0.25


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    # Assign each 0.05° cell to a 0.25° coarse cell.
    df["lat_index"] = np.floor(
        df["latitude"] / COARSE_RESOLUTION
    ).astype(int)

    df["lon_index"] = np.floor(
        df["longitude"] / COARSE_RESOLUTION
    ).astype(int)

    coarse = (
        df.groupby(
            ["lat_index", "lon_index"],
            as_index=False,
        )
        .agg(
            rainfall_mm=("rainfall_mm", "mean"),
            fine_cell_count=("rainfall_mm", "count"),
        )
    )

    # Convert coarse grid indices back to cell centers.
    coarse["latitude"] = (
        coarse["lat_index"] * COARSE_RESOLUTION
        + COARSE_RESOLUTION / 2
    )

    coarse["longitude"] = (
        coarse["lon_index"] * COARSE_RESOLUTION
        + COARSE_RESOLUTION / 2
    )

    coarse = coarse[
        [
            "latitude",
            "longitude",
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

    print("Input:", INPUT_FILE.name)
    print("Fine cells:", len(df))
    print("Coarse cells:", len(coarse))
    print("Output:", OUTPUT_FILE)

    print(
        "\nCoarse rainfall range:"
    )

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

    print("\nFine cells per coarse cell:")

    print(
        coarse["fine_cell_count"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nSample rows:")

    print(
        coarse.head(10).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()