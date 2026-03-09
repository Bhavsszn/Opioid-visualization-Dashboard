"""Validation utilities for ETL data contracts and user-provided filters."""

from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import HTTPException

REQUIRED_COLUMNS = ["state", "year", "deaths", "population", "crude_rate", "age_adjusted_rate"]


def ensure_contract_columns(df: pd.DataFrame) -> None:
    """Raise if ETL output does not include required columns."""
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise HTTPException(status_code=500, detail=f"Missing required ETL columns: {missing}")


def normalize_state(state: str | None) -> str | None:
    if state is None:
        return None
    cleaned = state.strip()
    if not cleaned:
        raise HTTPException(status_code=422, detail="state cannot be empty")
    if len(cleaned) > 64:
        raise HTTPException(status_code=422, detail="state is too long")
    return cleaned


def serialize_unknown(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
