from pathlib import Path
import time

import pandas as pd
import requests


BASE_DIR = Path(__file__).resolve().parents[2]

EXISTING_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gfs_previous_day1_up_2025-07.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gfs_previous_day1_up_2025-07_complete.csv"
)

API_URL = (
    "https://previous-runs-api.open-meteo.com/v1/forecast"
)


LAT_START = 23.875
LAT_END = 30.375

LON_START = 77.125
LON_END = 84.375

GRID_STEP = 0.25


START_DATE = "2025-07-01"
END_DATE = "2025-07-31"

# Smaller batches to reduce API load.
BATCH_SIZE = 10

# Pause after successful requests.
REQUEST_DELAY = 15

# Maximum retry attempts for a 429.
MAX_RETRIES = 5


def build_grid():
    points = []

    lat = LAT_START

    while lat <= LAT_END + 0.0001:
        lon = LON_START

        while lon <= LON_END + 0.0001:
            points.append(
                (
                    round(lat, 3),
                    round(lon, 3),
                )
            )

            lon += GRID_STEP

        lat += GRID_STEP

    return points


def process_location(
    location,
    requested_point,
):
    hourly = location.get(
        "hourly",
        {},
    )

    times = hourly.get(
        "time",
        [],
    )

    precipitation = hourly.get(
        "precipitation_previous_day1",
        [],
    )

    if not times or not precipitation:
        return pd.DataFrame()

    frame = pd.DataFrame(
        {
            "time": pd.to_datetime(
                times,
                utc=True,
            ),
            "precipitation_mm": precipitation,
        }
    )

    frame["date"] = (
        frame["time"]
        .dt.strftime("%Y-%m-%d")
    )

    daily = (
        frame.groupby(
            "date",
            as_index=False,
        )["precipitation_mm"]
        .sum()
    )

    daily["requested_latitude"] = (
        requested_point[0]
    )

    daily["requested_longitude"] = (
        requested_point[1]
    )

    daily["model_latitude"] = (
        location.get("latitude")
    )

    daily["model_longitude"] = (
        location.get("longitude")
    )

    daily = daily.rename(
        columns={
            "precipitation_mm":
                "forecast_rainfall_mm"
        }
    )

    return daily[
        [
            "date",
            "requested_latitude",
            "requested_longitude",
            "model_latitude",
            "model_longitude",
            "forecast_rainfall_mm",
        ]
    ]


def fetch_batch(points):
    latitudes = ",".join(
        str(point[0])
        for point in points
    )

    longitudes = ",".join(
        str(point[1])
        for point in points
    )

    params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": "precipitation_previous_day1",
        "models": "gfs_global",
        "timezone": "UTC",
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                API_URL,
                params=params,
                timeout=180,
            )

            if response.status_code == 429:
                retry_after = response.headers.get(
                    "Retry-After"
                )

                if retry_after:
                    wait_time = float(
                        retry_after
                    )
                else:
                    wait_time = min(
                        60 * attempt,
                        300,
                    )

                print(
                    f"429 rate limit. "
                    f"Waiting {wait_time:.0f}s "
                    f"(attempt {attempt}/{MAX_RETRIES})"
                )

                time.sleep(wait_time)
                continue

            response.raise_for_status()

            data = response.json()

            if isinstance(data, dict) and data.get(
                "error"
            ):
                raise RuntimeError(
                    data.get(
                        "reason",
                        "Open-Meteo API error",
                    )
                )

            if isinstance(data, dict):
                data = [data]

            return data

        except requests.RequestException as error:
            if attempt == MAX_RETRIES:
                raise

            wait_time = min(
                30 * attempt,
                180,
            )

            print(
                f"Request failed: {error}"
            )

            print(
                f"Retrying in {wait_time}s..."
            )

            time.sleep(wait_time)

    raise RuntimeError(
        "Unable to fetch batch."
    )


def main():
    if not EXISTING_FILE.exists():
        raise FileNotFoundError(
            f"Existing GFS file not found: "
            f"{EXISTING_FILE}"
        )

    existing = pd.read_csv(
        EXISTING_FILE
    )

    print(
        "Existing rows:",
        len(existing),
    )

    # Identify grid points already downloaded.
    completed_points = set(
        zip(
            existing[
                "requested_latitude"
            ],
            existing[
                "requested_longitude"
            ],
        )
    )

    all_points = build_grid()

    remaining_points = [
        point
        for point in all_points
        if point not in completed_points
    ]

    print(
        "Total grid points:",
        len(all_points),
    )

    print(
        "Completed grid points:",
        len(completed_points),
    )

    print(
        "Remaining grid points:",
        len(remaining_points),
    )

    if not remaining_points:
        print(
            "\nAll grid points are already "
            "downloaded."
        )

        existing.to_csv(
            OUTPUT_FILE,
            index=False,
        )

        print(
            "Complete file:",
            OUTPUT_FILE,
        )

        return

    new_rows = []

    total_batches = (
        len(remaining_points)
        + BATCH_SIZE
        - 1
    ) // BATCH_SIZE

    for batch_start in range(
        0,
        len(remaining_points),
        BATCH_SIZE,
    ):
        batch = remaining_points[
            batch_start:
            batch_start + BATCH_SIZE
        ]

        batch_number = (
            batch_start // BATCH_SIZE
        ) + 1

        print(
            f"\nBatch "
            f"{batch_number}/{total_batches}"
        )

        print(
            "Points:",
            len(batch),
        )

        try:
            locations = fetch_batch(batch)

            print(
                "Locations returned:",
                len(locations),
            )

            for index, location in enumerate(
                locations
            ):
                if index >= len(batch):
                    break

                rows = process_location(
                    location,
                    batch[index],
                )

                if not rows.empty:
                    new_rows.extend(
                        rows.to_dict(
                            "records"
                        )
                    )

        except Exception as error:
            print(
                "Batch failed:",
                error,
            )

        time.sleep(
            REQUEST_DELAY
        )

    if not new_rows:
        raise RuntimeError(
            "No new forecast records were obtained."
        )

    new_data = pd.DataFrame(
        new_rows
    )

    combined = pd.concat(
        [
            existing,
            new_data,
        ],
        ignore_index=True,
    )

    combined = combined.drop_duplicates(
        subset=[
            "date",
            "requested_latitude",
            "requested_longitude",
        ]
    )

    combined = combined.sort_values(
        [
            "date",
            "requested_latitude",
            "requested_longitude",
        ]
    )

    combined.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    unique_points = combined[
        [
            "requested_latitude",
            "requested_longitude",
        ]
    ].drop_duplicates()

    print("\nResume complete.")
    print(
        "Total rows:",
        len(combined),
    )

    print(
        "Unique dates:",
        combined["date"].nunique(),
    )

    print(
        "Unique grid points:",
        len(unique_points),
    )

    print(
        "Expected maximum rows:",
        len(all_points) * 31,
    )

    print(
        "Output:",
        OUTPUT_FILE,
    )


if __name__ == "__main__":
    main()