from fastapi import APIRouter, Query

from app.services.weather_service import get_panchayats

router = APIRouter(prefix="/api/panchayats", tags=["Panchayats"])


@router.get("")
def panchayats(
    search: str = Query(default="", max_length=100),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    return {
        "state": "Uttar Pradesh",
        "district": "All",
        "block": "All",
        "panchayats": get_panchayats(search, limit, offset),
    }