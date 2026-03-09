"""Forecast router (evaluation, forecasts, and demo policy/risk endpoints)."""

from fastapi import APIRouter

from settings import settings
from services.forecast_service import (
    get_forecast_evaluation,
    get_forecast_sarimax,
    get_forecast_simple,
    run_risk_score,
    run_simulator_whatif,
)

router = APIRouter(tags=["forecast"])


@router.get("/api/forecast/evaluation")
def forecast_evaluation():
    """Return model benchmark metrics by state and aggregate."""
    return get_forecast_evaluation()


@router.get("/api/forecast/simple")
def forecast_simple(state: str, horizon: int = settings.default_forecast_horizon):
    """Return forecast payload with backward-compatible aliases and metadata."""
    return get_forecast_simple(state=state, horizon=horizon)


@router.get("/api/forecast/sarimax")
def forecast_sarimax(state: str, horizon: int = settings.default_forecast_horizon):
    """Compatibility endpoint retaining legacy path semantics."""
    return get_forecast_sarimax(state=state, horizon=horizon)


@router.post("/api/simulator/whatif")
def simulator_whatif(
    state: str,
    rx_reduction_pct: float = 0.0,
    mat_increase_pct: float = 0.0,
    naloxone_coverage_pct: float = 0.0,
    horizon: int = settings.default_forecast_horizon,
):
    """Demo what-if simulator endpoint retained from existing behavior."""
    return run_simulator_whatif(
        state=state,
        rx_reduction_pct=rx_reduction_pct,
        mat_increase_pct=mat_increase_pct,
        naloxone_coverage_pct=naloxone_coverage_pct,
        horizon=horizon,
    )


@router.post("/api/risk/score")
def risk_score(age: int, prior_overdose: int, high_mme: int, polysubstance: int, mental_dx: int, male: int):
    """Demo risk scoring endpoint retained for compatibility."""
    return run_risk_score(
        age=age,
        prior_overdose=prior_overdose,
        high_mme=high_mme,
        polysubstance=polysubstance,
        mental_dx=mental_dx,
        male=male,
    )
