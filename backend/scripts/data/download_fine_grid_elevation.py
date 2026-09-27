from pathlib import Path
import time
import requests
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

TRAINING_FILE = BASE_DIR / "data" / "processed" / (
    "gfs_chirps_training_up_2025-07.csv"
)

OUTPUT_FILE = BASE_DIR / "data" / "processed" / (
    "fine_grid_elevation_up.csv"
)


# ============================================================
# API SETTINGS
# ============================================================

API_URL = "https://api.open-meteo.com/v1/elevation"

BATCH_SIZE = 100

# Conservative delay between requests
REQUEST_DELAY = 10.0

MAX_RETRIES = 5

REQUEST_TIMEOUT = 60


# ============================================================
# LOAD UNIQUE FINE GRID
# ============================================================

print("=" * 60)
print("Loading fine-grid coordinates...")
print("=" * 60)

fine_grid = pd.read_csv(
    TRAINING_FILE,
    usecols=["fine_lat", "fine_lon"]
)

fine_grid = fine_grid.drop_duplicates().reset_index(drop=True)

fine_grid["fine_lat"] = pd.to_numeric(
    fine_grid["fine_lat"],
    errors="coerce"
)

fine_grid["fine_lon"] = pd.to_numeric(
    fine_grid["fine_lon"],
    errors="coerce"
)

fine_grid = fine_grid.dropna(
    subset=["fine_lat", "fine_lon"]
)

fine_grid["fine_lat"] = fine_grid["fine_lat"].round(6)
fine_grid["fine_lon"] = fine_grid["fine_lon"].round(6)

fine_grid = fine_grid.drop_duplicates(
    subset=["fine_lat", "fine_lon"]
).reset_index(drop=True)


print(f"Unique fine-grid points: {len(fine_grid):,}")


# ============================================================
# RESUME FROM EXISTING OUTPUT
# ============================================================

completed = set()

if OUTPUT_FILE.exists():

    print()
    print("Existing elevation file found.")
    print("Reading completed points...")

    existing = pd.read_csv(OUTPUT_FILE)

    required_cols = {
        "fine_lat",
        "fine_lon",
        "elevation_m",
    }

    if required_cols.issubset(existing.columns):

        existing = existing.dropna(
            subset=["fine_lat", "fine_lon", "elevation_m"]
        )

        existing["fine_lat"] = existing["fine_lat"].round(6)
        existing["fine_lon"] = existing["fine_lon"].round(6)

        completed = set(
            zip(
                existing["fine_lat"],
                existing["fine_lon"]
            )
        )

        print(
            f"Already completed: "
            f"{len(completed):,}"
        )

    else:
        print(
            "Existing file does not have the expected columns."
        )
        print(
            "Starting a fresh download."
        )

else:
    print("No existing elevation file found.")


# ============================================================
# FIND REMAINING POINTS
# ============================================================

fine_grid["key"] = list(
    zip(
        fine_grid["fine_lat"],
        fine_grid["fine_lon"]
    )
)

remaining = fine_grid[
    ~fine_grid["key"].isin(completed)
].copy()

remaining = remaining.drop(columns=["key"])

remaining = remaining.reset_index(drop=True)


print(
    f"Remaining points: {len(remaining):,}"
)


if len(remaining) == 0:

    print()
    print("All elevation points are already complete.")

    if OUTPUT_FILE.exists():

        final = pd.read_csv(OUTPUT_FILE)

        final["fine_lat"] = final["fine_lat"].round(6)
        final["fine_lon"] = final["fine_lon"].round(6)

        final = final.drop_duplicates(
            subset=["fine_lat", "fine_lon"]
        ).sort_values(
            ["fine_lat", "fine_lon"]
        ).reset_index(drop=True)

        final.to_csv(
            OUTPUT_FILE,
            index=False
        )

        print(
            f"Final rows: {len(final):,}"
        )
        print(
            f"Output: {OUTPUT_FILE}"
        )

    raise SystemExit


# ============================================================
# API SESSION
# ============================================================

session = requests.Session()

new_rows = []

total_batches = (
    len(remaining) + BATCH_SIZE - 1
) // BATCH_SIZE


# ============================================================
# DOWNLOAD
# ============================================================

