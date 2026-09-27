from pathlib import Path
import json

import numpy as np
import pandas as pd

from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from sklearn.inspection import permutation_importance
import joblib


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

TRAINING_FILE = BASE_DIR / "data" / "processed" / (
    "gfs_chirps_training_up_2025-07.csv"
)

ELEVATION_FILE = BASE_DIR / "data" / "processed" / (
    "fine_grid_elevation_up_complete.csv"
)

MODEL_DIR = BASE_DIR / "models"

MODEL_FILE = MODEL_DIR / (
    "grammausam_rainfall_downscaler.joblib"
)

METRICS_FILE = MODEL_DIR / (
    "grammausam_rainfall_metrics.json"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# DATE SPLIT
# ============================================================

TRAIN_END = "2025-07-21"
VAL_START = "2025-07-22"
VAL_END = "2025-07-26"
TEST_START = "2025-07-27"
TEST_END = "2025-07-31"


# ============================================================
# LOAD TRAINING DATA
# ============================================================

print("=" * 60)
print("Loading GFS + CHIRPS training data...")
print("=" * 60)

training = pd.read_csv(
    TRAINING_FILE
)

print(
    f"Training rows loaded: {len(training):,}"
)


# ============================================================
# LOAD ELEVATION
# ============================================================

print()
print("=" * 60)
print("Loading elevation data...")
print("=" * 60)

elevation = pd.read_csv(
    ELEVATION_FILE
)

print(
    f"Elevation rows: {len(elevation):,}"
)

required_elevation = {
    "fine_lat",
    "fine_lon",
    "elevation_m",
    "elevation_source",
    "nearest_known_distance_deg",
}

missing = (
    required_elevation
    - set(elevation.columns)
)

if missing:
    raise ValueError(
        f"Missing elevation columns: {missing}"
    )


# ============================================================
# CLEAN TYPES
# ============================================================

training["date"] = pd.to_datetime(
    training["date"]
)

for col in [
    "coarse_lat",
    "coarse_lon",
    "fine_lat",
    "fine_lon",
    "gfs_rainfall",
    "chirps_rainfall",
]:
    training[col] = pd.to_numeric(
        training[col],
        errors="coerce"
    )


elevation["fine_lat"] = pd.to_numeric(
    elevation["fine_lat"],
    errors="coerce"
)

elevation["fine_lon"] = pd.to_numeric(
    elevation["fine_lon"],
    errors="coerce"
)

elevation["elevation_m"] = pd.to_numeric(
    elevation["elevation_m"],
    errors="coerce"
)

elevation["nearest_known_distance_deg"] = pd.to_numeric(
    elevation["nearest_known_distance_deg"],
    errors="coerce"
)


# ============================================================
# MERGE ELEVATION
# ============================================================

print()
print("=" * 60)
print("Merging elevation into training data...")
print("=" * 60)

elevation = elevation[
    [
        "fine_lat",
        "fine_lon",
        "elevation_m",
        "elevation_source",
        "nearest_known_distance_deg",
    ]
].drop_duplicates(
    subset=[
        "fine_lat",
        "fine_lon",
    ]
)


training["fine_lat"] = training[
    "fine_lat"
].round(6)

training["fine_lon"] = training[
    "fine_lon"
].round(6)

elevation["fine_lat"] = elevation[
    "fine_lat"
].round(6)

elevation["fine_lon"] = elevation[
    "fine_lon"
].round(6)


training = training.merge(
    elevation,
    on=[
        "fine_lat",
        "fine_lon",
    ],
    how="left",
    validate="many_to_one",
)


print(
    f"Rows after merge: {len(training):,}"
)

print(
    f"Missing elevation: "
    f"{training['elevation_m'].isna().sum():,}"
)


# ============================================================
# ELEVATION QUALITY FEATURE
# ============================================================

training["elevation_interpolated"] = (
    training["elevation_source"]
    == "local_idw_interpolation"
).astype(np.int8)


training["nearest_known_distance_deg"] = (
    training["nearest_known_distance_deg"]
    .fillna(999.0)
)


# ============================================================
# SPATIAL FEATURES
# ============================================================

# Location of the fine cell inside its coarse GFS cell.

training["fine_offset_lat"] = (
    training["fine_lat"]
    - training["coarse_lat"]
)

training["fine_offset_lon"] = (
    training["fine_lon"]
    - training["coarse_lon"]
)


# ============================================================
# FINAL FEATURE SET
# ============================================================

FEATURES = [
    "gfs_rainfall",
    "fine_lat",
    "fine_lon",
    "fine_offset_lat",
    "fine_offset_lon",
    "elevation_m",
    "elevation_interpolated",
    "nearest_known_distance_deg",
]

TARGET = "chirps_rainfall"


# ============================================================
# CLEAN DATA
# ============================================================

needed_columns = FEATURES + [
    TARGET,
    "date",
]

training = training.dropna(
    subset=needed_columns
).copy()


training = training[
    training["gfs_rainfall"] >= 0
].copy()

training = training[
    training[TARGET] >= 0
].copy()


print()
print(
    f"Rows available for modelling: "
    f"{len(training):,}"
)


# ============================================================
# ELEVATION DIAGNOSTICS
# ============================================================

print()
print("=" * 60)
print("ELEVATION QUALITY")
print("=" * 60)

print(
    f"API-based rows: "
    f"{(
        training['elevation_interpolated'] == 0
    ).sum():,}"
)

