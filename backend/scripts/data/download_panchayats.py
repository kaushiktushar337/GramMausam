from pathlib import Path
import json
import time

import requests


SERVICE_URL = (
    "https://bharatnetprogress.nic.in/"
    "nicclouddb/rest/services/"
    "BharatMaps/AllIndiaFeatures/MapServer/6/query"
)

STATE_NAME = "Uttar Pradesh"
BATCH_SIZE = 1000

OUTPUT_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "gis"
    / "up_gram_panchayats.geojson"
)


def get_count(session):
    params = {
        "where": f"STNAME = '{STATE_NAME}'",
        "returnCountOnly": "true",
        "f": "json",
    }

    response = session.get(
        SERVICE_URL,
        params=params,
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise RuntimeError(data["error"])

    return data["count"]


def get_features(session, offset):
    params = {
        "where": f"STNAME = '{STATE_NAME}'",
        "outFields": (
            "OBJECTID,GP_ID,GP_NAME,"
            "BLK_NAME,DTNAME,STNAME"
        ),
        "returnGeometry": "true",
        "outSR": "4326",
        "resultOffset": offset,
        "resultRecordCount": BATCH_SIZE,
        "f": "geojson",
    }

    response = session.get(
        SERVICE_URL,
        params=params,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise RuntimeError(data["error"])

    return data


def main():
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with requests.Session() as session:
        print("Checking Panchayat count...")

        total = get_count(session)

        print(
            f"{STATE_NAME} Panchayats available: {total}"
        )

        all_features = []

        for offset in range(0, total, BATCH_SIZE):
            print(
                f"Downloading "
                f"{offset + 1}-{min(offset + BATCH_SIZE, total)} "
                f"of {total}..."
            )

            data = get_features(
                session,
                offset,
            )

            features = data.get("features", [])

            all_features.extend(features)

            if not features:
                break

            time.sleep(0.2)

        output = {
            "type": "FeatureCollection",
            "features": all_features,
        }

        with open(
            OUTPUT_PATH,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                output,
                file,
                ensure_ascii=False,
            )

    print()
    print("Download complete.")
    print("Features:", len(all_features))
    print("Saved to:", OUTPUT_PATH)


if __name__ == "__main__":
    main()