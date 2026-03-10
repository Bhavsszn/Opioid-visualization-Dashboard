"""Metric retrieval and aggregation services."""

from __future__ import annotations

import logging

import pandas as pd
from fastapi import HTTPException

from repositories.metrics_repository import MetricsRepository
from settings import settings
from utils.validation import ensure_contract_columns, normalize_state


repo = MetricsRepository()
logger = logging.getLogger("opioid.metrics_service")


def load_state_year_df() -> pd.DataFrame:
    """Load canonical state-year dataset into a validated dataframe."""
    rows = repo.fetch_state_year_data()
    if not rows:
        return pd.DataFrame(columns=["year", "state", "deaths", "population", "crude_rate", "age_adjusted_rate"])
    frame = pd.DataFrame(rows)
    ensure_contract_columns(frame)
    return frame


def get_state_year(state: str | None = None, year: int | None = None) -> dict:
    """Return state/year rows for optional filters."""
    try:
        rows = repo.fetch_state_year_data(state=normalize_state(state), year=year)
    except Exception as exc:
        table_name = (
            f"{settings.postgres_schema}.state_year_overdoses" if settings.db_backend == "postgres" else "state_year_overdoses"
        )
        logger.exception("get_state_year failed for table=%s", table_name)
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable or serving table not loaded ({table_name}).",
        ) from exc
    return {"rows": rows}


def get_states_latest(year: int | None = None) -> dict:
    """Return latest-state snapshot for selected year or max available year."""
    try:
        selected_year, rows = repo.fetch_latest_state_metrics(year=year)
    except Exception as exc:
        table_name = f"{settings.postgres_schema}.states_latest" if settings.db_backend == "postgres" else "states_latest"
        logger.exception("get_states_latest failed for table=%s", table_name)
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable or serving table not loaded ({table_name}).",
        ) from exc
    return {"year": selected_year, "rows": rows}
