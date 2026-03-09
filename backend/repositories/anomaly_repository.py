"""Repository layer for anomaly-related data reads."""

from __future__ import annotations

from repositories.metrics_repository import MetricsRepository


class AnomalyRepository:
    @staticmethod
    def fetch_state_deaths_history(state: str) -> list[dict]:
        return MetricsRepository.fetch_state_deaths_history(state)
