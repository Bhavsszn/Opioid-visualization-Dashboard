"""Repository layer for pipeline summary serving table."""

from __future__ import annotations

from db import fetch_one
from settings import settings


def _table(name: str) -> str:
    return f"{settings.postgres_schema}.{name}"


class PipelineRepository:
    @staticmethod
    def fetch_latest_summary() -> dict | None:
        return fetch_one(
            f"""
            SELECT run_id, checked_at, source, row_count, states, min_year, max_year,
                   quality_status, stages_json, databricks_assets_json
            FROM {_table('pipeline_run_summary')}
            ORDER BY checked_at DESC
            LIMIT 1
            """
        )
