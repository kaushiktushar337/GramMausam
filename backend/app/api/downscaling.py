from fastapi import APIRouter, HTTPException

from app.models.schemas import DownscalingInput, DownscalingResponse
from app.ml.predict import predict
from app.services.downscaling_service import downscale_panchayat

router = APIRouter(prefix="/api/downscaling", tags=["Downscaling"])


@router.post("/predict", response_model=DownscalingResponse)
def downscaling_predict(payload: DownscalingInput):
    return predict(
        "rainfall",
        payload.model_dump(),
    )


@router.get("/{panchayat}/{target}", response_model=DownscalingResponse)
def panchayat_downscaling(panchayat: str, target: str):
    allowed = {"rainfall", "max_temp", "min_temp", "humidity", "wind_speed"}
    if target not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported target: {target}")
    return downscale_panchayat(panchayat, target)
