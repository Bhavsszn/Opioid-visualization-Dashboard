"""SQL repository for state-level metrics data."""

from __future__ import annotations

import logging

from db import fetch_all, fetch_one
from settings import settings

logger = logging.getLogger("opioid.metrics_repository")


def _table(name: str) -> str:
    if settings.db_backend == "postgres":
        schema = settings.postgres_schema.strip()
        return f'"{schema}"."{name}"'
    return name


def _param() -> str:
    return "%s" if settings.db_backend == "postgres" else "?"


def _log_table_error(operation: str, table_name: str, exc: Exception) -> None:
    if settings.db_backend == "postgres":
        logger.exception(
            "query_failed op=%s table=%s.%s backend=%s error=%s",
            operation,
            settings.postgres_schema,
            table_name,
            settings.db_backend,
            str(exc),
        )
    else:
        logger.exception(
            "query_failed op=%s table=%s backend=%s error=%s",
            operation,
            table_name,
            settings.db_backend,
            str(exc),
        )


class MetricsRepository:
    """Encapsulates read operations for metric endpoints."""

    @staticmethod
    def fetch_state_year_data(state: str | None = None, year: int | None = None) -> list[dict]:
        p = _param()
        sql = f"""
            SELECT year, state, deaths, population, crude_rate, age_adjusted_rate
            FROM {_table('state_year_overdoses')}
            WHERE 1=1
        """
        params: list[object] = []
        if state:
            sql += f" AND state = {p}"
            params.append(state)
        if year is not None:
            sql += f" AND year = {p}"
            params.append(year)
        sql += " ORDER BY year, state"
        try:
            return fetch_all(sql, params)
        except Exception as exc:
            _log_table_error("fetch_state_year_data", "state_year_overdoses", exc)
            raise

    @staticmethod
    def fetch_latest_state_metrics(year: int | None = None) -> tuple[int | None, list[dict]]:
        p = _param()
        selected_year = year
        if selected_year is None:
            try:
                row = fetch_one(f"SELECT MAX(year) AS latest_year FROM {_table('state_year_overdoses')}")
            except Exception as exc:
                _log_table_error("fetch_latest_state_metrics.max_year", "state_year_overdoses", exc)
                raise
            if not row or row.get("latest_year") is None:
                return None, []
            selected_year = int(row["latest_year"])

        try:
            rows = fetch_all(
                f"""
                SELECT year, state, deaths, population, crude_rate, age_adjusted_rate
                FROM {_table('states_latest')}
                WHERE year = {p}
                ORDER BY crude_rate DESC
                """,
                (selected_year,),
            )
        except Exception as exc:
            _log_table_error("fetch_latest_state_metrics.states_latest", "states_latest", exc)
            raise

        if not rows:
            try:
                rows = fetch_all(
                    f"""
                    SELECT year, state, deaths, population, crude_rate, age_adjusted_rate
                    FROM {_table('state_year_overdoses')}
                    WHERE year = {p}
                    ORDER BY crude_rate DESC
                    """,
                    (selected_year,),
                )
            except Exception as exc:
                _log_table_error("fetch_latest_state_metrics.state_year_overdoses", "state_year_overdoses", exc)
                raise

        return selected_year, rows

    @staticmethod
    def fetch_state_history(state: str) -> list[dict]:
        p = _param()
        try:
            return fetch_all(
                f"""
                SELECT year, state, deaths, population, crude_rate, age_adjusted_rate
                FROM {_table('state_year_overdoses')}
                WHERE state = {p}
                ORDER BY year
                """,
                (state,),
            )
        except Exception as exc:
            _log_table_error("fetch_state_history", "state_year_overdoses", exc)
            raise

    @staticmethod
    def fetch_state_deaths_history(state: str) -> list[dict]:
        p = _param()
        try:
            return fetch_all(
                f"""
                SELECT year, deaths
                FROM {_table('state_year_overdoses')}
                WHERE state = {p}
                ORDER BY year
                """,
                (state,),
            )
        except Exception as exc:
            _log_table_error("fetch_state_deaths_history", "state_year_overdoses", exc)
            raise
