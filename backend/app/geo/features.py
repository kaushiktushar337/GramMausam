from __future__ import annotations

import geopandas as gpd
import numpy as np


def add_centroid_features(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    result = gdf.copy()
    centroids = result.geometry.centroid
    result["centroid_x"] = centroids.x
    result["centroid_y"] = centroids.y
    return result


def add_simple_elevation_gradient(gdf: gpd.GeoDataFrame, base: float = 100.0) -> gpd.GeoDataFrame:
    result = gdf.copy()
    centroid_y = result.geometry.centroid.y.to_numpy()
    if len(centroid_y) == 0:
        result["elevation"] = base
        return result

    norm = (centroid_y - centroid_y.min()) / max(centroid_y.max() - centroid_y.min(), 1e-9)
    result["elevation"] = base + norm * 20.0
    return result


def add_demo_environmental_features(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    result = add_centroid_features(gdf)
    result = add_simple_elevation_gradient(result)
    result["ndvi"] = np.clip(0.45 + (result["centroid_x"] - result["centroid_x"].mean()) * 5, 0.1, 0.85)
    result["soil_moisture"] = np.clip(0.6 + (result["centroid_y"] - result["centroid_y"].mean()) * 4, 0.2, 0.9)
    result["land_cover_code"] = 12
    return result
