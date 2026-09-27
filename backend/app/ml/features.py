from __future__ import annotations

FEATURE_COLUMNS = [
    "coarse_rainfall",
    "coarse_max_temp",
    "coarse_min_temp",
    "coarse_humidity",
    "coarse_wind_speed",
    "elevation",
    "ndvi",
    "soil_moisture",
    "land_cover_code",
    "day_of_year",
]


def add_time_features(df):
    result = df.copy()
    result["day_of_year"] = result["date"].dt.dayofyear
    return result


def make_feature_frame(df):
    missing = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")
    return df[FEATURE_COLUMNS]
