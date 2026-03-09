"""Health router."""

import os

from fastapi import APIRouter

from schemas import HealthResponse
from settings import settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health():
    """Simple health check with database-file existence flag."""
    return {"ok": True, "db_exists": os.path.exists(settings.db_path)}
