"""Data quality service with Postgres-first behavior and optional static fallback."""

from __future__ import annotations

import json

from fastapi import HTTPException

from quality import build_quality_report
from repositories.quality_repository import QualityRepository
from services.metrics_service import load_state_year_df
from utils.artifact_loader import load_artifact

repo = QualityRepository()


def _from_serving_table() -> dict | None:
    try:
        rows = repo.fetch_quality_rows()
    except Exception:
        return None

    if not rows:
        return None

    checked_at = rows[0].get("checked_at")
    checks = []
    for row in rows:
        value = row.get("value_json")
        threshold = row.get("threshold_json")
        checks.append(
            {
                "name": row.get("check_name", "unknown_check"),
                "status": row.get("status", "fail"),
                "value": json.loads(value) if isinstance(value, str) else value,
                "threshold": json.loads(threshold) if isinstance(threshold, str) else threshold,
                "detail": row.get("detail", ""),
            }
        )

    pass_count = sum(1 for check in checks if check["status"] == "pass")
    fail_count = sum(1 for check in checks if check["status"] == "fail")
    total = len(checks)

    return {
        "status": "pass" if fail_count == 0 else "fail",
        "checked_at": checked_at,
        "checks": checks,
        "summary": {
            "rows": 0,
            "columns": ["state", "year", "deaths", "population", "crude_rate", "age_adjusted_rate"],
            "latest_year": None,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": round(pass_count / total, 4) if total else 0.0,
        },
    }


def get_quality_status() -> dict:
    serving = _from_serving_table()
    if serving:
        return serving

    artifact = load_artifact("quality_report.json")
    if artifact:
        return artifact

    df = load_state_year_df()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    return build_quality_report(df)
