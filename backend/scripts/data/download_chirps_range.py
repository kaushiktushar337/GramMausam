from pathlib import Path
from datetime import date, timedelta

import requests


BASE_URL = (
    "https://data.chc.ucsb.edu/"
    "products/CHIRPS/v3.0/"
    "daily/final/sat/"
)

OUTPUT_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "chirps"
)

START_DATE = date(2025, 7, 1)
END_DATE = date(2025, 7, 31)


def download_file(file_date):
    year = file_date.strftime("%Y")
    filename = (
        f"chirps-v3.0.sat."
        f"{file_date.strftime('%Y.%m.%d')}.tif"
    )

    url = f"{BASE_URL}{year}/{filename}"
    output_path = OUTPUT_DIR / filename

    if output_path.exists():
        print(f"Already exists: {filename}")
        return

    print(f"Downloading: {filename}")

    response = requests.get(
        url,
        timeout=120,
    )

    response.raise_for_status()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_bytes(
        response.content
    )

    print(
        f"Saved: {output_path}"
    )


def main():
    current_date = START_DATE

    while current_date <= END_DATE:
        try:
            download_file(current_date)
        except requests.RequestException as error:
            print(
                f"Failed: {current_date} -> {error}"
            )

        current_date += timedelta(days=1)

    print("\nDownload process complete.")


if __name__ == "__main__":
    main()