for batch_start in range(
    0,
    len(remaining),
    BATCH_SIZE
):

    batch = remaining.iloc[
        batch_start:
        batch_start + BATCH_SIZE
    ]

    batch_number = (
        batch_start // BATCH_SIZE
    ) + 1

    print()
    print(
        f"Batch {batch_number}/{total_batches}"
    )

    print(
        f"Points: {len(batch)}"
    )

    latitudes = ",".join(
        f"{x:.6f}"
        for x in batch["fine_lat"]
    )

    longitudes = ",".join(
        f"{x:.6f}"
        for x in batch["fine_lon"]
    )

    params = {
        "latitude": latitudes,
        "longitude": longitudes,
    }


    success = False

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = session.get(
                API_URL,
                params=params,
                timeout=REQUEST_TIMEOUT
            )


            # ------------------------------------------------
            # RATE LIMIT
            # ------------------------------------------------

            if response.status_code == 429:

                retry_after = response.headers.get(
                    "Retry-After"
                )

                if retry_after:
                    wait_seconds = float(
                        retry_after
                    )
                else:
                    wait_seconds = min(
    120 * attempt,
    600
)

                print(
                    f"HTTP 429. "
                    f"Waiting {wait_seconds:.0f}s..."
                )

                time.sleep(wait_seconds)

                continue


            # ------------------------------------------------
            # OTHER HTTP ERRORS
            # ------------------------------------------------

            response.raise_for_status()

            data = response.json()

            if "elevation" not in data:

                raise ValueError(
                    "API response does not contain "
                    "'elevation'."
                )

            elevations = data["elevation"]

            if len(elevations) != len(batch):

                raise ValueError(
                    "Elevation count does not match "
                    "requested coordinate count."
                )


            # ------------------------------------------------
            # BUILD ROWS
            # ------------------------------------------------

            batch_rows = []

            for (_, row), elevation in zip(
                batch.iterrows(),
                elevations
            ):

                batch_rows.append(
                    {
                        "fine_lat": round(
                            float(row["fine_lat"]),
                            6
                        ),
                        "fine_lon": round(
                            float(row["fine_lon"]),
                            6
                        ),
                        "elevation_m": float(
                            elevation
                        ),
                    }
                )


            new_rows.extend(batch_rows)

            print(
                f"Locations returned: "
                f"{len(elevations)}"
            )

            success = True
            break


        except Exception as e:

            print(
                f"Attempt {attempt}/{MAX_RETRIES} failed: "
                f"{e}"
            )

            if attempt < MAX_RETRIES:

                wait_seconds = min(
                    10 * attempt,
                    60
                )

                print(
                    f"Waiting {wait_seconds}s "
                    f"before retry..."
                )

                time.sleep(wait_seconds)


    # ========================================================
    # SAVE PROGRESS AFTER EVERY BATCH
    # ========================================================

    if not success:

        print()
        print(
            "Batch failed after maximum retries."
        )

        print(
            "Saving all successful batches so far..."
        )

        break


    progress_df = pd.DataFrame(
        new_rows
    )

    if OUTPUT_FILE.exists():

        old_df = pd.read_csv(
            OUTPUT_FILE
        )

        combined = pd.concat(
            [
                old_df,
                progress_df
            ],
            ignore_index=True
        )

    else:

        combined = progress_df


    combined["fine_lat"] = combined[
        "fine_lat"
    ].round(6)

    combined["fine_lon"] = combined[
        "fine_lon"
    ].round(6)

    combined = combined.drop_duplicates(
        subset=["fine_lat", "fine_lon"],
        keep="last"
    )

    combined = combined.sort_values(
        ["fine_lat", "fine_lon"]
    ).reset_index(drop=True)

    combined.to_csv(
        OUTPUT_FILE,
        index=False
    )


    print(
        f"Saved progress: "
        f"{len(combined):,} points"
    )


    if batch_number < total_batches:

        time.sleep(
            REQUEST_DELAY
        )


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 60)
print("ELEVATION DOWNLOAD SUMMARY")
print("=" * 60)


if OUTPUT_FILE.exists():

    final = pd.read_csv(
        OUTPUT_FILE
    )

    final["fine_lat"] = final[
        "fine_lat"
    ].round(6)

    final["fine_lon"] = final[
        "fine_lon"
    ].round(6)

    final = final.drop_duplicates(
        subset=["fine_lat", "fine_lon"]
    ).sort_values(
        ["fine_lat", "fine_lon"]
    ).reset_index(drop=True)

    final.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"Elevation rows: {len(final):,}"
    )

    print(
        f"Elevation min: "
        f"{final['elevation_m'].min():.2f} m"
    )

    print(
        f"Elevation max: "
        f"{final['elevation_m'].max():.2f} m"
    )

    print(
        f"Elevation mean: "
        f"{final['elevation_m'].mean():.2f} m"
    )

    print(
        f"Missing elevations: "
        f"{final['elevation_m'].isna().sum()}"
    )

    print()
    print(
        f"Expected points: "
        f"{len(fine_grid):,}"
    )

    print(
        f"Completed points: "
        f"{len(final):,}"
    )

    print()
    print(
        f"Output: {OUTPUT_FILE}"
    )

else:

    print(
        "No output file was created."
    )