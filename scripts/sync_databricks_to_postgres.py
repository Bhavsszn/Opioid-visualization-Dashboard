"""Sync curated Databricks Gold outputs into PostgreSQL analytics schema.

Run modes:
- Databricks SQL Warehouse source (default if DATABRICKS_* vars are set)
- Local parquet/json source fallback for CI/local demo
"""

from __future__ import annotations

import json
import logging
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import psycopg
from psycopg.rows import dict_row

try:
    from databricks import sql as dbsql
except Exception:  # pragma: no cover
    dbsql = None


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("sync_databricks_to_postgres")


@dataclass
class Config:
    postgres_dsn: str
    postgres_schema: str
    databricks_host: str | None
    databricks_http_path: str | None
    databricks_token: str | None
    local_publish_dir: Path


TABLES = [
    "state_year_overdoses",
    "states_latest",
    "quality_report",
    "pipeline_run_summary",
    "forecast_output",
]


def load_config() -> Config:
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    dbname = os.getenv("POSTGRES_DB", "opioid")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    schema = os.getenv("POSTGRES_SCHEMA", "analytics")
    sslmode = os.getenv("POSTGRES_SSLMODE", "prefer")

    dsn = os.getenv("DATABASE_URL") or f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode={sslmode}"

    return Config(
        postgres_dsn=dsn,
        postgres_schema=schema,
        databricks_host=os.getenv("DATABRICKS_HOST"),
        databricks_http_path=os.getenv("DATABRICKS_HTTP_PATH"),
        databricks_token=os.getenv("DATABRICKS_TOKEN"),
        local_publish_dir=Path(os.getenv("LOCAL_PUBLISH_DIR", "pipeline/publish")),
    )


@contextmanager
def pg_connection(dsn: str):
    conn = psycopg.connect(dsn, row_factory=dict_row, autocommit=False)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_databricks_table(cfg: Config, table_name: str) -> pd.DataFrame:
    if cfg.databricks_host and cfg.databricks_http_path and cfg.databricks_token and dbsql is not None:
        logger.info("Reading gold.%s from Databricks SQL Warehouse", table_name)
        with dbsql.connect(
            server_hostname=cfg.databricks_host,
            http_path=cfg.databricks_http_path,
            access_token=cfg.databricks_token,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM gold.{table_name}")
                rows = cursor.fetchall_arrow().to_pandas()
                return rows

    parquet_path = cfg.local_publish_dir / table_name
    if parquet_path.exists():
        logger.info("Reading %s from local parquet fallback", parquet_path)
        return pd.read_parquet(parquet_path)

    json_path = cfg.local_publish_dir / f"{table_name}.json"
    if json_path.exists():
        logger.info("Reading %s from local json fallback", json_path)
        return pd.read_json(json_path)

    logger.warning("No source found for %s; returning empty frame", table_name)
    return pd.DataFrame()


def upsert_state_year(conn, schema: str, frame: pd.DataFrame) -> None:
    if frame.empty:
        return
    sql = f"""
        INSERT INTO {schema}.state_year_overdoses
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
            str(row["state"]),
            int(row["year"]),
            None if pd.isna(row.get("deaths")) else float(row.get("deaths")),
            None if pd.isna(row.get("population")) else float(row.get("population")),
            None if pd.isna(row.get("crude_rate")) else float(row.get("crude_rate")),
            None if pd.isna(row.get("age_adjusted_rate")) else float(row.get("age_adjusted_rate")),
        )
        for _, row in frame.iterrows()
    ]
    conn.executemany(sql, payload)


def upsert_states_latest(conn, schema: str, frame: pd.DataFrame) -> None:
    if frame.empty:
        return
    sql = f"""
        INSERT INTO {schema}.states_latest
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
            str(row["state"]),
            int(row["year"]),
            None if pd.isna(row.get("deaths")) else float(row.get("deaths")),
            None if pd.isna(row.get("population")) else float(row.get("population")),
            None if pd.isna(row.get("crude_rate")) else float(row.get("crude_rate")),
            None if pd.isna(row.get("age_adjusted_rate")) else float(row.get("age_adjusted_rate")),
        )
        for _, row in frame.iterrows()
    ]
    conn.executemany(sql, payload)


