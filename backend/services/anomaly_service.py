"""Anomaly detection and clustering services."""

from __future__ import annotations

import pandas as pd
from fastapi import HTTPException
from sklearn.cluster import KMeans

from repositories.metrics_repository import MetricsRepository
from services.metrics_service import get_states_latest
from utils.validation import normalize_state

repo = MetricsRepository()


def get_anomalies(state: str, window: int = 3, z_threshold: float = 2.0) -> dict:
    """Return rolling z-score anomalies for one state."""
    normalized_state = normalize_state(state)
    rows = repo.fetch_state_deaths_history(normalized_state or "")
    if not rows:
        raise HTTPException(status_code=404, detail="No data")

    frame = pd.DataFrame(rows)
    frame["diff"] = frame["deaths"].diff()
    rolling_mean = frame["diff"].rolling(window=window, min_periods=window).mean()
    rolling_std = frame["diff"].rolling(window=window, min_periods=window).std()
    frame["z"] = (frame["diff"] - rolling_mean) / rolling_std
    frame["is_anomaly"] = (frame["z"].abs() >= z_threshold).fillna(False)

    return {
        "rows": frame.fillna(0).to_dict(orient="records"),
        "window": window,
        "z_threshold": z_threshold,
    }


def get_hotspots_kmeans(k: int = 3, year: int | None = None) -> dict:
    """Cluster states by latest crude rate using KMeans."""
    latest = get_states_latest(year)
    frame = pd.DataFrame(latest["rows"])
    if frame.empty or "crude_rate" not in frame.columns:
        return {"year": latest["year"], "clusters": []}

    x_values = frame[["crude_rate"]].fillna(0.0).values
    n_clusters = max(1, min(k, len(frame)))
    km = KMeans(n_clusters=n_clusters, n_init="auto", random_state=42).fit(x_values)

    frame["cluster"] = km.labels_
    ordering = frame.groupby("cluster")["crude_rate"].mean().sort_values(ascending=False).index.tolist()
    rank_map = {cluster: idx + 1 for idx, cluster in enumerate(ordering)}
    frame["cluster_rank"] = frame["cluster"].map(rank_map)
    frame = frame.sort_values(["cluster_rank", "crude_rate"], ascending=[True, False])

    return {"year": latest["year"], "clusters": frame.to_dict(orient="records")}
