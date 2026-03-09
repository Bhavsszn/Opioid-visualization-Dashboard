"""FastAPI app creation and router registration."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings import settings
from routers.anomalies import router as anomalies_router
from routers.forecast import router as forecast_router
from routers.health import router as health_router
from routers.metrics import router as metrics_router
from routers.pipeline import router as pipeline_router
from routers.quality import router as quality_router
from services.forecast_service import get_forecast_simple
from services.pipeline_service import get_pipeline_run_summary
from services.quality_service import get_quality_status

app = FastAPI(title="Opioid AI Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Keep endpoint paths unchanged by registering routers that preserve current routes.
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(forecast_router)
app.include_router(quality_router)
app.include_router(pipeline_router)
app.include_router(anomalies_router)

# Compatibility exports for existing tests and scripts that imported api.py symbols.
DB_PATH = str(settings.db_path)


def _sync_db_path() -> None:
    settings.db_path = Path(DB_PATH)


def forecast_simple(state: str, horizon: int = settings.default_forecast_horizon):
    _sync_db_path()
    return get_forecast_simple(state=state, horizon=horizon)


def quality_status():
    _sync_db_path()
    return get_quality_status()


def pipeline_run_summary():
    _sync_db_path()
    return get_pipeline_run_summary()
