"""Metrics router (state-year and latest-state snapshots)."""

from fastapi import APIRouter

from services.metrics_service import get_state_year, get_states_latest

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/state-year")
def state_year(state: str | None = None, year: int | None = None):
    """Return state-year rows with optional state and year filters."""
    return get_state_year(state=state, year=year)


@router.get("/states-latest")
def states_latest(year: int | None = None):
    """Return latest-year rows for all states, sorted by crude rate."""
    return get_states_latest(year=year)
