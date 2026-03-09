"""FastAPI app factory, middleware, and router registration."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from logging_config import configure_logging
from routers.anomalies import router as anomalies_router
from routers.forecast import router as forecast_router
from routers.health import router as health_router
from routers.metrics import router as metrics_router
from routers.pipeline import router as pipeline_router
from routers.quality import router as quality_router
from schemas import APIErrorResponse
from services.forecast_service import get_forecast_simple
from services.pipeline_service import get_pipeline_run_summary
from services.quality_service import get_quality_status
from settings import settings

configure_logging()
logger = logging.getLogger("opioid.api")

app = FastAPI(title="Opioid AI Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = request_id
    logger.info("request.start %s %s", request.method, request.url.path, extra={"request_id": request_id})
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    logger.info(
        "request.end %s %s status=%s",
        request.method,
        request.url.path,
        response.status_code,
        extra={"request_id": request_id},
    )
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        "http_error status=%s detail=%s",
        exc.status_code,
        exc.detail,
        extra={"request_id": request_id},
    )
    payload = APIErrorResponse(
        error_code="http_error",
        message=str(exc.detail),
        details=None,
        request_id=request_id,
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning("validation_error", extra={"request_id": request_id})
    payload = APIErrorResponse(
        error_code="validation_error",
        message="Invalid request parameters",
        details=exc.errors(),
        request_id=request_id,
    )
    return JSONResponse(status_code=422, content=payload.model_dump())


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception("unhandled_exception", extra={"request_id": request_id})
    payload = APIErrorResponse(
        error_code="internal_error",
        message="Unexpected server error",
        details=None,
        request_id=request_id,
    )
    return JSONResponse(status_code=500, content=payload.model_dump())


@app.on_event("startup")
def startup_log() -> None:
    logger.info(
        "startup environment=%s db_path=%s",
        settings.environment,
        settings.db_path,
        extra={"request_id": "-"},
    )


app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(forecast_router)
app.include_router(quality_router)
app.include_router(pipeline_router)
app.include_router(anomalies_router)

# Backward compatibility exports used by existing scripts/tests.
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
