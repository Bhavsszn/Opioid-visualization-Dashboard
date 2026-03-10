# PostgreSQL Local Setup (Current Working Contract)

This runbook codifies the current working local stack:
- FastAPI backend
- PostgreSQL serving schema (`analytics`)
- React + Vite frontend

## 1. Backend env

Create `backend/.env` from `backend/.env.example` and set real DB credentials.

Minimum required:

```env
DB_BACKEND=postgres
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require
POSTGRES_SCHEMA=analytics
ENABLE_SQLITE_FALLBACK=false
ENABLE_STATIC_FALLBACK=false
ALLOWED_CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

## 2. Frontend env

Create `frontend/.env` from `frontend/.env.example`.

```env
VITE_API_BASE=http://127.0.0.1:8000
VITE_USE_STATIC=false
VITE_API_TO_STATIC_FALLBACK=false
```

## 3. Initialize serving schema

Run once (or re-run safely):

```bash
python -m pip install -r backend/requirements.txt
python - <<'PY'
import os, psycopg
from pathlib import Path
root = Path.cwd()
sql = (root / "pipeline" / "postgres" / "analytics_schema.sql").read_text(encoding="utf-8")
dsn = os.environ.get("DATABASE_URL")
if not dsn:
    raise SystemExit("Set DATABASE_URL in env first.")
with psycopg.connect(dsn, autocommit=True) as conn:
    conn.execute(sql)
print("analytics schema applied")
PY
```

## 4. Populate/refresh serving tables

Populate all required serving tables from local source CSV:

```bash
python scripts/populate_postgres_serving_tables.py
```

Refresh only `states_latest`:

```bash
python scripts/refresh_states_latest.py
```

Refresh only `pipeline_run_summary`:

```bash
python scripts/refresh_pipeline_run_summary.py
```

## 5. Start backend

```bash
cd backend
python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

Startup logs should print backend/schema/fallback flags and DB connectivity.

## 6. Start frontend

```bash
cd frontend
npm install
npm run dev
```

## 7. Quick checks

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/metrics/states-latest
curl http://127.0.0.1:8000/api/pipeline
```

## Notes for later Databricks integration

The local populate script is intentionally structured as a replaceable publish step.
Later flow can switch from local CSV input to:

`Databricks Gold -> PostgreSQL analytics.* tables`

without changing frontend/backend API contracts.
