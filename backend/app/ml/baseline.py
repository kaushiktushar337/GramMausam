from __future__ import annotations


def rainfall_baseline(coarse_rainfall: float, elevation: float, ndvi: float, soil_moisture: float) -> float:
    adjustment = (
        (elevation - 100.0) * 0.01
        + (ndvi - 0.5) * 4.0
        + (soil_moisture - 0.6) * 3.0
    )
    return max(0.0, coarse_rainfall + adjustment)


def temperature_baseline(coarse_temp: float, elevation: float) -> float:
    adjustment = -(elevation - 100.0) * 0.006
    return coarse_temp + adjustment


def humidity_baseline(coarse_humidity: float, soil_moisture: float, ndvi: float) -> float:
    adjustment = (soil_moisture - 0.6) * 8.0 + (ndvi - 0.5) * 5.0
    return min(100.0, max(0.0, coarse_humidity + adjustment))


def wind_baseline(coarse_wind: float, elevation: float) -> float:
    return max(0.0, coarse_wind + (elevation - 100.0) * 0.01)
