from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

FINE_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "india_rainfall_2025-04-24.csv"
)

COARSE_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "india_rainfall_coarse_0.25_2025-04-24.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "baseline_downscaled_2025-04-24.csv"
)

COARSE_RESOLUTION = 0.25


def calculate_metrics(actual, predicted):
    error = predicted - actual

    mae = np.mean(np.abs(error))
    rmse = np.sqrt(np.mean(error ** 2))

    return mae, rmse


def main():
    if not FINE_FILE.exists():
        raise FileNotFoundError(
            f"Fine dataset not found: {FINE_FILE}"
        )

    if not COARSE_FILE.exists():
        raise FileNotFoundError(
            f"Coarse dataset not found: {COARSE_FILE}"
        )

    fine = pd.read_csv(FINE_FILE)
    coarse = pd.read_csv(COARSE_FILE)

    # Identify the coarse cell belonging to each fine cell.
    fine["lat_index"] = np.floor(
        fine["latitude"] / COARSE_RESOLUTION
    ).astype(int)

    fine["lon_index"] = np.floor(
        fine["longitude"] / COARSE_RESOLUTION
    ).astype(int)

    # Recover the same indices from the coarse cell centers.
    coarse["lat_index"] = np.floor(
        coarse["latitude"] / COARSE_RESOLUTION
    ).astype(int)

    coarse["lon_index"] = np.floor(
        coarse["longitude"] / COARSE_RESOLUTION
    ).astype(int)

    # Keep only complete coarse cells.
    complete_coarse = coarse[
        coarse["fine_cell_count"] == 25
    ][
        [
            "lat_index",
            "lon_index",
            "rainfall_mm",
        ]
    ].copy()

    complete_coarse = complete_coarse.rename(
        columns={
            "rainfall_mm": "coarse_rainfall_mm"
        }
    )

    # Attach the coarse value to every fine cell.
    baseline = fine.merge(
        complete_coarse,
        on=["lat_index", "lon_index"],
        how="inner",
    )

    # Simple baseline:
    # every fine cell gets the mean of its coarse cell.
    baseline["baseline_rainfall_mm"] = (
        baseline["coarse_rainfall_mm"]
    )

    actual = baseline["rainfall_mm"].to_numpy()
    predicted = baseline[
        "baseline_rainfall_mm"
    ].to_numpy()

    mae, rmse = calculate_metrics(
        actual,
        predicted,
    )

    baseline = baseline[
        [
            "latitude",
            "longitude",
            "rainfall_mm",
            "coarse_rainfall_mm",
            "baseline_rainfall_mm",
        ]
    ]

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    baseline.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("Fine dataset:", FINE_FILE.name)
    print("Coarse dataset:", COARSE_FILE.name)

    print(
        "\nComplete coarse cells:",
        len(complete_coarse),
    )

    print(
        "Fine cells used for evaluation:",
        len(baseline),
    )

    print(
        "\nBaseline MAE:",
        float(mae),
        "mm",
    )

    print(
        "Baseline RMSE:",
        float(rmse),
        "mm",
    )

    print(
        "\nOutput:",
        OUTPUT_FILE,
    )

    print("\nSample:")
    print(
        baseline.head(10).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()