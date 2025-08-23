# backend/etl.py
import os, io, sqlite3, sys, re, json
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# --- Config / Paths ---
DATA_DIR   = os.getenv("DATA_DIR", "../data")
DB_PATH    = os.getenv("DB_PATH",  os.path.join(DATA_DIR, "opioid.db"))
# Prefer the user's shared CSV; fall back to data/
DEFAULT_CSV_NAME = "Underlying Cause of Death, 2018-2023, Single Race.csv"
CSV_PATHS = [
    os.path.join("..", "user_shared", DEFAULT_CSV_NAME),
    os.path.join(DATA_DIR, DEFAULT_CSV_NAME),
    os.path.join(DATA_DIR, "overdoses_state_year_clean_typed.csv"),
]
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")  # optional

os.makedirs(DATA_DIR, exist_ok=True)

# --- Helpers ---
def _to_num(s):
    if pd.isna(s): return np.nan
    s = str(s)
    # remove non-numeric chars except . and - (handles "1,234", "12.3 (CI)", "Suppressed")
    s = re.sub(r"[^0-9\.\-]", "", s)
    try:
        return float(s) if s != "" else np.nan
    except:
        return np.nan

def find_csv():
    for p in CSV_PATHS:
        if os.path.exists(p):
            print(f"[ETL] Using CSV: {p}")
            return p
    raise FileNotFoundError(
        "Could not find a CDC WONDER CSV.\n"
        "Expected at one of:\n  - ../user_shared/Underlying Cause of Death, 2018-2023, Single Race.csv\n"
        "  - ../data/Underlying Cause of Death, 2018-2023, Single Race.csv\n"
        "  - ../data/overdoses_state_year_clean_typed.csv\n"
        "If your file is elsewhere, set WONDER_CSV=... in backend/.env or move the file."
    )

def load_wonder_csv(path: str) -> pd.DataFrame:
    df_raw = pd.read_csv(path, low_memory=False)
    # CDC WONDER exports often have notes/header/footer rows. Keep rows that look like data.
    # Try to detect data columns in a flexible way.
    cols = {c.lower().strip(): c for c in df_raw.columns}
    # map common column names
    col_year  = next((cols[c] for c in cols if c in ("year",)), None)
    col_state = next((cols[c] for c in cols if c in ("state",)), None)
    # deaths column (avoid "Percent of Total Deaths")
    col_deaths = None
    for c in df_raw.columns:
        cl = c.lower()
        if "deaths" in cl and "percent" not in cl:
            col_deaths = c; break
    # population
    col_pop = next((c for c in df_raw.columns if c.lower().startswith("population")), None)
    # crude rate
    col_cr = next((c for c in df_raw.columns if c.lower().startswith("crude rate")), None)
    # age-adjusted rate
    col_aar = next((c for c in df_raw.columns if "age" in c.lower() and "adjust" in c.lower() and "rate" in c.lower()), None)

    required = [col_year, col_state, col_deaths]
    if any(c is None for c in required):
        raise ValueError(
            f"CSV does not have expected columns. Found: {list(df_raw.columns)}\n"
            "Need at least Year, State, and a 'Deaths' column."
        )

    df = df_raw[[col_year, col_state] + [c for c in [col_deaths, col_pop, col_cr, col_aar] if c]].copy()
    df.columns = ["year", "state"] + [n for n in ["deaths", "population", "crude_rate", "age_adjusted_rate"] if
                                      (n == "deaths" and col_deaths) or
                                      (n == "population" and col_pop) or
                                      (n == "crude_rate" and col_cr) or
                                      (n == "age_adjusted_rate" and col_aar)]

    # Clean numerics
    for c in ("deaths", "population", "crude_rate", "age_adjusted_rate"):
        if c in df.columns:
            df[c] = df[c].apply(_to_num)

    # Year must be int-like
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["year", "state", "deaths"]).copy()
    df["year"] = df["year"].astype(int)

    # Remove aggregate rows if present
    df = df[~df["state"].astype(str).str.contains("United States", case=False, na=False)]
    df = df.reset_index(drop=True)

    # Save a cleaned copy for reference
    out_csv = os.path.join(DATA_DIR, "overdoses_state_year_clean_typed.csv")
    df.to_csv(out_csv, index=False)
    print(f"[ETL] Cleaned CSV saved -> {out_csv}")
    return df

