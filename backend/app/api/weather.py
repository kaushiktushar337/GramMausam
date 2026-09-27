from fastapi import APIRouter, HTTPException

from app.models.schemas import WeatherResponse
from app.services.weather_service import get_weather

router = APIRouter(prefix="/api/weather", tags=["Weather"])


@router.get("/{panchayat}", response_model=WeatherResponse)
def weather(panchayat: str):
    normalized = panchayat.strip()
    if not normalized:
        raise HTTPException(status_code=400, detail="Panchayat is required")
    return get_weather(normalized)
