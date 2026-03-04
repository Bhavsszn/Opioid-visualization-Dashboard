# backend/export_static.py
import os
import json
import sqlite3
import pathlib

HERE = os.path.dirname(__file__)
DB_PATH = os.environ.get("DB_PATH", os.path.join(HERE, "..", "data", "opioid.db"))

# Default: write into the React app's public folder
OUT_DIR = os.environ.get(
    "STATIC_OUT_DIR",
    os.path.join(HERE, "..", "frontend", "public", "api")
)
pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)


def dump_json(filename: str, obj):
    out_path = os.path.join(OUT_DIR, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def main():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"DB not found at: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    dump_json("health.json", {"ok": True, "db_path": DB_PATH})

    # States
    rows = c.execute("SELECT DISTINCT state FROM metrics ORDER BY state").fetchall()
    states = [r[0] for r in rows]
    dump_json("states.json", states)

    # State-year metrics
    metrics = {}
    for s in states:
        mrows = c.execute(
            """
            SELECT year, deaths, prescriptions, overdose_rate, population
            FROM metrics
            WHERE state = ?
            ORDER BY year
            """,
            (s,),
        ).fetchall()

        metrics[s] = [
            {
                "year": int(r[0]),
                "deaths": float(r[1]) if r[1] is not None else None,
                "prescriptions": float(r[2]) if r[2] is not None else None,
                "overdose_rate": float(r[3]) if r[3] is not None else None,
                "population": float(r[4]) if r[4] is not None else None,
            }
            for r in mrows
        ]

    dump_json("metrics_state_year.json", metrics)

    # Simple forecast placeholder (kept lightweight for static demo)
    forecasts = {}
    for s in states:
        hist = metrics.get(s, [])
        last = hist[-1] if hist else None
        if last and last.get("overdose_rate") is not None:
            y0 = last["year"]
            base = float(last["overdose_rate"])
            forecasts[s] = [
                {"year": y0 + i, "overdose_rate": round(base * (1 + 0.02 * i), 2)}
                for i in range(1, 6)
            ]
        else:
            forecasts[s] = []

    dump_json("forecast_by_state.json", forecasts)

    conn.close()
    print(f"✅ Static API exported to: {OUT_DIR}")


if __name__ == "__main__":
    main()
