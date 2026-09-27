from __future__ import annotations

import geopandas as gpd
import pandas as pd


def aggregate_grid_to_panchayat(
    grid_predictions: gpd.GeoDataFrame,
    panchayats: gpd.GeoDataFrame,
    prediction_column: str,
    panchayat_column: str = "panchayat",
) -> pd.DataFrame:
    joined = gpd.sjoin(
        grid_predictions,
        panchayats[[panchayat_column, "geometry"]],
        how="inner",
        predicate="intersects",
    )

    return (
        joined.groupby(panchayat_column)[prediction_column]
        .mean()
        .reset_index(name=prediction_column)
    )
