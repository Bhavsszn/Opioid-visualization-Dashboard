"""Repository layer for forecast-related precomputed assets."""

from __future__ import annotations

from db import fetch_all
from settings import settings


def _table(name: str) -> str:
    return f"{settings.postgres_schema}.{name}"


class ForecastRepository:
    @staticmethod
    def fetch_forecast_output(state: str) -> list[dict]:
        return fetch_all(
            f"""
            SELECT year, forecast_deaths, forecast_deaths_lo, forecast_deaths_hi
            FROM {_table('forecast_output')}
            WHERE state = ?
            ORDER BY year
            """,
            (state,),
        )
