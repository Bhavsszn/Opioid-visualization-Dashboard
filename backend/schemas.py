"""Pydantic schemas for API request/response contracts."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class APIErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Any = None
    request_id: str


class HealthResponse(BaseModel):
    ok: bool
    db_exists: bool


class QualityCheck(BaseModel):
    name: str
    status: str
    value: Any
    threshold: Any
    detail: str


class QualitySummary(BaseModel):
    rows: int
    columns: list[str]
    latest_year: int | None
    pass_count: int
    fail_count: int
    pass_rate: float


class QualityReport(BaseModel):
    status: str
    checked_at: str
    checks: list[QualityCheck]
    summary: QualitySummary


class PipelineStage(BaseModel):
    name: str
    purpose: str
    output: str
    script: str


class PipelineRunSummary(BaseModel):
    run_id: str
    checked_at: str
    source: str
    row_count: int
    states: int
    years: dict[str, int]
    quality_status: str
    stages: list[PipelineStage]
    databricks_assets: list[str]


class StateYearRow(BaseModel):
    year: int
    state: str
    deaths: float | None = None
    population: float | None = None
    crude_rate: float | None = None
    age_adjusted_rate: float | None = None


class StateYearResponse(BaseModel):
    rows: list[StateYearRow]


class StatesLatestResponse(BaseModel):
    year: int | None
    rows: list[StateYearRow]


class ForecastPoint(BaseModel):
    year: int
    forecast_deaths: float | None = None
    forecast_deaths_lo: float | None = None
    forecast_deaths_hi: float | None = None
    yhat: float | None = None
    yhat_lo: float | None = None
    yhat_hi: float | None = None


class ForecastMetadata(BaseModel):
    model_name: str | None = None
    train_start_year: int | None = None
    train_end_year: int | None = None
    mae: float | None = None
    mape: float | None = None
    interval_coverage: float | None = None


class ForecastResponse(ForecastMetadata):
    forecast: list[ForecastPoint]
    history_anoms: list[dict[str, Any]] = Field(default_factory=list)
    evaluation: dict[str, Any] | None = None


class ForecastEvaluationResponse(BaseModel):
    by_state: list[dict[str, Any]]
    aggregate: dict[str, Any]


class AnomalyPoint(BaseModel):
    year: int
    deaths: float
    diff: float | None = None
    z: float
    is_anomaly: bool


class AnomaliesResponse(BaseModel):
    rows: list[AnomalyPoint]
    window: int
    z_threshold: float


class HotspotsResponse(BaseModel):
    year: int | None = None
    clusters: list[dict[str, Any]]


class SimulatorResponse(BaseModel):
    state: str
    assumptions: dict[str, Any]
    projection: list[dict[str, Any]]


class RiskScoreResponse(BaseModel):
    risk_probability: float
    coefficients: dict[str, float]
    contributions: dict[str, float]
