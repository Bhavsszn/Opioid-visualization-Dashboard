"""Anomaly and hotspot router."""

from __future__ import annotations

from fastapi import APIRouter, Query

from schemas import AnomaliesResponse, HotspotsResponse
from services.anomaly_service import get_anomalies, get_hotspots_kmeans

router = APIRouter(tags=["anomalies"])


@router.get("/api/anomalies", response_model=AnomaliesResponse)
def anomalies(
    state: str = Query(..., min_length=1, max_length=64),
    window: int = Query(3, ge=2, le=15),
    z_threshold: float = Query(2.0, ge=0.1, le=10.0),
) -> AnomaliesResponse:
    """Return anomaly flags for yearly deaths in a selected state."""
    return AnomaliesResponse(**get_anomalies(state=state, window=window, z_threshold=z_threshold))


@router.get("/api/hotspots/kmeans", response_model=HotspotsResponse)
def hotspots_kmeans(
    k: int = Query(3, ge=1, le=10),
    year: int | None = Query(default=None, ge=1900, le=2100),
) -> HotspotsResponse:
    """Return KMeans clusters for latest available state rates."""
    return HotspotsResponse(**get_hotspots_kmeans(k=k, year=year))
