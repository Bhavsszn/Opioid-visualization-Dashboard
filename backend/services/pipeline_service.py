"""Pipeline summary service sourced from PostgreSQL serving tables."""

from __future__ import annotations

import json
import logging
from datetime import datetime

from quality import build_quality_report
from repositories.pipeline_repository import PipelineRepository
from services.metrics_service import load_state_year_df

repo = PipelineRepository()
logger = logging.getLogger("opioid.pipeline_service")


def build_pipeline_summary(df, quality_status: str, checked_at: str) -> dict:
    return {
        "run_id": checked_at.replace(":", "").replace("-", "") if checked_at else "",
        "checked_at": checked_at,
        "source": "databricks-medallion-pattern",
        "row_count": int(len(df)),
        "states": int(df["state"].nunique()) if not df.empty else 0,
        "years": {
            "min": int(df["year"].min()) if not df.empty else 0,
            "max": int(df["year"].max()) if not df.empty else 0,
        },
        "quality_status": quality_status,
        "stages": [
            {
                "name": "Bronze",
                "purpose": "Ingest raw opioid source records with minimal transformation.",
                "output": "bronze.overdose_raw",
                "script": "pipeline/databricks/01_bronze_ingest.py",
            },
            {
                "name": "Silver",
                "purpose": "Clean and standardize types, field names, and quality checks.",
                "output": "silver.overdose_clean",
                "script": "pipeline/databricks/02_silver_clean.py",
            },
            {
                "name": "Gold",
                "purpose": "Produce serving-ready analytics tables for API and BI.",
                "output": "gold.state_year_overdoses / gold.states_latest",
                "script": "pipeline/databricks/03_gold_aggregates.py",
            },
            {
                "name": "Publish",
                "purpose": "Upsert Gold outputs into PostgreSQL analytics schema.",
                "output": "analytics.* tables",
                "script": "scripts/sync_databricks_to_postgres.py",
            },
        ],
        "databricks_assets": [
            "pipeline/databricks/01_bronze_ingest.py",
            "pipeline/databricks/02_silver_clean.py",
            "pipeline/databricks/03_gold_aggregates.py",
            "pipeline/databricks/05_gold_quality_and_forecast.sql",
            "pipeline/postgres/analytics_schema.sql",
            "scripts/sync_databricks_to_postgres.py",
        ],
    }


def _from_serving_table() -> dict | None:
    row = repo.fetch_latest_summary()
    if not row:
        return None

    def _to_int(value, default: int = 0) -> int:
        try:
            return int(value) if value is not None else default
        except (TypeError, ValueError):
            return default

    def _to_checked_at(value: object) -> str:
        if value is None:
            return ""
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)

    def _to_list(value: object) -> list:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return parsed if isinstance(parsed, list) else []
            except json.JSONDecodeError:
                return []
        return []

    def _normalize_stages(value: object) -> list[dict]:
        rows = _to_list(value)
        normalized: list[dict] = []
        for index, item in enumerate(rows):
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "name": str(item.get("name") or item.get("stage") or f"Stage {index + 1}"),
                    "purpose": str(item.get("purpose") or ""),
                    "output": str(item.get("output") or ""),
                    "script": str(item.get("script") or ""),
                }
            )
        return normalized

    stages = _normalize_stages(row.get("stages_json"))
    assets_raw = _to_list(row.get("databricks_assets_json"))
    assets = [str(item) for item in assets_raw if item is not None]

    summary = {
        "run_id": str(row.get("run_id") or ""),
        "checked_at": _to_checked_at(row.get("checked_at")),
        "source": str(row.get("source") or "databricks-medallion-pattern"),
        "row_count": _to_int(row.get("row_count"), 0),
        "states": _to_int(row.get("states"), 0),
        "years": {"min": _to_int(row.get("min_year"), 0), "max": _to_int(row.get("max_year"), 0)},
        "quality_status": str(row.get("quality_status") or "unknown"),
        "stages": stages,
        "databricks_assets": assets,
    }
    logger.info(
        "pipeline_serving_row_loaded run_id=%s checked_at=%s stages=%s assets=%s",
        summary["run_id"],
        summary["checked_at"],
        len(summary["stages"]),
        len(summary["databricks_assets"]),
    )
    return summary


def get_pipeline_run_summary() -> dict:
    try:
        serving = _from_serving_table()
    except Exception:
        logger.exception("pipeline_serving_row_parse_failed")
        serving = None
    if serving:
        return serving

    logger.warning("pipeline_serving_row_missing_or_invalid fallback=derived_summary")
    df = load_state_year_df()
    if df.empty:
        return build_pipeline_summary(df, "fail", "")

    quality_report = build_quality_report(df)
    return build_pipeline_summary(df, quality_report["status"], quality_report["checked_at"])
