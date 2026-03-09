"""Anomalies and hotspot router."""

from fastapi import APIRouter

from services.anomaly_service import get_anomalies, get_hotspots_kmeans

router = APIRouter(tags=["anomalies"])


@router.get("/api/anomalies")
def anomalies(state: str, window: int = 3, z_threshold: float = 2.0):
    """Return rolling-z anomaly rows for a selected state."""
    return get_anomalies(state=state, window=window, z_threshold=z_threshold)


@router.get("/api/hotspots/kmeans")
def hotspots_kmeans(k: int = 3, year: int | None = None):
    """Return KMeans clusters for latest state rates."""
    return get_hotspots_kmeans(k=k, year=year)
