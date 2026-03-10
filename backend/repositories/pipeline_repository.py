"""Repository layer for pipeline summary serving table."""

from __future__ import annotations

import logging

from db import fetch_one
from settings import settings

logger = logging.getLogger("opioid.pipeline_repository")


def _table(name: str) -> str:
    if settings.db_backend == "postgres":
        schema = settings.postgres_schema.strip()
        return f'"{schema}"."{name}"'
    return name


class PipelineRepository:
    @staticmethod
    def fetch_latest_summary() -> dict | None:
        try:
            return fetch_one(
                f"""
                SELECT run_id, checked_at, source, row_count, states, min_year, max_year,
                       quality_status, stages_json, databricks_assets_json
                FROM {_table('pipeline_run_summary')}
                ORDER BY checked_at DESC
                LIMIT 1
                """
            )
        except Exception:
            logger.exception(
                "query_failed op=fetch_latest_summary table=%s.pipeline_run_summary backend=%s",
                settings.postgres_schema,
                settings.db_backend,
            )
            raise
