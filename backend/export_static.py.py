# backend/export_static.py
import os, json, sqlite3, pathlib

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "opioid.db"))
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "api")
pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)

def dump_json(name, obj):
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 1) Health (for quick sanity check)
dump_json("health.json", {"ok": True, "db_exists": os.path.exists(DB_PATH)})

# 2) List of states your UI uses (normalize to match the app)
rows = c.execute("SELECT DISTINCT state FROM metrics ORDER BY state").fetchall()
states = [r[0] for r in rows]
dump_json("states.json", states)

# 3) State-Year metrics for all states (adjust query to match your schema)
# Expecting columns like: state, year, deaths, prescriptions, etc.
metrics = {}
for s in states:
    mrows = c.execute("""
        SELECT year, deaths, prescriptions, overdose_rate, population
        FROM metrics
        WHERE state = ?
        ORDER BY year
    """, (s,)).fetchall()
    metrics[s] = [
        {
            "year": r[0],
            "deaths": r[1],
            "prescriptions": r[2],
            "overdose_rate": r[3],
            "population": r[4],
        } for r in mrows
    ]
dump_json("metrics_state_year.json", metrics)

# 4) Forecasts for each state (if you had a forecast table or generate a simple baseline)
# If you *already* compute forecasts at runtime with statsmodels, replace this with your logic
# or store your precomputed results into the DB and read them here.
forecasts = {}
for s in states:
    # Example: naive projection from last 3 years (replace with your real forecast logic or table)
    hist = metrics.get(s, [])
    last = hist[-1] if hist else None
    if last:
        y0 = last["year"]
        base = last["overdose_rate"] or 0
        f = [{"year": y0 + i, "overdose_rate": round(base * (1 + 0.02*i), 2)} for i in range(1, 6)]
    else:
        f = []
    forecasts[s] = f
dump_json("forecast_by_state.json", forecasts)

conn.close()
print(f"Static API exported to: {OUT_DIR}")
