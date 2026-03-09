"""Quality router."""

from fastapi import APIRouter

from schemas import QualityStatusResponse
from services.quality_service import get_quality_status

router = APIRouter(prefix="/api/quality", tags=["quality"])


@router.get("/status", response_model=QualityStatusResponse)
def quality_status():
    """Return quality report payload."""
    return get_quality_status()
