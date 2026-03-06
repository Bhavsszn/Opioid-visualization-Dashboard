import json
import os
import pathlib
import sqlite3
from typing import Any

import pandas as pd

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DB_PATH = os.environ.get("DB_PATH", os.path.join(ROOT, "data", "opioid.db"))
CSV_PATH = os.environ.get(
    "CSV_PATH", os.path.join(ROOT, "data", "overdoses_state_year_clean_typed.csv")
)
OUT_DIR = os.environ.get(
    "STATIC_OUT_DIR", os.path.join(ROOT, "frontend", "public", "api")
)
pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)


def dump_json(filename: str, obj: Any) -> None:
    out_path = os.path.join(OUT_DIR, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _safe_float(value: Any) -> float | None:
    if pd.isna(value):
        return None
    return float(value)


def load_dataframe() -> tuple[pd.DataFrame, str]:
    """Load curated state/year data from SQLite if available, otherwise CSV."""
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        try:
            df = pd.read_sql_query(
                """
                SELECT year, state, population, deaths, crude_rate, age_adjusted_rate
                FROM state_year_overdoses
                ORDER BY year, state
                """,
                conn,
            )
            return df, f"sqlite:{DB_PATH}"
        finally:
            conn.close()

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        needed = ["year", "state", "population", "deaths", "crude_rate", "age_adjusted_rate"]
        missing = [c for c in needed if c not in df.columns]
        if missing:
            raise ValueError(f"CSV is missing required columns: {missing}")
        df = df[needed].copy()
        return df, f"csv:{CSV_PATH}"

    raise FileNotFoundError(
        f"Could not find either SQLite database at {DB_PATH} or CSV at {CSV_PATH}."
    )


def build_static_payloads(df: pd.DataFrame) -> None:
    df["year"] = df["year"].astype(int)
    for col in ["population", "deaths", "crude_rate", "age_adjusted_rate"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    states = sorted(df["state"].dropna().unique().tolist())
    dump_json("states.json", states)

    metrics_by_state: dict[str, list[dict[str, Any]]] = {}
    for state in states:
        subset = df[df["state"] == state].sort_values("year")
        metrics_by_state[state] = [
            {
                "year": int(row["year"]),
                "deaths": _safe_float(row["deaths"]),
                "population": _safe_float(row["population"]),
                "crude_rate": _safe_float(row["crude_rate"]),
                "overdose_rate": _safe_float(row["crude_rate"]),
                "age_adjusted_rate": _safe_float(row["age_adjusted_rate"]),
            }
            for _, row in subset.iterrows()
        ]
    dump_json("metrics_state_year.json", metrics_by_state)

    latest_year = int(df["year"].max())
    latest = (
        df[df["year"] == latest_year]
        .sort_values("crude_rate", ascending=False)
        .reset_index(drop=True)
    )
    states_latest = [
        {
            "state": row["state"],
            "year": int(row["year"]),
            "population": _safe_float(row["population"]),
            "deaths": _safe_float(row["deaths"]),
            "crude_rate": _safe_float(row["crude_rate"]),
            "overdose_rate": _safe_float(row["crude_rate"]),
            "age_adjusted_rate": _safe_float(row["age_adjusted_rate"]),
        }
        for _, row in latest.iterrows()
    ]
    dump_json("states_latest.json", states_latest)

    forecasts: dict[str, list[dict[str, Any]]] = {}
    for state, rows in metrics_by_state.items():
        if not rows:
            forecasts[state] = []
            continue
        last = rows[-1]
        base = last.get("overdose_rate") or last.get("age_adjusted_rate") or 0
        year0 = int(last["year"])
        forecasts[state] = [
            {
                "year": year0 + i,
                "overdose_rate": round(float(base) * (1 + 0.02 * i), 2),
            }
            for i in range(1, 6)
        ]
    dump_json("forecast_by_state.json", forecasts)


def main() -> None:
    df, source = load_dataframe()
    build_static_payloads(df)
    dump_json(
        "health.json",
        {
            "ok": True,
            "source": source,
            "rows": int(len(df)),
            "latest_year": int(df["year"].max()),
        },
    )
    print(f"Exported static API files to: {OUT_DIR}")
    print(f"Source: {source}")


if __name__ == "__main__":
    main()
