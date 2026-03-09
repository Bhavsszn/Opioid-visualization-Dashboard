"""Forecast and demo-model routers."""

from __future__ import annotations

from fastapi import APIRouter, Query

from schemas import ForecastEvaluationResponse, ForecastResponse, RiskScoreResponse, SimulatorResponse
from settings import settings
from services.forecast_service import (
    get_forecast_evaluation,
    get_forecast_sarimax,
    get_forecast_simple,
    run_risk_score,
    run_simulator_whatif,
)

router = APIRouter(tags=["forecast"])


@router.get("/api/forecast/evaluation", response_model=ForecastEvaluationResponse)
def forecast_evaluation() -> ForecastEvaluationResponse:
    """Return benchmark metrics by state and aggregate."""
    return ForecastEvaluationResponse(**get_forecast_evaluation())


@router.get("/api/forecast", response_model=ForecastResponse)
@router.get("/api/forecast/simple", response_model=ForecastResponse)
def forecast_simple(
    state: str = Query(..., min_length=1, max_length=64),
    horizon: int = Query(settings.default_forecast_horizon, ge=1, le=20),
) -> ForecastResponse:
    """Return forecast payload (compatibility route and canonical route)."""
    return ForecastResponse(**get_forecast_simple(state=state, horizon=horizon))


@router.get("/api/forecast/sarimax", response_model=ForecastResponse)
def forecast_sarimax(
    state: str = Query(..., min_length=1, max_length=64),
    horizon: int = Query(settings.default_forecast_horizon, ge=1, le=20),
) -> ForecastResponse:
    """Legacy route retaining SARIMAX naming semantics."""
    return ForecastResponse(**get_forecast_sarimax(state=state, horizon=horizon))


@router.post("/api/simulator/whatif", response_model=SimulatorResponse)
def simulator_whatif(
    state: str = Query(..., min_length=1, max_length=64),
    rx_reduction_pct: float = Query(0.0, ge=-100.0, le=100.0),
    mat_increase_pct: float = Query(0.0, ge=-100.0, le=100.0),
    naloxone_coverage_pct: float = Query(0.0, ge=-100.0, le=100.0),
    horizon: int = Query(settings.default_forecast_horizon, ge=1, le=20),
) -> SimulatorResponse:
    """Demo what-if simulator endpoint."""
    return SimulatorResponse(
        **run_simulator_whatif(
            state=state,
            rx_reduction_pct=rx_reduction_pct,
            mat_increase_pct=mat_increase_pct,
            naloxone_coverage_pct=naloxone_coverage_pct,
            horizon=horizon,
        )
    )


@router.post("/api/risk/score", response_model=RiskScoreResponse)
def risk_score(
    age: int = Query(..., ge=0, le=120),
    prior_overdose: int = Query(..., ge=0, le=1),
    high_mme: int = Query(..., ge=0, le=1),
    polysubstance: int = Query(..., ge=0, le=1),
    mental_dx: int = Query(..., ge=0, le=1),
    male: int = Query(..., ge=0, le=1),
) -> RiskScoreResponse:
    """Demo risk scoring endpoint."""
    return RiskScoreResponse(
        **run_risk_score(
            age=age,
            prior_overdose=prior_overdose,
            high_mme=high_mme,
            polysubstance=polysubstance,
            mental_dx=mental_dx,
            male=male,
        )
    )
