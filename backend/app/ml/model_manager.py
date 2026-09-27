from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.config import MODEL_DIR
from app.ml.features import FEATURE_COLUMNS, add_time_features

TARGETS = {
    "rainfall": "observed_rainfall",
    "max_temp": "observed_max_temp",
    "min_temp": "observed_min_temp",
    "humidity": "observed_humidity",
    "wind_speed": "observed_wind_speed",
}

MODEL_DIR.mkdir(parents=True, exist_ok=True)


def train_models(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42) -> dict:
    trained = {}
    df = add_time_features(df)

    for target, target_column in TARGETS.items():
        clean = df.dropna(subset=FEATURE_COLUMNS + [target_column]).copy()
        X = clean[FEATURE_COLUMNS]
        y = clean[target_column]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
        )

        model = RandomForestRegressor(
            n_estimators=250,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        )
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        rmse = mean_squared_error(y_test, predictions) ** 0.5
        residual_std = float(np.std(y_test.to_numpy() - predictions))

        artifact = {
            "model": model,
            "features": FEATURE_COLUMNS,
            "target": target,
            "mae": float(mae),
            "rmse": float(rmse),
            "residual_std": residual_std,
            "sample_count": int(len(clean)),
        }

        path = model_path(target)
        joblib.dump(artifact, path)
        trained[target] = artifact

    return trained


def model_path(target: str) -> Path:
    return MODEL_DIR / f"{target}_model.joblib"


def load_model(target: str):
    path = model_path(target)
    if not path.exists():
        return None
    return joblib.load(path)
