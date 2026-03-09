"""Pipeline summary services for Databricks showcase evidence."""

import json

from fastapi import HTTPException

from quality import build_quality_report
from services.metrics_service import load_state_year_df
from settings import settings


def build_pipeline_summary(df, quality_status: str, checked_at: str) -> dict:
    """Build the pipeline run summary payload used by the frontend pipeline page."""
    return {
        "run_id": checked_at.replace(":", "").replace("-", ""),
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
                "output": "opioid.bronze_raw",
                "script": "pipeline/databricks/01_bronze_ingest.py",
            },
            {
                "name": "Silver",
                "purpose": "Clean and standardize types, column names, and quality edge cases.",
                "output": "opioid.silver_clean",
                "script": "pipeline/databricks/02_silver_clean.py",
            },
            {
                "name": "Gold",
                "purpose": "Produce analytics-ready state-year and latest-state aggregates.",
                "output": "opioid.gold_state_year / opioid.gold_state_latest",
                "script": "pipeline/databricks/03_gold_aggregates.py",
            },
            {
                "name": "Publish",
                "purpose": "Export curated Gold outputs to OneLake/Fabric for BI consumption.",
                "output": "OneLake parquet folders",
                "script": "pipeline/databricks/04_publish_to_onelake.py",
            },
        ],
        "databricks_assets": [
            "pipeline/databricks/01_bronze_ingest.py",
            "pipeline/databricks/02_silver_clean.py",
            "pipeline/databricks/03_gold_aggregates.py",
            "pipeline/databricks/04_publish_to_onelake.py",
            "pipeline/databricks/pipeline_overview.md",
        ],
    }


def get_pipeline_run_summary() -> dict:
    """Return pipeline summary from static artifact when present, else compute from DB."""
    report_path = settings.static_api_dir / "pipeline_run_summary.json"
    if report_path.exists():
        return json.loads(report_path.read_text(encoding="utf-8"))

    df = load_state_year_df()
    if df.empty:
        raise HTTPException(404, "No data")

    q_report = build_quality_report(df)
    return build_pipeline_summary(df, q_report["status"], q_report["checked_at"])
