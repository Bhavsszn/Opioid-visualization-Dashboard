from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tools.sm_exceptions import ConvergenceWarning


@dataclass
class BacktestPoint:
    year: int
    actual: float
    naive_pred: float
    sarimax_pred: float
    sarimax_lo: float
    sarimax_hi: float


def _mae(actual: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean(np.abs(actual - pred))) if len(actual) else 0.0


def _mape(actual: np.ndarray, pred: np.ndarray) -> float:
    denom = np.where(actual == 0, np.nan, actual)
    vals = np.abs((actual - pred) / denom)
    vals = vals[~np.isnan(vals)]
    return float(np.mean(vals) * 100.0) if len(vals) else 0.0


def _coverage(actual: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> float:
    return float(np.mean((actual >= lo) & (actual <= hi))) if len(actual) else 0.0


def _safe_sarimax_forecast(train: pd.Series) -> tuple[float, float, float]:
    last = float(train.iloc[-1])
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", category=FutureWarning)
            warnings.filterwarnings("ignore", category=ConvergenceWarning)
            model = SARIMAX(train, order=(1, 1, 1), enforce_stationarity=False, enforce_invertibility=False)
            res = model.fit(disp=False)
            fc = res.get_forecast(steps=1)
        yhat = float(fc.predicted_mean.iloc[0])
        lo, hi = fc.conf_int(alpha=0.2).iloc[0].tolist()
        return yhat, float(lo), float(hi)
    except Exception:
        return last, max(0.0, last - 100.0), last + 100.0


def evaluate_state(df_state: pd.DataFrame, min_train_years: int = 4) -> dict[str, Any]:
    df_state = df_state.sort_values("year")
    y = df_state["deaths"].astype(float).reset_index(drop=True)
    years = df_state["year"].astype(int).tolist()

    if len(y) < min_train_years + 1:
        return {
            "state": str(df_state["state"].iloc[0]),
            "points": len(y),
            "selected_model": "naive_last",
            "mae": None,
            "mape": None,
            "interval_coverage": None,
            "train_start_year": int(years[0]) if years else None,
            "train_end_year": int(years[-1]) if years else None,
            "backtest_points": [],
        }

    rows: list[BacktestPoint] = []
    for split_idx in range(min_train_years, len(y)):
        train = y.iloc[:split_idx]
        actual = float(y.iloc[split_idx])
        naive = float(train.iloc[-1])
        sarimax_pred, sarimax_lo, sarimax_hi = _safe_sarimax_forecast(train)
        rows.append(
            BacktestPoint(
                year=int(years[split_idx]),
                actual=actual,
                naive_pred=naive,
                sarimax_pred=sarimax_pred,
                sarimax_lo=sarimax_lo,
                sarimax_hi=sarimax_hi,
            )
        )

    actual_arr = np.array([r.actual for r in rows], dtype=float)
    naive_arr = np.array([r.naive_pred for r in rows], dtype=float)
    sar_arr = np.array([r.sarimax_pred for r in rows], dtype=float)
    sar_lo = np.array([r.sarimax_lo for r in rows], dtype=float)
    sar_hi = np.array([r.sarimax_hi for r in rows], dtype=float)

    naive_mae = _mae(actual_arr, naive_arr)
    sar_mae = _mae(actual_arr, sar_arr)

    if sar_mae <= naive_mae:
        selected = "sarimax"
        selected_pred = sar_arr
    else:
        selected = "naive_last"
        selected_pred = naive_arr

    return {
        "state": str(df_state["state"].iloc[0]),
        "points": len(y),
        "selected_model": selected,
        "mae": round(float(_mae(actual_arr, selected_pred)), 4),
        "mape": round(float(_mape(actual_arr, selected_pred)), 4),
        "interval_coverage": round(float(_coverage(actual_arr, sar_lo, sar_hi)), 4),
        "train_start_year": int(years[0]),
        "train_end_year": int(years[-2]),
        "backtest_points": [r.__dict__ for r in rows],
        "benchmark": {
            "naive_last": {
                "mae": round(float(naive_mae), 4),
                "mape": round(float(_mape(actual_arr, naive_arr)), 4),
            },
            "sarimax": {
                "mae": round(float(sar_mae), 4),
                "mape": round(float(_mape(actual_arr, sar_arr)), 4),
            },
        },
    }


def evaluate_all_states(df: pd.DataFrame) -> dict[str, Any]:
    rows = []
    for state, group in df.groupby("state"):
        g = group[["state", "year", "deaths"]].dropna()
        if g.empty:
            continue
        rows.append(evaluate_state(g))

    with_metrics = [r for r in rows if r.get("mae") is not None]
    aggregate = {
        "states_evaluated": len(rows),
        "states_with_metrics": len(with_metrics),
        "mae": round(float(np.mean([r["mae"] for r in with_metrics])), 4) if with_metrics else None,
        "mape": round(float(np.mean([r["mape"] for r in with_metrics])), 4) if with_metrics else None,
        "interval_coverage": round(float(np.mean([r["interval_coverage"] for r in with_metrics])), 4)
        if with_metrics
        else None,
    }
    return {"by_state": rows, "aggregate": aggregate}


def forecast_state(df_state: pd.DataFrame, horizon: int = 3) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    df_state = df_state.sort_values("year")
    y = df_state["deaths"].astype(float)
    years = df_state["year"].astype(int)
    evaluation = evaluate_state(df_state)
    model_name = evaluation["selected_model"]

    if model_name == "sarimax":
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                warnings.filterwarnings("ignore", category=FutureWarning)
                warnings.filterwarnings("ignore", category=ConvergenceWarning)
                model = SARIMAX(y, order=(1, 1, 1), enforce_stationarity=False, enforce_invertibility=False)
                res = model.fit(disp=False)
                fc = res.get_forecast(steps=horizon)
            preds = fc.predicted_mean.tolist()
            ci = fc.conf_int(alpha=0.2).values.tolist()
        except Exception:
            model_name = "naive_last"
            last = float(y.iloc[-1])
            preds = [last] * horizon
            ci = [[max(0.0, last - 100.0), last + 100.0]] * horizon
    else:
        last = float(y.iloc[-1])
        preds = [last] * horizon
        ci = [[max(0.0, last - 100.0), last + 100.0]] * horizon

    last_year = int(years.iloc[-1])
    out = []
    for i in range(horizon):
        pred = float(preds[i])
        lo = float(ci[i][0])
        hi = float(ci[i][1])
        out.append(
            {
                "year": last_year + i + 1,
                "forecast_deaths": pred,
                "forecast_deaths_lo": lo,
                "forecast_deaths_hi": hi,
                "yhat": pred,
                "yhat_lo": lo,
                "yhat_hi": hi,
            }
        )

    metadata = {
        "model_name": model_name,
        "train_start_year": int(years.iloc[0]),
        "train_end_year": int(years.iloc[-1]),
        "mae": evaluation.get("mae"),
        "mape": evaluation.get("mape"),
        "interval_coverage": evaluation.get("interval_coverage"),
    }
    return out, metadata
