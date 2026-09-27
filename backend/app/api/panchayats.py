from fastapi import APIRouter, HTTPException, Query

from app.services.panchayat_boundary_service import (
    get_nearby_panchayat_boundaries,
    get_panchayat_boundary,
)
from app.services.weather_service import get_panchayats, get_weather

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


@router.get("/{panchayat}/boundary")
def panchayat_boundary(panchayat: str):
    boundary = get_panchayat_boundary(panchayat)
    if boundary is None:
        raise HTTPException(
            status_code=404,
            detail=f"Boundary for Panchayat '{panchayat}' not found.",
        )
    return boundary


@router.get("/{panchayat}/nearby")
def nearby_panchayats(
    panchayat: str,
    limit: int = Query(default=8, ge=1, le=12),
):
    nearby = get_nearby_panchayat_boundaries(panchayat, limit)
    if nearby is None:
        raise HTTPException(
            status_code=404,
            detail=f"Boundary for Panchayat '{panchayat}' not found.",
        )

    features = []
    for feature in nearby["features"]:
        name = feature["properties"].get("gpname", "")
        try:
            weather = get_weather(name)
        except HTTPException:
            continue

        feature["properties"]["weather"] = {
            "date": weather["date"].isoformat(),
            "rainfall": weather["rainfall"],
            "minTemp": weather["min_temp"],
            "maxTemp": weather["max_temp"],
            "humidity": weather["humidity"],
            "windSpeed": weather["wind_speed"],
            "windDirection": weather["wind_direction"],
            "condition": weather["condition"],
            "risk": weather["risk"],
        }
        features.append(feature)

    nearby["features"] = features
    return nearby