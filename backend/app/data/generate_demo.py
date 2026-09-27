from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from app.config import DATA_DIR
from app.data.demo import PANCHAYAT_PROFILES, make_forecast


OUTPUT = DATA_DIR / "processed" / "demo_training_data.csv"


def generate(days: int = 365) -> Path:
    rng = np.random.default_rng(42)
    rows = []

    for panchayat, profile in PANCHAYAT_PROFILES.items():
        forecast = make_forecast(panchayat, days=7)
        for i in range(days):
            day = pd.Timestamp("2024-04-26") + pd.Timedelta(days=i)
            base = profile["rainfall"] + 6 * np.sin(i / 14)
            coarse_rain = max(0.0, base + rng.normal(0, 5))
            observed_rain = max(
                0.0,
                coarse_rain
                + (profile["elevation"] - 100) * 0.03
                + (profile["ndvi"] - 0.5) * 7
                + (profile["soil_moisture"] - 0.6) * 5
                + rng.normal(0, 2.8),
            )

            coarse_max = profile["max_temp"] + 3 * np.sin(i / 21) + rng.normal(0, 1.2)
            observed_max = coarse_max - (profile["elevation"] - 100) * 0.006 + rng.normal(0, 0.6)
            coarse_min = profile["min_temp"] + 2 * np.sin(i / 21) + rng.normal(0, 0.9)
            observed_min = coarse_min - (profile["elevation"] - 100) * 0.006 + rng.normal(0, 0.5)

            coarse_humidity = np.clip(profile["humidity"] + rng.normal(0, 5), 20, 98)
            observed_humidity = np.clip(
                coarse_humidity
                + (profile["soil_moisture"] - 0.6) * 8
                + (profile["ndvi"] - 0.5) * 4
                + rng.normal(0, 2),
                20,
                100,
            )

            coarse_wind = max(0, profile["wind_speed"] + rng.normal(0, 2.0))
            observed_wind = max(
                0,
                coarse_wind + (profile["elevation"] - 100) * 0.01 + rng.normal(0, 0.8),
            )

            rows.append(
                {
                    "panchayat": panchayat,
                    "date": day,
                    "coarse_rainfall": coarse_rain,
                    "coarse_max_temp": coarse_max,
                    "coarse_min_temp": coarse_min,
                    "coarse_humidity": coarse_humidity,
                    "coarse_wind_speed": coarse_wind,
                    "elevation": profile["elevation"],
                    "ndvi": profile["ndvi"],
                    "soil_moisture": profile["soil_moisture"],
                    "land_cover_code": profile["land_cover_code"],
                    "observed_rainfall": observed_rain,
                    "observed_max_temp": observed_max,
                    "observed_min_temp": observed_min,
                    "observed_humidity": observed_humidity,
                    "observed_wind_speed": observed_wind,
                }
            )

    result = pd.DataFrame(rows)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)
    return OUTPUT


if __name__ == "__main__":
    path = generate()
    print(f"Generated {path}")
