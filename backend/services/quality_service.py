"""Quality-report services and static artifact fallback loading."""

import json

from fastapi import HTTPException

from quality import build_quality_report
from services.metrics_service import load_state_year_df
from settings import settings


def get_quality_status() -> dict:
    """Return quality status from static artifact when present, else compute from DB."""
    report_path = settings.static_api_dir / "quality_report.json"
    if report_path.exists():
        return json.loads(report_path.read_text(encoding="utf-8"))

    df = load_state_year_df()
    if df.empty:
        raise HTTPException(404, "No data")
    return build_quality_report(df)
