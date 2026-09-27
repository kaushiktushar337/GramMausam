from app.config import DATA_DIR
from app.data.generate_demo import generate
from app.ml.evaluate import evaluate_models


if __name__ == "__main__":
    data_path = DATA_DIR / "processed" / "demo_training_data.csv"
    if not data_path.exists():
        generate()

    result = evaluate_models()
    for target, metrics in result.items():
        print(
            f"{target}: MAE={metrics['mae']:.4f}, "
            f"RMSE={metrics['rmse']:.4f}, "
            f"BIAS={metrics['bias']:.4f}"
        )
