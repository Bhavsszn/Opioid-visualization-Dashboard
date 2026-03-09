"""Health router."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter

from db import ping
from schemas import HealthResponse
from settings import settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Basic service health probe including DB reachability."""
    if settings.db_backend == "sqlite":
        db_exists = Path(settings.db_path).exists()
    else:
        db_exists = ping()
    return HealthResponse(ok=True, db_exists=db_exists)
