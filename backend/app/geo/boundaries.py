from __future__ import annotations

from pathlib import Path

import geopandas as gpd


def load_boundaries(path: str | Path, layer: str | None = None) -> gpd.GeoDataFrame:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Boundary file not found: {source}")

    gdf = gpd.read_file(source, layer=layer)
    if gdf.empty:
        raise ValueError("Boundary file contains no features")

    if gdf.crs is None:
        raise ValueError("Boundary dataset must define a CRS")

    return gdf


def standardize_to_wgs84(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    return gdf.to_crs("EPSG:4326")
