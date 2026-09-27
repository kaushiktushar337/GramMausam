from __future__ import annotations

from datetime import date, timedelta

PANCHAYAT_PROFILES = {
    "Bara": {
        "rainfall": 18.0,
        "max_temp": 32.0,
        "min_temp": 24.0,
        "humidity": 78.0,
        "wind_speed": 12.0,
        "wind_direction": "SW",
        "condition": "Light Rain",
        "confidence": "Medium",
        "confidence_value": 62.0,
        "risk": "Medium",
        "risk_text": "Moderate risk of waterlogging in low-lying areas.",
        "crop": "Wheat",
        "crop_stage": "Vegetative Stage",
        "elevation": 98.0,
        "ndvi": 0.47,
        "soil_moisture": 0.62,
        "land_cover_code": 12,
    },
    "Kareli": {
        "rainfall": 26.0,
        "max_temp": 33.0,
        "min_temp": 25.0,
        "humidity": 82.0,
        "wind_speed": 14.0,
        "wind_direction": "SW",
        "condition": "Rain",
        "confidence": "High",
        "confidence_value": 82.0,
        "risk": "High",
        "risk_text": "High rainfall probability may affect field operations.",
        "crop": "Wheat",
        "crop_stage": "Vegetative Stage",
        "elevation": 104.0,
        "ndvi": 0.52,
        "soil_moisture": 0.68,
        "land_cover_code": 12,
    },
    "Soraon": {
        "rainfall": 32.0,
        "max_temp": 34.0,
        "min_temp": 26.0,
        "humidity": 85.0,
        "wind_speed": 16.0,
        "wind_direction": "SW",
        "condition": "Heavy Rain",
        "confidence": "Medium",
        "confidence_value": 58.0,
        "risk": "High",
        "risk_text": "Heavy rainfall may create localized waterlogging.",
        "crop": "Rice",
        "crop_stage": "Vegetative Stage",
        "elevation": 92.0,
        "ndvi": 0.58,
        "soil_moisture": 0.74,
        "land_cover_code": 12,
    },
    "Phaphamau": {
        "rainfall": 21.0,
        "max_temp": 32.0,
        "min_temp": 24.0,
        "humidity": 80.0,
        "wind_speed": 12.0,
        "wind_direction": "W",
        "condition": "Light Rain",
        "confidence": "High",
        "confidence_value": 76.0,
        "risk": "Medium",
        "risk_text": "Rain may interrupt irrigation and field operations.",
        "crop": "Wheat",
        "crop_stage": "Vegetative Stage",
        "elevation": 101.0,
        "ndvi": 0.49,
        "soil_moisture": 0.64,
        "land_cover_code": 12,
    },
    "Jasra": {
        "rainfall": 16.0,
        "max_temp": 31.0,
        "min_temp": 23.0,
        "humidity": 76.0,
        "wind_speed": 10.0,
        "wind_direction": "W",
        "condition": "Cloudy",
        "confidence": "High",
        "confidence_value": 84.0,
        "risk": "Low",
        "risk_text": "No significant weather-related risk expected.",
        "crop": "Wheat",
        "crop_stage": "Vegetative Stage",
        "elevation": 95.0,
        "ndvi": 0.45,
        "soil_moisture": 0.57,
        "land_cover_code": 12,
    },
}


def list_panchayats() -> list[str]:
    return list(PANCHAYAT_PROFILES)


def get_profile(panchayat: str) -> dict:
    return PANCHAYAT_PROFILES.get(panchayat, PANCHAYAT_PROFILES["Bara"])


def _condition(rainfall: float) -> str:
    if rainfall >= 25:
        return "Heavy Rain"
    if rainfall >= 15:
        return "Light Rain"
    if rainfall >= 8:
        return "Cloudy"
    return "Sunny"


def make_forecast(panchayat: str, days: int = 7, start: date | None = None) -> list[dict]:
    profile = get_profile(panchayat)
    start_date = start or date.today()
    rainfall_decay = [1.0, 0.67, 0.28, 0.50, 0.39, 0.33, 0.22]
    probability = [72, 58, 36, 42, 31, 25, 18]

    result = []
    for i in range(min(days, 7)):
        current = start_date + timedelta(days=i)
        rainfall = round(profile["rainfall"] * rainfall_decay[i], 1)
        max_temp = round(profile["max_temp"] + [0, 2, 3, 1, 0, 2, 3][i], 1)
        min_temp = round(profile["min_temp"] + [0, 1, 2, 0, -1, 0, 1][i], 1)
        humidity = round(max(45, profile["humidity"] - [0, 4, 9, 6, 8, 11, 14][i]), 1)
        wind_speed = round(max(4, profile["wind_speed"] - [0, 1, 2, 1, 3, 2, 1][i]), 1)
        day_name = "Today" if i == 0 else "Tomorrow" if i == 1 else f"Day {i + 1}"
        result.append(
            {
                "date": current,
                "day": day_name,
                "rainfall": rainfall,
                "rain_probability": probability[i],
                "max_temp": max_temp,
                "min_temp": min_temp,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "condition": _condition(rainfall),
            }
        )
    return result


def make_historical(panchayat: str, days: int = 30) -> list[dict]:
    profile = get_profile(panchayat)
    end = date(2025, 4, 24)
    result = []

    for i in range(days):
        current = end - timedelta(days=days - 1 - i)
        phase = (i % 7) - 3
        observed = max(0.0, profile["rainfall"] + phase * 2 + ((i * 3) % 5 - 2))
        block = max(0.0, profile["rainfall"] + phase * 2.4 + ((i * 2) % 7 - 3))
        downscaled = max(0.0, profile["rainfall"] + phase * 1.7 + ((i * 5) % 5 - 2))
        result.append(
            {
                "date": current,
                "observation": round(observed, 2),
                "block_forecast": round(block, 2),
                "downscaled": round(downscaled, 2),
            }
        )
    return result
