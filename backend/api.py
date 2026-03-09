import math
import os
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression

from forecast_eval import evaluate_all_states, forecast_state
from quality import build_quality_report

load_dotenv()
DATA_DIR = os.getenv("DATA_DIR", "../data")
DB_PATH = os.getenv("DB_PATH", os.path.join(DATA_DIR, "opioid.db"))
ROOT = Path(__file__).resolve().parents[1]
STATIC_API_DIR = Path(os.getenv("STATIC_OUT_DIR", str(ROOT / "frontend" / "public" / "api")))

app = FastAPI(title="Opioid AI Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def q(sql: str, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _load_state_year_df() -> pd.DataFrame:
    rows = q(
        """
        SELECT year, state, deaths, population, crude_rate, age_adjusted_rate
        FROM state_year_overdoses
        ORDER BY year, state
        """
    )
    if not rows:
        return pd.DataFrame(columns=["year", "state", "deaths", "population", "crude_rate", "age_adjusted_rate"])
    return pd.DataFrame(rows)


def _build_pipeline_summary(df: pd.DataFrame, quality_status: str, checked_at: str) -> dict:
    return {
        "run_id": checked_at.replace(":", "").replace("-", ""),
        "checked_at": checked_at,
        "source": "databricks-medallion-pattern",
        "row_count": int(len(df)),
        "states": int(df["state"].nunique()) if not df.empty else 0,
        "years": {
            "min": int(df["year"].min()) if not df.empty else 0,
            "max": int(df["year"].max()) if not df.empty else 0,
        },
        "quality_status": quality_status,
        "stages": [
            {
                "name": "Bronze",
                "purpose": "Ingest raw opioid source records with minimal transformation.",
                "output": "opioid.bronze_raw",
                "script": "pipeline/databricks/01_bronze_ingest.py",
            },
            {
                "name": "Silver",
                "purpose": "Clean and standardize types, column names, and quality edge cases.",
                "output": "opioid.silver_clean",
                "script": "pipeline/databricks/02_silver_clean.py",
            },
            {
                "name": "Gold",
                "purpose": "Produce analytics-ready state-year and latest-state aggregates.",
                "output": "opioid.gold_state_year / opioid.gold_state_latest",
                "script": "pipeline/databricks/03_gold_aggregates.py",
            },
            {
                "name": "Publish",
                "purpose": "Export curated Gold outputs to OneLake/Fabric for BI consumption.",
                "output": "OneLake parquet folders",
                "script": "pipeline/databricks/04_publish_to_onelake.py",
            },
        ],
        "databricks_assets": [
            "pipeline/databricks/01_bronze_ingest.py",
            "pipeline/databricks/02_silver_clean.py",
            "pipeline/databricks/03_gold_aggregates.py",
            "pipeline/databricks/04_publish_to_onelake.py",
            "pipeline/databricks/pipeline_overview.md",
        ],
    }


@app.get("/health")
def health():
    return {"ok": True, "db_exists": os.path.exists(DB_PATH)}


@app.get("/api/quality/status")
def quality_status():
    report_path = STATIC_API_DIR / "quality_report.json"
    if report_path.exists():
        import json

        return json.loads(report_path.read_text(encoding="utf-8"))

    df = _load_state_year_df()
    if df.empty:
        raise HTTPException(404, "No data")
    return build_quality_report(df)


@app.get("/api/pipeline/run-summary")
def pipeline_run_summary():
    report_path = STATIC_API_DIR / "pipeline_run_summary.json"
    if report_path.exists():
        import json

        return json.loads(report_path.read_text(encoding="utf-8"))

    df = _load_state_year_df()
    if df.empty:
        raise HTTPException(404, "No data")
    q_report = build_quality_report(df)
    return _build_pipeline_summary(df, q_report["status"], q_report["checked_at"])


@app.get("/api/metrics/state-year")
def state_year(state: str | None = None, year: int | None = None):
    sql = "SELECT * FROM state_year_overdoses WHERE 1=1"
    params = []
    if state:
        sql += " AND state=?"
        params.append(state)
    if year:
        sql += " AND year=?"
        params.append(year)
    sql += " ORDER BY year, state"
    return {"rows": q(sql, tuple(params))}


@app.get("/api/metrics/states-latest")
def states_latest(year: int | None = None):
    if year is None:
        y = q("SELECT MAX(year) AS y FROM state_year_overdoses")[0]["y"]
        year = int(y)
    rows = q("SELECT * FROM state_year_overdoses WHERE year=? ORDER BY crude_rate DESC", (year,))
    return {"year": year, "rows": rows}


@app.get("/api/forecast/evaluation")
def forecast_evaluation():
    df = _load_state_year_df()
    if df.empty:
        raise HTTPException(404, "No data")
    return evaluate_all_states(df[["year", "state", "deaths"]].dropna())


@app.get("/api/forecast/simple")
def forecast_simple(state: str, horizon: int = 3):
    rows = q("SELECT year, deaths FROM state_year_overdoses WHERE state=? ORDER BY year", (state,))
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


@app.get("/api/forecast/sarimax")
def forecast_sarimax(state: str, horizon: int = 3):
    payload = forecast_simple(state=state, horizon=horizon)
    payload["model_name"] = "sarimax" if payload.get("model_name") == "sarimax" else payload.get("model_name")
    return payload


@app.get("/api/anomalies")
def anomalies(state: str, window: int = 3, z_threshold: float = 2.0):
    rows = q("SELECT year, deaths FROM state_year_overdoses WHERE state=? ORDER BY year", (state,))
    if not rows:
        raise HTTPException(404, "No data")
    df = pd.DataFrame(rows)
    df["diff"] = df["deaths"].diff()
    roll = df["diff"].rolling(window=window, min_periods=window).mean()
    std = df["diff"].rolling(window=window, min_periods=window).std()
    z = (df["diff"] - roll) / std
    df["z"] = z
    df["is_anomaly"] = (df["z"].abs() >= z_threshold).fillna(False)
    return {"rows": df.fillna(0).to_dict(orient="records"), "window": window, "z_threshold": z_threshold}


@app.get("/api/hotspots/kmeans")
def hotspots_kmeans(k: int = 3, year: int | None = None):
    latest = states_latest(year)
    df = pd.DataFrame(latest["rows"])
    if df.empty or "crude_rate" not in df.columns:
        return {"clusters": []}
    x_vals = df[["crude_rate"]].fillna(0.0).values
    k = max(1, min(k, len(df)))
    km = KMeans(n_clusters=k, n_init="auto", random_state=42).fit(x_vals)
    df["cluster"] = km.labels_
    order = df.groupby("cluster")["crude_rate"].mean().sort_values(ascending=False).index.tolist()
    rank_map = {c: i + 1 for i, c in enumerate(order)}
    df["cluster_rank"] = df["cluster"].map(rank_map)
    df = df.sort_values(["cluster_rank", "crude_rate"], ascending=[True, False])
    return {"year": latest["year"], "clusters": df.to_dict(orient="records")}


@app.post("/api/simulator/whatif")
def simulator_whatif(
    state: str,
    rx_reduction_pct: float = 0.0,
    mat_increase_pct: float = 0.0,
    naloxone_coverage_pct: float = 0.0,
    horizon: int = 3,
):
    base = q("SELECT year, deaths FROM state_year_overdoses WHERE state=? ORDER BY year", (state,))
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


@app.post("/api/risk/score")
def risk_score(age: int, prior_overdose: int, high_mme: int, polysubstance: int, mental_dx: int, male: int):
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
