from pathlib import Path

import pandas as pd


INPUT_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "india_rainfall_2025-04-24.csv"
)


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"File not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print("File:", INPUT_FILE.name)
    print("Rows:", len(df))
    print("Columns:", list(df.columns))

    print("\nLatitude range:")
    print(
        df["latitude"].min(),
        "to",
        df["latitude"].max(),
    )

    print("\nLongitude range:")
    print(
        df["longitude"].min(),
        "to",
        df["longitude"].max(),
    )

    print("\nRainfall range:")
    print(
        df["rainfall_mm"].min(),
        "to",
        df["rainfall_mm"].max(),
    )

    print("\nMissing values:")
    print(df.isna().sum())

    # Small sample around Prayagraj
    prayagraj = df[
        (df["latitude"].between(25.3, 25.6))
        & (df["longitude"].between(81.7, 82.0))
    ]

    print("\nPrayagraj-area cells:")
    print(len(prayagraj))

    print("\nPrayagraj rainfall statistics:")
    print(
        "Minimum:",
        prayagraj["rainfall_mm"].min(),
    )

    print(
        "Maximum:",
        prayagraj["rainfall_mm"].max(),
    )

    print(
        "Mean:",
        prayagraj["rainfall_mm"].mean(),
    )

    print(
        "Non-zero cells:",
        (prayagraj["rainfall_mm"] > 0).sum(),
    )

    print("\nSample rows:")
    print(
        prayagraj.head(10).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()