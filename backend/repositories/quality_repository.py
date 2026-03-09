"""Repository layer for quality-report serving table."""

from __future__ import annotations

from db import fetch_all
from settings import settings


def _table(name: str) -> str:
    return f"{settings.postgres_schema}.{name}" if settings.db_backend == "postgres" else name


class QualityRepository:
    @staticmethod
    def fetch_quality_rows() -> list[dict]:
        return fetch_all(
            f"""
            SELECT checked_at, check_name, status, value_json, threshold_json, detail
            FROM {_table('quality_report')}
            ORDER BY check_name
            """
        )
