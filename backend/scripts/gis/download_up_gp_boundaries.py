from pathlib import Path
import requests
import json
import time


BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = BASE_DIR / "data" / "gis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "up_gp_boundaries_official.geojson"


# Official NIC/BharatMaps Gram Panchayat polygon layer
SERVICE_URL = (
    "https://bharatnetprogress.nic.in/"
    "nicclouddb/rest/services/"
    "BharatMaps/AllIndiaFeatures/"
    "MapServer/6/query"
)

PAGE_SIZE = 500
TIMEOUT = 60


print("=" * 60)
print("OFFICIAL GRAM PANCHAYAT BOUNDARY DOWNLOAD")
print("=" * 60)

print("Source:")
print(SERVICE_URL)
print()
print("Target: Uttar Pradesh")


features = []
offset = 0


while True:

    params = {
        "where": "STNAME='Uttar Pradesh'",
        "outFields": (
            "GP_ID,GP_NAME,STNAME,"
            "DT_CODE,DTNAME,"
            "SDT_CODE,SDT_NAME,"
            "BLK_NAME"
        ),
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
        "resultOffset": offset,
        "resultRecordCount": PAGE_SIZE,
    }

    print(
        f"Requesting records "
        f"{offset + 1} → {offset + PAGE_SIZE}"
    )

    response = requests.get(
        SERVICE_URL,
        params=params,
        timeout=TIMEOUT,
    )

    response.raise_for_status()

    data = response.json()

    page_features = data.get("features", [])

    print(
        f"Returned: {len(page_features)}"
    )

    if not page_features:
        break

    features.extend(page_features)

    exceeded = data.get(
        "exceededTransferLimit",
        False
    )

    if not exceeded and len(page_features) < PAGE_SIZE:
        break

    offset += len(page_features)

    time.sleep(1)


geojson = {
    "type": "FeatureCollection",
    "features": features,
}


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        geojson,
        f,
        ensure_ascii=False
    )


print()
print("=" * 60)
print("DOWNLOAD COMPLETE")
print("=" * 60)

print(
    f"Total polygons: {len(features):,}"
)

print(
    f"Output: {OUTPUT_FILE}"
)

print()
print(
    "Source: Government of India "
    "NIC/BharatMaps"
)

print(
    "Note: Panchayat boundaries are "
    "administrative reference data and "
    "should not be presented as legally "
    "authoritative cadastral boundaries."
)