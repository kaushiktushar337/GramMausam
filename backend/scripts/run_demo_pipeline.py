from app.data.generate_demo import generate
from app.ml.evaluate import evaluate_models
from app.ml.model_manager import train_models
import pandas as pd


if __name__ == "__main__":
    data_path = generate()
    df = pd.read_csv(data_path, parse_dates=["date"])
    train_models(df)
    metrics = evaluate_models(data_path)

    print("\nDemo pipeline completed.\n")
    for target, values in metrics.items():
        print(
            f"{target}: "
            f"MAE={values['mae']:.4f}, "
            f"RMSE={values['rmse']:.4f}, "
            f"BIAS={values['bias']:.4f}"
        )
