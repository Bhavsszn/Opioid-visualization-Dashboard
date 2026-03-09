"""Data quality service with artifact fallback."""

from __future__ import annotations

from fastapi import HTTPException

from quality import build_quality_report
from services.metrics_service import load_state_year_df
from utils.artifact_loader import load_artifact


def get_quality_status() -> dict:
    """Return quality report from artifact, otherwise compute against live DB data."""
    artifact = load_artifact("quality_report.json")
    if artifact:
        return artifact

    df = load_state_year_df()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    return build_quality_report(df)
