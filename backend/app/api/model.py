import json

from fastapi import APIRouter

from app.config import MODEL_DIR
from app.ml.model_manager import TARGETS, load_model

router = APIRouter(prefix="/api/model", tags=["Model"])


@router.get("/status")
def model_status():
    models = {}
    for target in TARGETS:
        artifact = load_model(target)
        models[target] = {
            "trained": artifact is not None,
            "mae": None if artifact is None else artifact.get("mae"),
            "rmse": None if artifact is None else artifact.get("rmse"),
            "sample_count": None if artifact is None else artifact.get("sample_count"),
        }

    metrics_path = MODEL_DIR / "evaluation_metrics.json"
    evaluation = None
    if metrics_path.exists():
        evaluation = json.loads(metrics_path.read_text(encoding="utf-8"))

    return {
        "models": models,
        "evaluation": evaluation,
    }
