from fastapi import APIRouter, Query

from app.models.schemas import ForecastDay
from app.services.weather_service import get_forecast

router = APIRouter(prefix="/api/forecast", tags=["Forecast"])


@router.get("/{panchayat}", response_model=list[ForecastDay])
def forecast(panchayat: str, days: int = Query(7, ge=1, le=7)):
    return get_forecast(panchayat, days)
