"""Repository layer for quality-report serving table."""

from __future__ import annotations

import logging

from db import fetch_all
from settings import settings

logger = logging.getLogger("opioid.quality_repository")


def _table(name: str) -> str:
    if settings.db_backend == "postgres":
        schema = settings.postgres_schema.strip()
        return f'"{schema}"."{name}"'
    return name


class QualityRepository:
    @staticmethod
    def fetch_quality_rows() -> list[dict]:
        try:
            return fetch_all(
                f"""
                SELECT checked_at, check_name, status, value_json, threshold_json, detail
                FROM {_table('quality_report')}
                ORDER BY check_name
                """
            )
        except Exception:
            logger.exception(
                "query_failed op=fetch_quality_rows table=%s.quality_report backend=%s",
                settings.postgres_schema,
                settings.db_backend,
            )
            raise
