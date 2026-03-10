"""Health router."""

from __future__ import annotations

from fastapi import APIRouter

from db import ping
from schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Basic service health probe including PostgreSQL reachability."""
    return HealthResponse(ok=True, db_exists=ping())
