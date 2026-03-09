"""Metrics router."""

from __future__ import annotations

from fastapi import APIRouter, Query

from schemas import StateYearResponse, StatesLatestResponse
from services.metrics_service import get_state_year, get_states_latest

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/state-year", response_model=StateYearResponse)
def state_year(
    state: str | None = Query(default=None, min_length=1, max_length=64),
    year: int | None = Query(default=None, ge=1900, le=2100),
) -> StateYearResponse:
    """Return state-year rows with optional filters."""
    return StateYearResponse(**get_state_year(state=state, year=year))


@router.get("/states-latest", response_model=StatesLatestResponse)
def states_latest(year: int | None = Query(default=None, ge=1900, le=2100)) -> StatesLatestResponse:
    """Return latest state metrics for selected year or max available year."""
    return StatesLatestResponse(**get_states_latest(year=year))
