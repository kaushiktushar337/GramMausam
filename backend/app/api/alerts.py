from fastapi import APIRouter

from app.models.schemas import AlertItem
from app.services.alert_service import create_alerts

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("", response_model=list[AlertItem])
def alerts():
    return create_alerts()
