"""Anomaly detection and hotspot clustering services."""

import pandas as pd
from fastapi import HTTPException
from sklearn.cluster import KMeans

from db import query
from services.metrics_service import get_states_latest


def get_anomalies(state: str, window: int = 3, z_threshold: float = 2.0) -> dict:
    rows = query("SELECT year, deaths FROM state_year_overdoses WHERE state=? ORDER BY year", (state,))
    if not rows:
        raise HTTPException(404, "No data")
    df = pd.DataFrame(rows)
    df["diff"] = df["deaths"].diff()
    roll = df["diff"].rolling(window=window, min_periods=window).mean()
    std = df["diff"].rolling(window=window, min_periods=window).std()
    z = (df["diff"] - roll) / std
    df["z"] = z
    df["is_anomaly"] = (df["z"].abs() >= z_threshold).fillna(False)
    return {"rows": df.fillna(0).to_dict(orient="records"), "window": window, "z_threshold": z_threshold}


def get_hotspots_kmeans(k: int = 3, year: int | None = None) -> dict:
    latest = get_states_latest(year)
    df = pd.DataFrame(latest["rows"])
    if df.empty or "crude_rate" not in df.columns:
        return {"clusters": []}

    x_vals = df[["crude_rate"]].fillna(0.0).values
    k = max(1, min(k, len(df)))
    km = KMeans(n_clusters=k, n_init="auto", random_state=42).fit(x_vals)
    df["cluster"] = km.labels_

    order = df.groupby("cluster")["crude_rate"].mean().sort_values(ascending=False).index.tolist()
    rank_map = {cluster: idx + 1 for idx, cluster in enumerate(order)}
    df["cluster_rank"] = df["cluster"].map(rank_map)
    df = df.sort_values(["cluster_rank", "crude_rate"], ascending=[True, False])
    return {"year": latest["year"], "clusters": df.to_dict(orient="records")}
