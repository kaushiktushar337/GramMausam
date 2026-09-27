from __future__ import annotations

import pandas as pd

from app.ml.baseline import (
    humidity_baseline,
    rainfall_baseline,
    temperature_baseline,
    wind_baseline,
)
from app.ml.model_manager import load_model

UNITS = {
    "rainfall": "mm",
    "max_temp": "°C",
    "min_temp": "°C",
    "humidity": "%",
    "wind_speed": "km/h",
}

COARSE_KEYS = {
    "rainfall": "coarse_rainfall",
    "max_temp": "coarse_max_temp",
    "min_temp": "coarse_min_temp",
    "humidity": "coarse_humidity",
    "wind_speed": "coarse_wind_speed",
}


def predict(target: str, features: dict) -> dict:
    artifact = load_model(target)

    if artifact is not None:
        X = pd.DataFrame([{name: features[name] for name in artifact["features"]}])
        value = float(artifact["model"].predict(X)[0])
        coarse = float(features[COARSE_KEYS[target]])
        residual_std = float(artifact.get("residual_std", 0.0))
        confidence = confidence_from_error(value, coarse, residual_std)
        source = "trained_random_forest"
    else:
        value = baseline_prediction(target, features)
        coarse = float(features[COARSE_KEYS[target]])
        confidence = "Medium"
        source = "baseline_demo"

    if target in {"rainfall", "humidity"}:
        value = max(0.0, value)
    if target == "humidity":
        value = min(100.0, value)

    return {
        "target": target,
        "coarse_value": round(coarse, 2),
        "downscaled_value": round(value, 2),
        "unit": UNITS[target],
        "confidence": confidence,
        "model_source": source,
    }


def baseline_prediction(target: str, features: dict) -> float:
    if target == "rainfall":
        return rainfall_baseline(
            features["coarse_rainfall"],
            features["elevation"],
            features["ndvi"],
            features["soil_moisture"],
        )
    if target == "max_temp":
        return temperature_baseline(
            features["coarse_max_temp"],
            features["elevation"],
        )
    if target == "min_temp":
        return temperature_baseline(
            features["coarse_min_temp"],
            features["elevation"],
        )
    if target == "humidity":
        return humidity_baseline(
            features["coarse_humidity"],
            features["soil_moisture"],
            features["ndvi"],
        )
    if target == "wind_speed":
        return wind_baseline(
            features["coarse_wind_speed"],
            features["elevation"],
        )
    raise ValueError(f"Unsupported target: {target}")


def confidence_from_error(prediction: float, coarse: float, residual_std: float) -> str:
    scale = max(abs(prediction), abs(coarse), 1.0)
    relative_error = residual_std / scale
    if relative_error <= 0.08:
        return "High"
    if relative_error <= 0.16:
        return "Medium"
    return "Low"
