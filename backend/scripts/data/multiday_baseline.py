from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

FINE_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "india_chirps_daily_2025-07.csv"
)

COARSE_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "india_chirps_coarse_0.25_daily_2025-07.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "multiday_baseline_2025-07.csv"
)

COARSE_RESOLUTION = 0.25
CHUNK_SIZE = 500_000


def main():
    if not FINE_FILE.exists():
        raise FileNotFoundError(
            f"Fine file not found: {FINE_FILE}"
        )

    if not COARSE_FILE.exists():
        raise FileNotFoundError(
            f"Coarse file not found: {COARSE_FILE}"
        )

    print("Reading coarse dataset...")

    coarse = pd.read_csv(COARSE_FILE)

    # Only use complete coarse cells.
    coarse = coarse[
        coarse["fine_cell_count"] == 25
    ].copy()

    coarse = coarse[
        [
            "date",
            "lat_index",
            "lon_index",
            "rainfall_mm",
        ]
    ]

    coarse = coarse.rename(
        columns={
            "rainfall_mm": "coarse_rainfall_mm"
        }
    )

    print(
        "Complete coarse rows:",
        len(coarse),
    )

    print("\nProcessing fine dataset in chunks...")

    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    total_rows = 0
    total_squared_error = 0.0
    total_absolute_error = 0.0

    daily_results = []

    for chunk_number, fine in enumerate(
        pd.read_csv(
            FINE_FILE,
            chunksize=CHUNK_SIZE,
        ),
        start=1,
    ):
        print(
            f"Chunk {chunk_number}: "
            f"{len(fine)} rows"
        )

        fine["lat_index"] = np.floor(
            fine["latitude"]
            / COARSE_RESOLUTION
        ).astype(int)

        fine["lon_index"] = np.floor(
            fine["longitude"]
            / COARSE_RESOLUTION
        ).astype(int)

        merged = fine.merge(
            coarse,
            on=[
                "date",
                "lat_index",
                "lon_index",
            ],
            how="inner",
        )

        if merged.empty:
            continue

        merged["baseline_rainfall_mm"] = (
            merged["coarse_rainfall_mm"]
        )

        error = (
            merged["baseline_rainfall_mm"]
            - merged["rainfall_mm"]
        )

        total_rows += len(merged)

        total_absolute_error += (
            np.abs(error).sum()
        )

        total_squared_error += (
            np.square(error).sum()
        )

        # Daily metrics for this chunk.
        for date_value, group in merged.groupby(
            "date"
        ):
            group_error = (
                group["baseline_rainfall_mm"]
                - group["rainfall_mm"]
            )

            daily_results.append(
                {
                    "date": date_value,
                    "rows": len(group),
                    "mae": np.abs(
                        group_error
                    ).mean(),
                    "rmse": np.sqrt(
                        np.square(
                            group_error
                        ).mean()
                    ),
                }
            )

        # Save only the useful columns.
        output_chunk = merged[
            [
                "date",
                "latitude",
                "longitude",
                "rainfall_mm",
                "coarse_rainfall_mm",
                "baseline_rainfall_mm",
            ]
        ]

        output_chunk.to_csv(
            OUTPUT_FILE,
            mode="a",
            header=not OUTPUT_FILE.exists(),
            index=False,
        )

    if total_rows == 0:
        raise RuntimeError(
            "No fine cells matched the complete "
            "coarse cells."
        )

    overall_mae = (
        total_absolute_error
        / total_rows
    )

    overall_rmse = np.sqrt(
        total_squared_error
        / total_rows
    )

    daily = pd.DataFrame(
        daily_results
    )

    print("\nBaseline evaluation")
    print("-------------------")

    print(
        "Fine cells evaluated:",
        total_rows,
    )

    print(
        "Overall MAE:",
        float(overall_mae),
        "mm",
    )

    print(
        "Overall RMSE:",
        float(overall_rmse),
        "mm",
    )

    print(
        "\nDaily MAE range:",
        float(daily["mae"].min()),
        "to",
        float(daily["mae"].max()),
        "mm",
    )

    print(
        "Daily RMSE range:",
        float(daily["rmse"].min()),
        "to",
        float(daily["rmse"].max()),
        "mm",
    )

    print(
        "\nOutput:",
        OUTPUT_FILE,
    )

    print("\nDaily results:")
    print(
        daily.sort_values("date")
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()