import json
import os
import pathlib
import sqlite3
from typing import Any

import pandas as pd

from forecast_eval import evaluate_all_states, forecast_state
from quality import build_quality_report
from settings import settings

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DB_PATH = os.environ.get("DB_PATH", str(settings.db_path))
CSV_PATH = os.environ.get(
    "CSV_PATH", os.path.join(str(settings.data_dir), "overdoses_state_year_clean_typed.csv")
)
OUT_DIR = os.environ.get(
    "STATIC_OUT_DIR", str(settings.static_api_dir)
)
ARTIFACTS_DIR = os.environ.get("ARTIFACTS_DIR", os.path.join(ROOT, "artifacts"))
pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
pathlib.Path(ARTIFACTS_DIR).mkdir(parents=True, exist_ok=True)


def dump_json(path: str, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def dump_static(filename: str, obj: Any) -> None:
    dump_json(os.path.join(OUT_DIR, filename), obj)


def dump_artifact(filename: str, obj: Any) -> None:
    dump_json(os.path.join(ARTIFACTS_DIR, filename), obj)


def _safe_float(value: Any) -> float | None:
    if pd.isna(value):
        return None
    return float(value)


def load_dataframe() -> tuple[pd.DataFrame, str]:
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        try:
            df = pd.read_sql_query(
                """
                SELECT year, state, population, deaths, crude_rate, age_adjusted_rate
                FROM state_year_overdoses
                ORDER BY year, state
                """,
                conn,
            )
            return df, f"sqlite:{DB_PATH}"
        finally:
            conn.close()

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        needed = ["year", "state", "population", "deaths", "crude_rate", "age_adjusted_rate"]
        missing = [c for c in needed if c not in df.columns]
        if missing:
            raise ValueError(f"CSV is missing required columns: {missing}")
        df = df[needed].copy()
        return df, f"csv:{CSV_PATH}"

    raise FileNotFoundError(f"Could not find SQLite database at {DB_PATH} or CSV at {CSV_PATH}.")


def build_static_payloads(df: pd.DataFrame) -> dict[str, Any]:
    df["year"] = df["year"].astype(int)
    for col in ["population", "deaths", "crude_rate", "age_adjusted_rate"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    states = sorted(df["state"].dropna().unique().tolist())
    dump_static("states.json", states)

    metrics_by_state: dict[str, list[dict[str, Any]]] = {}
    for state in states:
        subset = df[df["state"] == state].sort_values("year")
        metrics_by_state[state] = [
            {
                "year": int(row["year"]),
                "deaths": _safe_float(row["deaths"]),
                "population": _safe_float(row["population"]),
                "crude_rate": _safe_float(row["crude_rate"]),
                "overdose_rate": _safe_float(row["crude_rate"]),
                "age_adjusted_rate": _safe_float(row["age_adjusted_rate"]),
            }
            for _, row in subset.iterrows()
        ]
    dump_static("metrics_state_year.json", metrics_by_state)

    latest_year = int(df["year"].max())
    latest = df[df["year"] == latest_year].sort_values("crude_rate", ascending=False).reset_index(drop=True)
    states_latest = [
        {
            "state": row["state"],
            "year": int(row["year"]),
            "population": _safe_float(row["population"]),
            "deaths": _safe_float(row["deaths"]),
            "crude_rate": _safe_float(row["crude_rate"]),
            "overdose_rate": _safe_float(row["crude_rate"]),
            "age_adjusted_rate": _safe_float(row["age_adjusted_rate"]),
        }
        for _, row in latest.iterrows()
    ]
    dump_static("states_latest.json", states_latest)

    forecasts: dict[str, list[dict[str, Any]]] = {}
    for state in states:
        series_df = df[df["state"] == state][["state", "year", "deaths"]].dropna().copy()
        if series_df.empty:
            forecasts[state] = []
            continue
        rows, _ = forecast_state(series_df, horizon=5)
        forecasts[state] = rows
    dump_static("forecast_by_state.json", forecasts)

    quality_report = build_quality_report(df)
    dump_static("quality_report.json", quality_report)

    eval_report = evaluate_all_states(df[["state", "year", "deaths"]].dropna())
    dump_static("forecast_evaluation.json", eval_report)

    checked_at = quality_report["checked_at"]
    pipeline_summary = {
        "run_id": checked_at.replace(":", "").replace("-", ""),
        "checked_at": checked_at,
        "source": "databricks-medallion-pattern",
        "row_count": int(len(df)),
        "states": int(df["state"].nunique()),
        "years": {"min": int(df["year"].min()), "max": int(df["year"].max())},
        "quality_status": quality_report["status"],
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
    dump_static("pipeline_run_summary.json", pipeline_summary)
    dump_artifact("pipeline_run_summary.json", pipeline_summary)

    return {
        "quality_report": quality_report,
        "forecast_evaluation": eval_report,
        "pipeline_summary": pipeline_summary,
        "latest_year": latest_year,
    }


def main() -> None:
    df, source = load_dataframe()
    reports = build_static_payloads(df)
    health_payload = {
        "ok": True,
        "source": source,
        "rows": int(len(df)),
        "latest_year": int(df["year"].max()),
        "quality_status": reports["quality_report"]["status"],
        "quality_checked_at": reports["quality_report"]["checked_at"],
    }
    dump_static("health.json", health_payload)

    snapshot = {
        "source": source,
        "created_at": reports["quality_report"]["checked_at"],
        "quality": reports["quality_report"],
        "forecast_evaluation": reports["forecast_evaluation"],
    }
    dump_artifact("portfolio_analysis_snapshot.json", snapshot)

    print(f"Exported static API files to: {OUT_DIR}")
    print(f"Wrote portfolio artifacts to: {ARTIFACTS_DIR}")
    print(f"Source: {source}")


if __name__ == "__main__":
    main()
