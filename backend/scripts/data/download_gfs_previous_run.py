from pathlib import Path

import pandas as pd
import requests
import time


BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "gfs_previous_day1_up_2025-07.csv"
)


API_URL = (
    "https://previous-runs-api.open-meteo.com/v1/forecast"
)


# --------------------------------------------------
# Approximate working area for Uttar Pradesh.
# Later we will apply the exact state boundary.
# --------------------------------------------------

LAT_START = 23.875
LAT_END = 30.375

LON_START = 77.125
LON_END = 84.375

GRID_STEP = 0.25


START_DATE = "2025-07-01"
END_DATE = "2025-07-31"

BATCH_SIZE = 40


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

    response = requests.get(
        API_URL,
        params=params,
        timeout=180,
    )

    response.raise_for_status()

    data = response.json()

    if isinstance(data, dict) and data.get("error"):
        raise RuntimeError(
            data.get(
                "reason",
                "Open-Meteo API error",
            )
        )

    if isinstance(data, dict):
        data = [data]

    return data


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

    # Aggregate 24 hourly forecast values into
    # one daily precipitation value.
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

    # Keep both the requested grid coordinate and
    # the actual model grid coordinate returned by
    # Open-Meteo.
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


def main():
    points = build_grid()

    print(
        "Grid points:",
        len(points),
    )

    print(
        "Date range:",
        START_DATE,
        "to",
        END_DATE,
    )

    total_batches = (
        len(points) + BATCH_SIZE - 1
    ) // BATCH_SIZE

    print(
        "Expected API batches:",
        total_batches,
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    all_rows = []

    for batch_start in range(
        0,
        len(points),
        BATCH_SIZE,
    ):
        batch = points[
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

            if len(locations) != len(batch):
                print(
                    "Warning: number of returned "
                    "locations does not match "
                    "requested points."
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
                    all_rows.extend(
                        rows.to_dict(
                            "records"
                        )
                    )

        except Exception as error:
            print(
                "Batch failed:",
                error,
            )

        time.sleep(0.5)

    if not all_rows:
        raise RuntimeError(
            "No forecast records were created."
        )

    result = pd.DataFrame(
        all_rows
    )

    result = result.sort_values(
        [
            "date",
            "requested_latitude",
            "requested_longitude",
        ]
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nDownload complete.")

    print(
        "Rows:",
        len(result),
    )

    print(
        "Unique dates:",
        result["date"].nunique(),
    )

    print(
        "Unique requested grid points:",
        result[
            [
                "requested_latitude",
                "requested_longitude",
            ]
        ]
        .drop_duplicates()
        .shape[0],
    )

    print(
        "Forecast rainfall minimum:",
        result[
            "forecast_rainfall_mm"
        ].min(),
    )

    print(
        "Forecast rainfall maximum:",
        result[
            "forecast_rainfall_mm"
        ].max(),
    )

    print(
        "Forecast rainfall mean:",
        result[
            "forecast_rainfall_mm"
        ].mean(),
    )

    print(
        "\nOutput:",
        OUTPUT_FILE,
    )

    print("\nSample:")

    print(
        result.head(10).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()