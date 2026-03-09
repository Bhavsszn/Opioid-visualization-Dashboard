"""Quality router."""

from __future__ import annotations

from fastapi import APIRouter

from schemas import QualityReport
from services.quality_service import get_quality_status

router = APIRouter(tags=["quality"])


@router.get("/api/quality", response_model=QualityReport)
@router.get("/api/quality/status", response_model=QualityReport)
def quality_status() -> QualityReport:
    """Return quality contract results."""
    return QualityReport(**get_quality_status())
