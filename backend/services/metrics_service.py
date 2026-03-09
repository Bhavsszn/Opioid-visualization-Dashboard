"""Metric retrieval and aggregation services."""

from __future__ import annotations

import pandas as pd
from fastapi import HTTPException

from repositories.metrics_repository import MetricsRepository
from utils.validation import ensure_contract_columns, normalize_state


repo = MetricsRepository()


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
        raise HTTPException(
            status_code=503,
            detail="PostgreSQL unavailable or serving tables not loaded (analytics.state_year_overdoses).",
        ) from exc
    return {"rows": rows}


def get_states_latest(year: int | None = None) -> dict:
    """Return latest-state snapshot for selected year or max available year."""
    try:
        selected_year, rows = repo.fetch_latest_state_metrics(year=year)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="PostgreSQL unavailable or serving tables not loaded (analytics.states_latest).",
        ) from exc
    return {"year": selected_year, "rows": rows}