def maybe_fetch_acs(year: int) -> pd.DataFrame | None:
    """Optional ACS enrichment: population, poverty %, uninsured %, median income.
       Continues silently if anything fails."""
    if not CENSUS_API_KEY:
        print("[ETL] CENSUS_API_KEY not set; skipping ACS enrichment.")
        return None

    import requests
    def get(get_str, dataset):
        try:
            url = f"https://api.census.gov/data/{year}/{dataset}"
            params = {"get": get_str, "for": "state:*", "key": CENSUS_API_KEY}
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
            try:
                rows = r.json()
            except Exception:
                print("[ACS] Non-JSON response. Skipping.")
                return None
            if not rows or not isinstance(rows, list) or not rows[0]:
                print("[ACS] Empty payload. Skipping.")
                return None
            return pd.DataFrame(rows[1:], columns=rows[0])
        except Exception as e:
            print(f"[ACS] Request failed: {e}. Skipping.")
            return None

    pop = get("NAME,B01003_001E", "acs/acs1")
    if pop is None:
        return None
    pop = pop.rename(columns={"B01003_001E": "acs_population"})

    pov = get("NAME,B17001_002E,B17001_001E", "acs/acs1")
    ins = get("NAME,S2701_C05_001E", "acs/acs1/subject")
    inc = get("NAME,B19013_001E", "acs/acs1")

    out = pop[["state", "NAME", "acs_population"]].copy()
    out["state_fips"] = out["state"].astype(str).str.zfill(2)
    out = out.drop(columns=["state"]).rename(columns={"NAME": "state_name"})
    out["acs_population"] = pd.to_numeric(out["acs_population"], errors="coerce")

    if pov is not None:
        pov["pct_poverty"] = (
            pd.to_numeric(pov["B17001_002E"], errors="coerce") /
            pd.to_numeric(pov["B17001_001E"], errors="coerce")
        ) * 100
        out = out.merge(pov[["state", "pct_poverty"]], left_on="state_fips", right_on="state", how="left").drop(columns=["state"])

    if ins is not None and "S2701_C05_001E" in ins.columns:
        ins = ins.rename(columns={"S2701_C05_001E": "pct_uninsured"})
        out = out.merge(ins[["state", "pct_uninsured"]], left_on="state_fips", right_on="state", how="left").drop(columns=["state"])

    if inc is not None:
        inc = inc.rename(columns={"B19013_001E": "median_household_income"})
        out = out.merge(inc[["state", "median_household_income"]], left_on="state_fips", right_on="state", how="left").drop(columns=["state"])

    print(f"[ETL] ACS rows: {len(out)}")
    return out

def write_db(df_over: pd.DataFrame, df_acs: pd.DataFrame | None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS state_year_overdoses")
    df_over.to_sql("state_year_overdoses", conn, index=False)
    if df_acs is not None:
        cur.execute("DROP TABLE IF EXISTS acs_state_features")
        df_acs.to_sql("acs_state_features", conn, index=False)
        cur.execute("DROP VIEW IF EXISTS vw_state_year_features")
        cur.execute("""
            CREATE VIEW vw_state_year_features AS
            SELECT o.year, o.state, o.deaths, o.population, o.crude_rate, o.age_adjusted_rate,
                   a.state_fips, a.state_name, a.acs_population, a.pct_poverty, a.pct_uninsured, a.median_household_income
            FROM state_year_overdoses o
            LEFT JOIN acs_state_features a
              ON a.state_name = o.state
        """)
    conn.commit()
    conn.close()
    print(f"[ETL] SQLite refreshed -> {DB_PATH}")

def write_frontend_json(df_over: pd.DataFrame):
    # Useful for the minimal static front-end if you use it
    js_path = os.path.join(DATA_DIR, "..", "frontend_min", "overdoses_state_year.json")
    try:
        os.makedirs(os.path.dirname(js_path), exist_ok=True)
        with open(js_path, "w", encoding="utf-8") as f:
            f.write(df_over.to_json(orient="records"))
        print(f"[ETL] Frontend JSON -> {js_path}")
    except Exception as e:
        print(f"[ETL] Skipped JSON write: {e}")

def main():
    csv_path = os.getenv("WONDER_CSV") or find_csv()
    df_over = load_wonder_csv(csv_path)

    # Use the last year in your CSV for ACS (optional).
    latest_year = int(df_over["year"].max())
    df_acs = maybe_fetch_acs(latest_year)

    write_db(df_over, df_acs)
    write_frontend_json(df_over)
    print("[ETL] Done.")

if __name__ == "__main__":
    main()
