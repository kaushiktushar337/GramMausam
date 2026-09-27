from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.config import DATA_DIR, MODEL_DIR
from app.ml.features import FEATURE_COLUMNS, add_time_features
from app.ml.model_manager import TARGETS, load_model


def evaluate_models(csv_path: Path | None = None) -> dict:
    source = csv_path or (DATA_DIR / "processed" / "demo_training_data.csv")
    df = pd.read_csv(source, parse_dates=["date"])
    df = add_time_features(df)

    metrics = {}
    for target, target_column in TARGETS.items():
        artifact = load_model(target)
        if artifact is None:
            continue

        clean = df.dropna(subset=FEATURE_COLUMNS + [target_column]).copy()
        prediction = artifact["model"].predict(clean[FEATURE_COLUMNS])
        observed = clean[target_column].to_numpy()
        metrics[target] = {
            "mae": float(mean_absolute_error(observed, prediction)),
            "rmse": float(mean_squared_error(observed, prediction) ** 0.5),
            "bias": float(np.mean(prediction - observed)),
            "sample_count": int(len(clean)),
        }

    output = MODEL_DIR / "evaluation_metrics.json"
    output.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics
