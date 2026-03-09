"""Pipeline summary service sourced from PostgreSQL serving tables."""

from __future__ import annotations

import json

from quality import build_quality_report
from repositories.pipeline_repository import PipelineRepository
from services.metrics_service import load_state_year_df

repo = PipelineRepository()


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

    stages = row.get("stages_json")
    assets = row.get("databricks_assets_json")
    return {
        "run_id": row.get("run_id", ""),
        "checked_at": row.get("checked_at", ""),
        "source": row.get("source", "databricks-medallion-pattern"),
        "row_count": int(row.get("row_count", 0)),
        "states": int(row.get("states", 0)),
        "years": {"min": int(row.get("min_year", 0)), "max": int(row.get("max_year", 0))},
        "quality_status": row.get("quality_status", "unknown"),
        "stages": json.loads(stages) if isinstance(stages, str) else (stages or []),
        "databricks_assets": json.loads(assets) if isinstance(assets, str) else (assets or []),
    }


def get_pipeline_run_summary() -> dict:
    serving = _from_serving_table()
    if serving:
        return serving

    df = load_state_year_df()
    if df.empty:
        return build_pipeline_summary(df, "fail", "")

    quality_report = build_quality_report(df)
    return build_pipeline_summary(df, quality_report["status"], quality_report["checked_at"])