def upsert_quality_report(conn, schema: str, frame: pd.DataFrame) -> None:
    if frame.empty:
        return
    sql = f"""
        INSERT INTO {schema}.quality_report
            (checked_at, check_name, status, value_json, threshold_json, detail)
        VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s)
        ON CONFLICT (checked_at, check_name)
        DO UPDATE SET
            status = EXCLUDED.status,
            value_json = EXCLUDED.value_json,
            threshold_json = EXCLUDED.threshold_json,
            detail = EXCLUDED.detail
    """
    payload = [
        (
            row.get("checked_at"),
            row.get("check_name"),
            row.get("status"),
            row.get("value_json") if isinstance(row.get("value_json"), str) else json.dumps(row.get("value_json") or {}),
            row.get("threshold_json")
            if isinstance(row.get("threshold_json"), str)
            else json.dumps(row.get("threshold_json") or {}),
            row.get("detail"),
        )
        for _, row in frame.iterrows()
    ]
    conn.executemany(sql, payload)


def upsert_pipeline_summary(conn, schema: str, frame: pd.DataFrame) -> None:
    if frame.empty:
        return
    sql = f"""
        INSERT INTO {schema}.pipeline_run_summary
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
    payload = [
        (
            row.get("run_id"),
            row.get("checked_at"),
            row.get("source", "databricks-medallion-pattern"),
            int(row.get("row_count", 0)),
            int(row.get("states", 0)),
            int(row.get("min_year", 0)) if pd.notna(row.get("min_year")) else None,
            int(row.get("max_year", 0)) if pd.notna(row.get("max_year")) else None,
            row.get("quality_status", "unknown"),
            row.get("stages_json") if isinstance(row.get("stages_json"), str) else json.dumps(row.get("stages_json") or []),
            row.get("databricks_assets_json")
            if isinstance(row.get("databricks_assets_json"), str)
            else json.dumps(row.get("databricks_assets_json") or []),
        )
        for _, row in frame.iterrows()
    ]
    conn.executemany(sql, payload)


def upsert_forecast_output(conn, schema: str, frame: pd.DataFrame) -> None:
    if frame.empty:
        return
    sql = f"""
        INSERT INTO {schema}.forecast_output
            (state, year, forecast_deaths, forecast_deaths_lo, forecast_deaths_hi,
             model_name, train_start_year, train_end_year, mae, mape, interval_coverage)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (state, year)
        DO UPDATE SET
            forecast_deaths = EXCLUDED.forecast_deaths,
            forecast_deaths_lo = EXCLUDED.forecast_deaths_lo,
            forecast_deaths_hi = EXCLUDED.forecast_deaths_hi,
            model_name = EXCLUDED.model_name,
            train_start_year = EXCLUDED.train_start_year,
            train_end_year = EXCLUDED.train_end_year,
            mae = EXCLUDED.mae,
            mape = EXCLUDED.mape,
            interval_coverage = EXCLUDED.interval_coverage,
            updated_at = now()
    """
    payload = [
        (
            row.get("state"),
            int(row.get("year")),
            None if pd.isna(row.get("forecast_deaths")) else float(row.get("forecast_deaths")),
            None if pd.isna(row.get("forecast_deaths_lo")) else float(row.get("forecast_deaths_lo")),
            None if pd.isna(row.get("forecast_deaths_hi")) else float(row.get("forecast_deaths_hi")),
            row.get("model_name"),
            int(row.get("train_start_year")) if pd.notna(row.get("train_start_year")) else None,
            int(row.get("train_end_year")) if pd.notna(row.get("train_end_year")) else None,
            None if pd.isna(row.get("mae")) else float(row.get("mae")),
            None if pd.isna(row.get("mape")) else float(row.get("mape")),
            None if pd.isna(row.get("interval_coverage")) else float(row.get("interval_coverage")),
        )
        for _, row in frame.iterrows()
    ]
    conn.executemany(sql, payload)


def main() -> None:
    cfg = load_config()

    with pg_connection(cfg.postgres_dsn) as conn:
        for table_name in TABLES:
            frame = fetch_databricks_table(cfg, table_name)
            logger.info("sync table=%s rows=%s", table_name, len(frame))

            if table_name == "state_year_overdoses":
                upsert_state_year(conn, cfg.postgres_schema, frame)
            elif table_name == "states_latest":
                upsert_states_latest(conn, cfg.postgres_schema, frame)
            elif table_name == "quality_report":
                upsert_quality_report(conn, cfg.postgres_schema, frame)
            elif table_name == "pipeline_run_summary":
                upsert_pipeline_summary(conn, cfg.postgres_schema, frame)
            elif table_name == "forecast_output":
                upsert_forecast_output(conn, cfg.postgres_schema, frame)

        conn.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {cfg.postgres_schema}.mv_states_latest")
        logger.info("refresh materialized view: %s.mv_states_latest", cfg.postgres_schema)

    logger.info("sync complete")


if __name__ == "__main__":
    main()
