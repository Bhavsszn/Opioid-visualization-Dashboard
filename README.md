# Opioid Analytics Portfolio Project

This project demonstrates a full analytics lifecycle for opioid overdose data: data ingestion and cleaning, quality contracts, forecasting with benchmark evaluation, API delivery, and stakeholder dashboards (React and Power BI/Fabric).

## 60-second value statement
- Built an end-to-end analytics system that turns raw public-health records into decision-ready state-year insights.
- Added explicit quality contracts with machine-readable pass/fail reporting.
- Added forecast credibility evidence via rolling backtests (naive vs SARIMAX) with model-selection metadata.
- Delivered both a product-style React dashboard and enterprise BI artifacts (Databricks + Fabric + Power BI).

## Architecture

```text
CDC / Public Health Data
  -> Python ETL (cleaning + typing)
  -> SQLite analytical table (state_year_overdoses)
  -> Quality contracts + forecast evaluation artifacts
  -> FastAPI endpoints / static JSON export
  -> React dashboard and Power BI semantic model
```

## Repository structure

```text
backend/               FastAPI API, ETL, quality + forecast modules
frontend/              React + Vite dashboard
pipeline/databricks/   Bronze -> Silver -> Gold ETL scripts
pipeline/fabric/       Lakehouse and semantic model documentation
pipeline/powerbi/      DAX, model notes, dashboard documentation
scripts/               Local/CI runner scripts
artifacts/             Versioned portfolio evidence snapshots
docs/                  Case study and milestone docs
```

## Quick start

### One command run (backend + frontend)

```bash
python run.py
```

This runs ETL + static export, then starts FastAPI and the React dev server.
If ETL cannot hydrate SQLite, it automatically falls back to static JSON mode so charts still render.

### 1. Install dependencies

```bash
cd frontend
npm install
cd ../backend
python -m pip install -r requirements.txt
```

### 2. Export static API + artifacts

```bash
cd backend
python export_static.py
```

This generates static data in `frontend/public/api/` including:
- `quality_report.json`
- `forecast_evaluation.json`
- `forecast_by_state.json`

And a versioned artifact snapshot in `artifacts/portfolio_analysis_snapshot.json`.

### 3. Run app (frontend + backend)

```bash
python scripts/run_demo.py
```

## One-command reproducibility run

For local validation and CI-style checks:

```bash
python scripts/run_portfolio_pipeline.py
```

It runs ETL, static export, backend tests, quality validation, and frontend build.

## What I would ship next in production
- Add monitoring and alerting for data-quality regressions.
- Add model retraining schedule and model registry versioning.
- Add richer feature set for forecasting (policy and socioeconomic covariates).

## Design tradeoffs
- Static export vs live API: static mode improves reproducibility and low-cost hosting; live mode improves freshness.
- Model simplicity vs interpretability: benchmark + SARIMAX is transparent and explainable; more complex models may reduce interpretability.
- Fast portfolio iteration vs full MLOps: current setup prioritizes evidence and clarity; production would add orchestration and observability.

## Additional docs
- Case study: `docs/case_study.md`
- Milestones: `docs/milestones.md`
- Power BI and Fabric notes: `pipeline/`

## Power BI on the webpage
Set this in `frontend/.env` to embed your published Power BI report at `/powerbi`:

```bash
VITE_POWERBI_EMBED_URL=https://app.powerbi.com/view?r=YOUR_EMBED_URL
```

## Databricks showcase on the webpage
Open `/pipeline` in the app to view the medallion flow, stage outputs, and generated run evidence from `pipeline_run_summary.json`.
