"""Repository layer for forecast-related precomputed assets."""

from __future__ import annotations

import logging

from db import fetch_all
from settings import settings

logger = logging.getLogger("opioid.forecast_repository")


def _table(name: str) -> str:
    if settings.db_backend == "postgres":
        schema = settings.postgres_schema.strip()
        return f'"{schema}"."{name}"'
    return name


class ForecastRepository:
    @staticmethod
    def fetch_forecast_output(state: str) -> list[dict]:
        try:
            return fetch_all(
                f"""
                SELECT year, forecast_deaths, forecast_deaths_lo, forecast_deaths_hi
                FROM {_table('forecast_output')}
                WHERE state = ?
                ORDER BY year
                """,
                (state,),
            )
        except Exception:
            logger.exception(
                "query_failed op=fetch_forecast_output table=%s.forecast_output backend=%s",
                settings.postgres_schema,
                settings.db_backend,
            )
            raise
