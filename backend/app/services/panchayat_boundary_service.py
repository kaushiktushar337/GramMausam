from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import geopandas as gpd

BOUNDARY_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "gis"
    / "model_domain_panchayats_clean.gpkg"
)


@lru_cache(maxsize=1)
def _load_boundaries() -> tuple[gpd.GeoDataFrame, gpd.GeoSeries]:
    boundaries = gpd.read_file(BOUNDARY_FILE)
    if boundaries.empty:
        raise ValueError("Boundary dataset contains no features")
    if boundaries.crs is None:
        raise ValueError("Boundary dataset must define a CRS")

    if boundaries.crs.to_epsg() != 4326:
        boundaries = boundaries.to_crs("EPSG:4326")

    projected = boundaries.to_crs("EPSG:32643")
    return boundaries, projected.geometry.centroid


def get_panchayat_boundary(panchayat: str) -> dict | None:
    escaped_name = panchayat.strip().replace("'", "''")
    boundaries = gpd.read_file(
        BOUNDARY_FILE,
        where=f"LOWER(gpname) = LOWER('{escaped_name}')",
    )

    if boundaries.empty:
        return None

    if boundaries.crs is None:
        raise ValueError("Boundary dataset must define a CRS")

    if boundaries.crs.to_epsg() != 4326:
        boundaries = boundaries.to_crs("EPSG:4326")

    return json.loads(boundaries.to_json())


def get_nearby_panchayat_boundaries(
    panchayat: str,
    limit: int = 8,
) -> dict | None:
    boundaries, centroids = _load_boundaries()
    names = boundaries["gpname"].astype(str).str.strip().str.casefold()
    matches = boundaries.index[names == panchayat.strip().casefold()]

    if len(matches) == 0:
        return None

    selected_index = matches[0]
    distances = centroids.distance(centroids.loc[selected_index])
    nearby_indexes = distances.nsmallest(limit).index
    nearby = boundaries.loc[nearby_indexes].copy()
    nearby["distance_km"] = (distances.loc[nearby_indexes] / 1000).round(2)

    return json.loads(nearby.to_json())