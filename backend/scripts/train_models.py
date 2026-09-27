from pathlib import Path

import pandas as pd

from app.config import DATA_DIR
from app.data.generate_demo import generate
from app.ml.model_manager import train_models


if __name__ == "__main__":
    data_path = DATA_DIR / "processed" / "demo_training_data.csv"
    if not data_path.exists():
        data_path = generate()

    df = pd.read_csv(data_path, parse_dates=["date"])
    artifacts = train_models(df)

    for target, artifact in artifacts.items():
        print(
            f"{target}: MAE={artifact['mae']:.4f}, "
            f"RMSE={artifact['rmse']:.4f}, "
            f"samples={artifact['sample_count']}"
        )
