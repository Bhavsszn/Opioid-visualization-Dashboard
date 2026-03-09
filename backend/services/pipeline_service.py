"""Pipeline summary service with artifact fallback."""

from __future__ import annotations

from quality import build_quality_report
from services.metrics_service import load_state_year_df
from utils.artifact_loader import load_artifact


def build_pipeline_summary(df, quality_status: str, checked_at: str) -> dict:
    """Build pipeline summary used by dashboard pipeline page."""
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
    """Return static pipeline summary if available, else compute from DB."""
    artifact = load_artifact("pipeline_run_summary.json")
    if artifact:
        return artifact

    df = load_state_year_df()
    if df.empty:
        return build_pipeline_summary(df, "fail", "")

    quality_report = build_quality_report(df)
    return build_pipeline_summary(df, quality_report["status"], quality_report["checked_at"])
