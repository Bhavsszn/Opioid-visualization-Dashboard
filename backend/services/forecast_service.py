"""Forecasting and evaluation services."""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
import pandas as pd
from fastapi import HTTPException
from sklearn.linear_model import LogisticRegression

from forecast_eval import evaluate_all_states, forecast_state
from repositories.forecast_repository import ForecastRepository
from repositories.metrics_repository import MetricsRepository
from services.metrics_service import load_state_year_df
from settings import settings
from utils.validation import normalize_state

metrics_repo = MetricsRepository()
forecast_repo = ForecastRepository()


def _build_history_anoms(df: pd.DataFrame) -> list[dict]:
    frame = df.copy()
    frame["diff"] = frame["deaths"].diff()
    std = frame["diff"].std(ddof=0)
    z = (frame["diff"] - frame["diff"].mean()) / std if std else pd.Series([0] * len(frame))
    return [
        {
            "year": int(frame["year"].iloc[idx]),
            "deaths": int(frame["deaths"].iloc[idx]),
            "z": float(z.iloc[idx] if not math.isnan(z.iloc[idx]) else 0),
        }
        for idx in range(len(frame))
    ]


def _try_precomputed_forecast(state: str, horizon: int) -> dict | None:
    try:
        rows = forecast_repo.fetch_forecast_output(state)
    except Exception:
        return None

    if not rows:
        return None

    selected = rows[:horizon]
    out = []
    for row in selected:
        pred = row.get("forecast_deaths")
        lo = row.get("forecast_deaths_lo")
        hi = row.get("forecast_deaths_hi")
        out.append(
            {
                "year": int(row["year"]),
                "forecast_deaths": pred,
                "forecast_deaths_lo": lo,
                "forecast_deaths_hi": hi,
                "yhat": pred,
                "yhat_lo": lo,
                "yhat_hi": hi,
            }
        )

    return {
        "forecast": out,
        "history_anoms": [],
        "model_name": "precomputed_gold",
        "train_start_year": None,
        "train_end_year": None,
        "mae": None,
        "mape": None,
        "interval_coverage": None,
        "evaluation": None,
    }


@lru_cache(maxsize=128)
def _cached_forecast(state: str, horizon: int) -> dict:
    precomputed = _try_precomputed_forecast(state=state, horizon=horizon)
    if precomputed is not None:
        return precomputed

    rows = metrics_repo.fetch_state_deaths_history(state)
    if not rows:
        raise HTTPException(status_code=404, detail="No data")

    df = pd.DataFrame(rows)
    series_df = df.assign(state=state)[["state", "year", "deaths"]]
    forecast_rows, metadata = forecast_state(series_df, horizon=horizon)

    return {
        "forecast": forecast_rows,
        "history_anoms": _build_history_anoms(df),
        "model_name": metadata["model_name"],
        "train_start_year": metadata["train_start_year"],
        "train_end_year": metadata["train_end_year"],
        "mae": metadata["mae"],
        "mape": metadata["mape"],
        "interval_coverage": metadata["interval_coverage"],
        "evaluation": metadata,
    }


def get_forecast_evaluation() -> dict:
    """Return benchmark comparison across states."""
    df = load_state_year_df()
    if df.empty:
        raise HTTPException(status_code=404, detail="No data")

    return evaluate_all_states(df[["year", "state", "deaths"]].dropna())


def get_forecast_simple(state: str, horizon: int = settings.default_forecast_horizon) -> dict:
    """Return forecast payload with metadata and backward-compatible aliases."""
    if horizon < 1 or horizon > 20:
        raise HTTPException(status_code=422, detail="horizon must be between 1 and 20")

    normalized_state = normalize_state(state)
    if not normalized_state:
        raise HTTPException(status_code=422, detail="state is required")

    return _cached_forecast(normalized_state, horizon)


def get_forecast_sarimax(state: str, horizon: int = settings.default_forecast_horizon) -> dict:
    payload = get_forecast_simple(state=state, horizon=horizon)
    if payload.get("model_name") == "sarimax":
        payload["model_name"] = "sarimax"
    return payload


def run_simulator_whatif(
    state: str,
    rx_reduction_pct: float = 0.0,
    mat_increase_pct: float = 0.0,
    naloxone_coverage_pct: float = 0.0,
    horizon: int = settings.default_forecast_horizon,
) -> dict:
    rows = metrics_repo.fetch_state_deaths_history(normalize_state(state) or "")
    if not rows:
        raise HTTPException(status_code=404, detail="No data")

    last = int(rows[-1]["deaths"])
    last_year = int(rows[-1]["year"])
    elasticities = {"rx": -0.20, "mat": -0.15, "naloxone": -0.08}
    adjusted = 1.0
    adjusted += (rx_reduction_pct / 100.0) * elasticities["rx"]
    adjusted += (mat_increase_pct / 100.0) * elasticities["mat"]
    adjusted += (naloxone_coverage_pct / 100.0) * elasticities["naloxone"]
    yhat = max(0, int(round(last * adjusted)))

    return {
        "state": state,
        "assumptions": {
            "rx_reduction_pct": rx_reduction_pct,
            "mat_increase_pct": mat_increase_pct,
            "naloxone_coverage_pct": naloxone_coverage_pct,
            "elasticities": elasticities,
        },
        "projection": [{"year": last_year + i, "yhat": yhat} for i in range(1, horizon + 1)],
    }


def run_risk_score(age: int, prior_overdose: int, high_mme: int, polysubstance: int, mental_dx: int, male: int) -> dict:
    np.random.seed(42)
    n_samples = 3000
    x_df = pd.DataFrame(
        {
            "age": np.random.normal(42, 12, n_samples).clip(15, 90).round(),
            "prior_overdose": np.random.binomial(1, 0.12, n_samples),
            "high_mme": np.random.binomial(1, 0.18, n_samples),
            "polysubstance": np.random.binomial(1, 0.22, n_samples),
            "mental_dx": np.random.binomial(1, 0.28, n_samples),
            "male": np.random.binomial(1, 0.52, n_samples),
        }
    )

    beta = np.array([-0.01, 1.6, 1.1, 0.9, 0.6, 0.2])
    logits = x_df[["age", "prior_overdose", "high_mme", "polysubstance", "mental_dx", "male"]].values @ beta - 6.0
    probability = 1 / (1 + np.exp(-logits))
    y = np.random.binomial(1, probability)

    model = LogisticRegression(max_iter=1000).fit(x_df, y)

    x_user = pd.DataFrame(
        [
            {
                "age": age,
                "prior_overdose": prior_overdose,
                "high_mme": high_mme,
                "polysubstance": polysubstance,
                "mental_dx": mental_dx,
                "male": male,
            }
        ]
    )

    risk_probability = float(model.predict_proba(x_user)[0, 1])
    coefficients = dict(zip(x_df.columns.tolist(), model.coef_[0].round(3)))
    contribution = {key: float(x_user.iloc[0][key] * coefficients[key]) for key in coefficients}

    return {
        "risk_probability": risk_probability,
        "coefficients": coefficients,
        "contributions": contribution,
    }
