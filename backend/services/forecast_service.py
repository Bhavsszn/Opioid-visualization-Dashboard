"""Forecasting, evaluation, and demo ML scenario services."""

import math

import numpy as np
import pandas as pd
from fastapi import HTTPException
from sklearn.linear_model import LogisticRegression

from db import query
from forecast_eval import evaluate_all_states, forecast_state
from settings import settings
from services.metrics_service import load_state_year_df


def get_forecast_evaluation() -> dict:
    df = load_state_year_df()
    if df.empty:
        raise HTTPException(404, "No data")
    return evaluate_all_states(df[["year", "state", "deaths"]].dropna())


def get_forecast_simple(state: str, horizon: int = settings.default_forecast_horizon) -> dict:
    rows = query("SELECT year, deaths FROM state_year_overdoses WHERE state=? ORDER BY year", (state,))
    if not rows:
        raise HTTPException(404, "No data")

    df = pd.DataFrame(rows)
    series_df = df.assign(state=state)[["state", "year", "deaths"]]
    forecast_rows, metadata = forecast_state(series_df, horizon=horizon)

    df["diff"] = df["deaths"].diff()
    std = df["diff"].std(ddof=0)
    z = (df["diff"] - df["diff"].mean()) / std if std else pd.Series([0] * len(df))
    hist = [
        {
            "year": int(df["year"].iloc[i]),
            "deaths": int(df["deaths"].iloc[i]),
            "z": float(z.iloc[i] if not math.isnan(z.iloc[i]) else 0),
        }
        for i in range(len(df))
    ]

    return {
        "forecast": forecast_rows,
        "history_anoms": hist,
        "model_name": metadata["model_name"],
        "train_start_year": metadata["train_start_year"],
        "train_end_year": metadata["train_end_year"],
        "mae": metadata["mae"],
        "mape": metadata["mape"],
        "interval_coverage": metadata["interval_coverage"],
        "evaluation": metadata,
    }


def get_forecast_sarimax(state: str, horizon: int = settings.default_forecast_horizon) -> dict:
    payload = get_forecast_simple(state=state, horizon=horizon)
    payload["model_name"] = "sarimax" if payload.get("model_name") == "sarimax" else payload.get("model_name")
    return payload


def run_simulator_whatif(
    state: str,
    rx_reduction_pct: float = 0.0,
    mat_increase_pct: float = 0.0,
    naloxone_coverage_pct: float = 0.0,
    horizon: int = settings.default_forecast_horizon,
) -> dict:
    base = query("SELECT year, deaths FROM state_year_overdoses WHERE state=? ORDER BY year", (state,))
    if not base:
        raise HTTPException(404, "No data")
    last = int(base[-1]["deaths"])
    last_year = int(base[-1]["year"])
    rx_elast = -0.20
    mat_elast = -0.15
    nalox_elast = -0.08
    adj_factor = (
        1.0
        + (rx_reduction_pct / 100.0) * rx_elast
        + (mat_increase_pct / 100.0) * mat_elast
        + (naloxone_coverage_pct / 100.0) * nalox_elast
    )
    yhat = max(0, int(round(last * adj_factor)))
    out = [{"year": last_year + i, "yhat": yhat} for i in range(1, horizon + 1)]
    return {
        "state": state,
        "assumptions": {
            "rx_reduction_pct": rx_reduction_pct,
            "mat_increase_pct": mat_increase_pct,
            "naloxone_coverage_pct": naloxone_coverage_pct,
            "elasticities": {"rx": rx_elast, "mat": mat_elast, "naloxone": nalox_elast},
        },
        "projection": out,
    }


def run_risk_score(age: int, prior_overdose: int, high_mme: int, polysubstance: int, mental_dx: int, male: int) -> dict:
    np.random.seed(42)
    n = 3000
    x_df = pd.DataFrame(
        {
            "age": np.random.normal(42, 12, n).clip(15, 90).round(),
            "prior_overdose": np.random.binomial(1, 0.12, n),
            "high_mme": np.random.binomial(1, 0.18, n),
            "polysubstance": np.random.binomial(1, 0.22, n),
            "mental_dx": np.random.binomial(1, 0.28, n),
            "male": np.random.binomial(1, 0.52, n),
        }
    )
    beta = np.array([-0.01, 1.6, 1.1, 0.9, 0.6, 0.2])
    logits = (
        x_df.assign(const=1)[["age", "prior_overdose", "high_mme", "polysubstance", "mental_dx", "male"]].values
        @ beta
    ) - 6.0
    p = 1 / (1 + np.exp(-logits))
    y = np.random.binomial(1, p)
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
    prob = float(model.predict_proba(x_user)[0, 1])
    coef = dict(zip(x_df.columns.tolist(), model.coef_[0].round(3)))
    x_vals = x_user.iloc[0].to_dict()
    contrib = {k: float(x_vals[k] * coef[k]) for k in coef.keys()}
    return {"risk_probability": prob, "coefficients": coef, "contributions": contrib}
