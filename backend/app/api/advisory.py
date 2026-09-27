from fastapi import APIRouter

from app.models.schemas import AdvisoryRequest, AdvisoryResponse
from app.services.advisory_service import create_advisory

router = APIRouter(prefix="/api/advisory", tags=["Advisory"])


@router.post("", response_model=AdvisoryResponse)
def advisory(payload: AdvisoryRequest):
    return create_advisory(**payload.model_dump())
