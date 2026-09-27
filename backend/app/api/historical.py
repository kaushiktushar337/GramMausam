from fastapi import APIRouter, Query
from app.models.schemas import HistoricalPoint
from app.services.historical_service import get_historical

router = APIRouter(prefix="/api/historical", tags=["Historical"])


@router.get("/{panchayat}", response_model=list[HistoricalPoint])
def historical(
    panchayat: str,
    days: int = Query(30, ge=3, le=365),
):
    return get_historical(panchayat, days)
