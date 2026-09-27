from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "india_chirps_daily_2025-07.csv"
)

CHUNK_SIZE = 250_000


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    total_rows = 0
    total_nonzero = 0

    daily_stats = []

    print("Reading dataset in chunks...")
    print("File:", INPUT_FILE)

    for chunk in pd.read_csv(
        INPUT_FILE,
        chunksize=CHUNK_SIZE,
    ):
        total_rows += len(chunk)

        total_nonzero += (
            chunk["rainfall_mm"] > 0
        ).sum()

        grouped = chunk.groupby("date")[
            "rainfall_mm"
        ].agg(
            ["min", "max", "mean", "median"]
        )

        for date_value, row in grouped.iterrows():
            daily_stats.append(
                {
                    "date": date_value,
                    "min": row["min"],
                    "max": row["max"],
                    "mean": row["mean"],
                    "median": row["median"],
                }
            )

    daily = (
        pd.DataFrame(daily_stats)
        .groupby("date", as_index=False)
        .agg(
            min=("min", "min"),
            max=("max", "max"),
            mean=("mean", "mean"),
            median=("median", "mean"),
        )
    )

    print("\nDataset summary")
    print("----------------")
    print("Total rows:", total_rows)

    print(
        "Non-zero rainfall cells:",
        int(total_nonzero),
    )

    print(
        "Zero rainfall percentage:",
        round(
            (1 - total_nonzero / total_rows) * 100,
            2,
        ),
        "%",
    )

    print("\nDate range:")
    print(
        daily["date"].min(),
        "to",
        daily["date"].max(),
    )

    print("\nDaily rainfall statistics:")
    print(
        daily.to_string(index=False)
    )


if __name__ == "__main__":
    main()