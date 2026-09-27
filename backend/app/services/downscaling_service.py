from app.data.demo import get_profile
from app.ml.predict import predict


def build_features_for_panchayat(panchayat: str) -> dict:
    profile = get_profile(panchayat)
    return {
        "coarse_rainfall": profile["rainfall"],
        "coarse_max_temp": profile["max_temp"],
        "coarse_min_temp": profile["min_temp"],
        "coarse_humidity": profile["humidity"],
        "coarse_wind_speed": profile["wind_speed"],
        "elevation": profile["elevation"],
        "ndvi": profile["ndvi"],
        "soil_moisture": profile["soil_moisture"],
        "land_cover_code": profile["land_cover_code"],
        "day_of_year": 114,
    }


def downscale_panchayat(panchayat: str, target: str) -> dict:
    features = build_features_for_panchayat(panchayat)
    return predict(target, features)
