"""Pydantic schemas used by routers for response documentation."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    ok: bool
    db_exists: bool


class QualityStatusResponse(BaseModel):
    status: str
    checked_at: str
    checks: list[dict]
    summary: dict