print(
    f"Interpolated rows: "
    f"{(
        training['elevation_interpolated'] == 1
    ).sum():,}"
)

print(
    f"Mean nearest-known distance: "
    f"{training['nearest_known_distance_deg'].mean():.4f}°"
)

print(
    f"Maximum nearest-known distance: "
    f"{training['nearest_known_distance_deg'].max():.4f}°"
)


# ============================================================
# CREATE DATE-BASED SPLITS
# ============================================================

train_mask = (
    training["date"]
    <= pd.Timestamp(TRAIN_END)
)

val_mask = (
    (training["date"] >= pd.Timestamp(VAL_START))
    &
    (training["date"] <= pd.Timestamp(VAL_END))
)

test_mask = (
    (training["date"] >= pd.Timestamp(TEST_START))
    &
    (training["date"] <= pd.Timestamp(TEST_END))
)


train_df = training[train_mask].copy()
val_df = training[val_mask].copy()
test_df = training[test_mask].copy()


print()
print("=" * 60)
print("DATE-BASED SPLIT")
print("=" * 60)

print(
    f"Train: "
    f"{train_df['date'].min().date()} → "
    f"{train_df['date'].max().date()} "
    f"({len(train_df):,} rows)"
)

print(
    f"Validation: "
    f"{val_df['date'].min().date()} → "
    f"{val_df['date'].max().date()} "
    f"({len(val_df):,} rows)"
)

print(
    f"Test: "
    f"{test_df['date'].min().date()} → "
    f"{test_df['date'].max().date()} "
    f"({len(test_df):,} rows)"
)


# ============================================================
# PREPARE X / y
# ============================================================

X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_val = val_df[FEATURES]
y_val = val_df[TARGET]

X_test = test_df[FEATURES]
y_test = test_df[TARGET]


# ============================================================
# MODEL
# ============================================================

print()
print("=" * 60)
print("TRAINING DOWNSCALING MODEL")
print("=" * 60)

model = HistGradientBoostingRegressor(
    learning_rate=0.08,
    max_iter=180,
    max_leaf_nodes=31,
    min_samples_leaf=100,
    l2_regularization=1.0,
    loss="squared_error",
    random_state=42,
    early_stopping=False,
)


model.fit(
    X_train,
    y_train
)


print("Model training complete.")


# ============================================================
# EVALUATION FUNCTION
# ============================================================

