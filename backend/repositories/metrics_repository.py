"""SQL repository for state-level metrics data."""

from __future__ import annotations

from db import fetch_all, fetch_one
from settings import settings


def _table(name: str) -> str:
    return f"{settings.postgres_schema}.{name}" if settings.db_backend == "postgres" else name


class MetricsRepository:
    """Encapsulates read operations for metric endpoints."""

    @staticmethod
    def fetch_state_year_data(state: str | None = None, year: int | None = None) -> list[dict]:
        sql = f"""
            SELECT year, state, deaths, population, crude_rate, age_adjusted_rate
            FROM {_table('state_year_overdoses')}
            WHERE 1=1
        """
        params: list[object] = []
        if state:
            sql += " AND state = ?"
            params.append(state)
        if year is not None:
            sql += " AND year = ?"
            params.append(year)
        sql += " ORDER BY year, state"
        return fetch_all(sql, params)

    @staticmethod
    def fetch_latest_state_metrics(year: int | None = None) -> tuple[int | None, list[dict]]:
        selected_year = year
        if selected_year is None:
            row = fetch_one(f"SELECT MAX(year) AS latest_year FROM {_table('state_year_overdoses')}")
            if not row or row.get("latest_year") is None:
                return None, []
            selected_year = int(row["latest_year"])

        rows = fetch_all(
            f"""
            SELECT year, state, deaths, population, crude_rate, age_adjusted_rate
            FROM {_table('states_latest')}
            WHERE year = ?
            ORDER BY crude_rate DESC
            """,
            (selected_year,),
        )

        if not rows:
            rows = fetch_all(
                f"""
                SELECT year, state, deaths, population, crude_rate, age_adjusted_rate
                FROM {_table('state_year_overdoses')}
                WHERE year = ?
                ORDER BY crude_rate DESC
                """,
                (selected_year,),
            )

        return selected_year, rows

    @staticmethod
    def fetch_state_history(state: str) -> list[dict]:
        return fetch_all(
            f"""
            SELECT year, state, deaths, population, crude_rate, age_adjusted_rate
            FROM {_table('state_year_overdoses')}
            WHERE state = ?
            ORDER BY year
            """,
            (state,),
        )

    @staticmethod
    def fetch_state_deaths_history(state: str) -> list[dict]:
        return fetch_all(
            f"""
            SELECT year, deaths
            FROM {_table('state_year_overdoses')}
            WHERE state = ?
            ORDER BY year
            """,
            (state,),
        )
