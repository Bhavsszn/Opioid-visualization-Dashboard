"""Populate PostgreSQL serving tables from local project data.

This script codifies local/manual serving-table fixes into a repeatable flow.
It is safe to rerun and uses backend settings/environment for connectivity.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from quality import build_quality_report  # noqa: E402
from settings import settings  # noqa: E402

try:
    import psycopg
except Exception as exc:  # pragma: no cover
    raise RuntimeError("psycopg is required to populate PostgreSQL serving tables") from exc

logger = logging.getLogger("populate_postgres_serving_tables")

STATE_YEAR_COLUMNS = ["state", "year", "deaths", "population", "crude_rate", "age_adjusted_rate"]


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Populate PostgreSQL serving tables from local data.")
    parser.add_argument(
        "--source-csv",
        default=str(ROOT / "data" / "overdoses_state_year_clean_typed.csv"),
        help="Path to source CSV with state/year overdose metrics.",
    )
    parser.add_argument(
        "--only",
        choices=["all", "state_year_overdoses", "states_latest", "quality_report", "pipeline_run_summary"],
        default="all",
        help="Populate only one serving table target.",
    )
    return parser.parse_args()


def _schema_prefix() -> str:
    return settings.postgres_schema.strip()


def _connect():
    if settings.db_backend != "postgres":
        raise RuntimeError("DB_BACKEND must be 'postgres' to run this script.")
    conn = psycopg.connect(settings.postgres_dsn, autocommit=False)
    schema = _schema_prefix()
    conn.execute(f'SET search_path TO "{schema}", public')
    return conn


def _load_source_df(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Source CSV not found: {csv_path}")

    frame = pd.read_csv(csv_path)
    missing = [column for column in STATE_YEAR_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Source CSV is missing required columns: {missing}")

    frame = frame[STATE_YEAR_COLUMNS].copy()
    frame["state"] = frame["state"].astype(str).str.strip()
    frame["year"] = pd.to_numeric(frame["year"], errors="coerce").astype("Int64")
    for column in ["deaths", "population", "crude_rate", "age_adjusted_rate"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    frame = frame.dropna(subset=["state", "year"])
    frame["year"] = frame["year"].astype(int)
    frame = frame.sort_values(["state", "year"]).drop_duplicates(["state", "year"], keep="last")
    return frame


def upsert_state_year_overdoses(conn, frame: pd.DataFrame) -> int:
    if frame.empty:
        logger.warning("state_year_overdoses source dataframe is empty; skipping.")
        return 0

    schema = _schema_prefix()
    sql = f"""
        INSERT INTO "{schema}"."state_year_overdoses"
            (state, year, deaths, population, crude_rate, age_adjusted_rate)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (state, year)
        DO UPDATE SET
            deaths = EXCLUDED.deaths,
            population = EXCLUDED.population,
            crude_rate = EXCLUDED.crude_rate,
            age_adjusted_rate = EXCLUDED.age_adjusted_rate,
            updated_at = now()
    """
    payload = [
        (
            row["state"],
            int(row["year"]),
            None if pd.isna(row["deaths"]) else float(row["deaths"]),
            None if pd.isna(row["population"]) else float(row["population"]),
            None if pd.isna(row["crude_rate"]) else float(row["crude_rate"]),
            None if pd.isna(row["age_adjusted_rate"]) else float(row["age_adjusted_rate"]),
        )
        for _, row in frame.iterrows()
    ]
    conn.executemany(sql, payload)
    return len(payload)


def refresh_states_latest(conn) -> int:
    schema = _schema_prefix()
    conn.execute(f'DELETE FROM "{schema}"."states_latest"')
    insert_sql = f"""
        INSERT INTO "{schema}"."states_latest"
            (state, year, deaths, population, crude_rate, age_adjusted_rate)
        SELECT state, year, deaths, population, crude_rate, age_adjusted_rate
        FROM "{schema}"."state_year_overdoses"
        WHERE year = (SELECT MAX(year) FROM "{schema}"."state_year_overdoses")
        ORDER BY crude_rate DESC NULLS LAST, state
    """
    conn.execute(insert_sql)
    count_sql = f'SELECT COUNT(*) AS n FROM "{schema}"."states_latest"'
    count = conn.execute(count_sql).fetchone()[0]
    return int(count or 0)


def refresh_quality_report(conn, frame: pd.DataFrame) -> int:
    if frame.empty:
        logger.warning("quality_report source dataframe is empty; skipping.")
        return 0

    quality_report = build_quality_report(frame)
    checked_at = quality_report.get("checked_at")
    checks = quality_report.get("checks", [])
    schema = _schema_prefix()

    conn.execute(f'DELETE FROM "{schema}"."quality_report"')
    insert_sql = f"""
        INSERT INTO "{schema}"."quality_report"
            (checked_at, check_name, status, value_json, threshold_json, detail)
        VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s)
    """

    payload = []
    for check in checks:
        payload.append(
            (
                checked_at,
                check.get("name", "unknown_check"),
                check.get("status", "fail"),
                json.dumps(check.get("value", {})),
                json.dumps(check.get("threshold", {})),
                check.get("detail", ""),
            )
        )

    if payload:
        conn.executemany(insert_sql, payload)
    return len(payload)


def refresh_pipeline_run_summary(conn, frame: pd.DataFrame) -> str:
    schema = _schema_prefix()
    checked_at = datetime.now(timezone.utc).isoformat()
    run_id = checked_at.replace(":", "").replace("-", "")

    quality_status = "unknown"
    quality_row = conn.execute(
        f'SELECT status FROM "{schema}"."quality_report" ORDER BY checked_at DESC, check_name ASC LIMIT 1'
    ).fetchone()
    if quality_row:
        quality_status = "pass" if str(quality_row[0]).lower() == "pass" else "fail"

    stages = [
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
    ]
    databricks_assets = [
        "pipeline/databricks/01_bronze_ingest.py",
        "pipeline/databricks/02_silver_clean.py",
        "pipeline/databricks/03_gold_aggregates.py",
        "pipeline/databricks/05_gold_quality_and_forecast.sql",
        "pipeline/postgres/analytics_schema.sql",
        "scripts/sync_databricks_to_postgres.py",
    ]

    row_count = int(len(frame))
    states = int(frame["state"].nunique()) if not frame.empty else 0
    min_year = int(frame["year"].min()) if not frame.empty else None
    max_year = int(frame["year"].max()) if not frame.empty else None

    conn.execute(f'DELETE FROM "{schema}"."pipeline_run_summary"')
    upsert_sql = f"""
        INSERT INTO "{schema}"."pipeline_run_summary"
            (run_id, checked_at, source, row_count, states, min_year, max_year, quality_status, stages_json, databricks_assets_json)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
        ON CONFLICT (run_id)
        DO UPDATE SET
            checked_at = EXCLUDED.checked_at,
            source = EXCLUDED.source,
            row_count = EXCLUDED.row_count,
            states = EXCLUDED.states,
            min_year = EXCLUDED.min_year,
            max_year = EXCLUDED.max_year,
            quality_status = EXCLUDED.quality_status,
            stages_json = EXCLUDED.stages_json,
            databricks_assets_json = EXCLUDED.databricks_assets_json
    """
    conn.execute(
        upsert_sql,
        (
            run_id,
            checked_at,
            "local-refresh",
            row_count,
            states,
            min_year,
            max_year,
            quality_status,
            json.dumps(stages),
            json.dumps(databricks_assets),
        ),
    )
    return run_id


def main() -> None:
    configure_logging()
    args = parse_args()
    source_csv = Path(args.source_csv).resolve()

    logger.info(
        "starting backend=%s schema=%s static_fallback=%s sqlite_fallback=%s source_csv=%s",
        settings.db_backend,
        settings.postgres_schema,
        settings.enable_static_fallback,
        settings.enable_sqlite_fallback,
        source_csv,
    )

    df = _load_source_df(source_csv)

    with _connect() as conn:
        try:
            if args.only in {"all", "state_year_overdoses"}:
                count = upsert_state_year_overdoses(conn, df)
                logger.info("upserted rows into state_year_overdoses=%s", count)

            if args.only in {"all", "states_latest"}:
                count = refresh_states_latest(conn)
                logger.info("refreshed states_latest rows=%s", count)

            if args.only in {"all", "quality_report"}:
                count = refresh_quality_report(conn, df)
                logger.info("refreshed quality_report checks=%s", count)

            if args.only in {"all", "pipeline_run_summary"}:
                run_id = refresh_pipeline_run_summary(conn, df)
                logger.info("refreshed pipeline_run_summary run_id=%s", run_id)

            conn.commit()
        except Exception:
            conn.rollback()
            logger.exception("populate_failed")
            raise

    logger.info("populate complete")


if __name__ == "__main__":
    main()