def evaluate(
    name,
    y_true,
    prediction,
    baseline_prediction,
):
    prediction = np.maximum(
        prediction,
        0
    )

    baseline_prediction = np.maximum(
        baseline_prediction,
        0
    )

    mae = mean_absolute_error(
        y_true,
        prediction
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_true,
            prediction
        )
    )

    r2 = r2_score(
        y_true,
        prediction
    )

    baseline_mae = mean_absolute_error(
        y_true,
        baseline_prediction
    )

    baseline_rmse = np.sqrt(
        mean_squared_error(
            y_true,
            baseline_prediction
        )
    )

    threshold = 1.0

    actual_event = (
        y_true >= threshold
    )

    predicted_event = (
        prediction >= threshold
    )

    hits = (
        actual_event
        &
        predicted_event
    ).sum()

    false_alarms = (
        (~actual_event)
        &
        predicted_event
    ).sum()

    misses = (
        actual_event
        &
        (~predicted_event)
    ).sum()

    precision = (
        hits / (hits + false_alarms)
        if hits + false_alarms > 0
        else 0
    )

    recall = (
        hits / (hits + misses)
        if hits + misses > 0
        else 0
    )

    f1 = (
        2 * precision * recall
        / (precision + recall)
        if precision + recall > 0
        else 0
    )

    print()
    print(f"{name}")
    print("-" * 60)

    print(
        f"Model MAE       : {mae:.4f} mm"
    )

    print(
        f"Model RMSE      : {rmse:.4f} mm"
    )

    print(
        f"Model R²        : {r2:.4f}"
    )

    print(
        f"Baseline MAE    : {baseline_mae:.4f} mm"
    )

    print(
        f"Baseline RMSE   : {baseline_rmse:.4f} mm"
    )

    print(
        f"MAE improvement : "
        f"{baseline_mae - mae:.4f} mm"
    )

    print(
        f"Rain precision  : {precision:.4f}"
    )

    print(
        f"Rain recall     : {recall:.4f}"
    )

    print(
        f"Rain F1         : {f1:.4f}"
    )

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "baseline_mae": float(baseline_mae),
        "baseline_rmse": float(baseline_rmse),
        "mae_improvement": float(
            baseline_mae - mae
        ),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


# ============================================================
# VALIDATION PREDICTIONS
# ============================================================

val_prediction = model.predict(
    X_val
)

val_metrics = evaluate(
    "VALIDATION RESULTS",
    y_val.to_numpy(),
    val_prediction,
    X_val["gfs_rainfall"].to_numpy(),
)


# ============================================================
# TEST PREDICTIONS
# ============================================================

test_prediction = model.predict(
    X_test
)

test_metrics = evaluate(
    "TEST RESULTS",
    y_test.to_numpy(),
    test_prediction,
    X_test["gfs_rainfall"].to_numpy(),
)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

print()
print("=" * 60)
print("FEATURE IMPORTANCE")
print("=" * 60)

# HistGradientBoostingRegressor does not expose
# feature_importances_. Use permutation importance instead.

importance_sample_size = min(
    20000,
    len(val_df)
)

importance_sample = val_df.sample(
    n=importance_sample_size,
    random_state=42
)

permutation = permutation_importance(
    model,
    importance_sample[FEATURES],
    importance_sample[TARGET],
    n_repeats=3,
    random_state=42,
    scoring="neg_mean_absolute_error",
    n_jobs=-1,
)

importance = pd.Series(
    permutation.importances_mean,
    index=FEATURES,
).sort_values(
    ascending=False
)

print(
    importance.to_string()
)


# ============================================================
# SAVE MODEL
# ============================================================

print()
print("=" * 60)
print("SAVING MODEL")
print("=" * 60)

joblib.dump(
    {
        "model": model,
        "features": FEATURES,
        "target": TARGET,
    },
    MODEL_FILE,
    compress=3,
)


# ============================================================
# SAVE METRICS
# ============================================================

metrics = {
    "experiment": {
        "region": "Uttar Pradesh working domain",
        "period": "2025-07-01 to 2025-07-31",
        "reference": "CHIRPS v3 daily rainfall",
        "forecast": "GFS previous_day1 rainfall",
    },
    "split": {
        "train": [
            "2025-07-01",
            "2025-07-21",
        ],
        "validation": [
            "2025-07-22",
            "2025-07-26",
        ],
        "test": [
            "2025-07-27",
            "2025-07-31",
        ],
    },
    "features": FEATURES,
    "validation": val_metrics,
    "test": test_metrics,
}

with open(
    METRICS_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        metrics,
        f,
        indent=2
    )


# ============================================================
# FINAL
# ============================================================

print()
print("=" * 60)
print("DOWNSCALING MODEL COMPLETE")
print("=" * 60)

print(
    f"Model: {MODEL_FILE}"
)

print(
    f"Metrics: {METRICS_FILE}"
)

print()
print("The model is ready for the next")
print("stage: fine-grid prediction.")