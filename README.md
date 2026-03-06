# Opioid Visualization Dashboard

An end-to-end opioid overdose analytics project that combines a public-facing React dashboard with an enterprise BI analytics layer built with Databricks, Microsoft Fabric, and Power BI.

## What this project includes

This repository now has **two visualization layers** built on the same curated overdose dataset:

### 1. React dashboard
A web-based interactive dashboard for public-facing exploration of state-by-state overdose trends.

### 2. Power BI / Fabric dashboard
An enterprise BI version of the project built on top of a Fabric Lakehouse and Direct Lake semantic model.

## Architecture

```text
CDC / Public Health Data
        ↓
Python ETL / Backend Processing
        ↓
Curated Dataset (SQLite / CSV)
        ↓
┌────────────────────────────┬────────────────────────────┐
│ React Frontend Dashboard   │ Fabric Lakehouse          │
│ Public-facing visualization│ Enterprise BI data layer  │
└────────────────────────────┴────────────────────────────┘
                                      ↓
                               Power BI Semantic Model
                                      ↓
                               Power BI Dashboard
```

## Repository structure

```text
backend/               FastAPI backend, ETL helpers, static export
frontend/              React + Vite dashboard
pipeline/databricks/   Bronze → Silver → Gold ETL pipeline
pipeline/fabric/       Lakehouse and semantic model documentation
pipeline/powerbi/      DAX, model notes, dashboard documentation
scripts/               Local runner scripts
```

## Quick start (local demo)

### 1. Install dependencies

```bash
cd frontend
npm install
cd ../backend
python -m pip install -r requirements.txt
```

### 2. Export static API files

```bash
cd backend
python export_static.py
```

This generates:

- `frontend/public/api/states.json`
- `frontend/public/api/states_latest.json`
- `frontend/public/api/metrics_state_year.json`
- `frontend/public/api/forecast_by_state.json`

### 3. Run the React app

```bash
cd ../frontend
npm run dev
```

## Analytics layers

### React dashboard
The React dashboard is the public demo layer. It reads from static JSON exported by the backend or from the live FastAPI API.

### Databricks pipeline
The Databricks pipeline implements a medallion architecture:

- Bronze: raw ingestion
- Silver: cleaning and standardization
- Gold: analytics-ready aggregates
- Publish: send curated output to Fabric / OneLake

### Microsoft Fabric + Power BI
The Fabric / Power BI layer uses the curated dataset in a Lakehouse table (`gold_state_year`) and exposes it to Power BI through a Direct Lake semantic model.

## Why this project is stronger now

This repo demonstrates:

- Python data processing
- FastAPI backend development
- React frontend visualization
- Databricks medallion pipeline design
- Microsoft Fabric data modeling
- Power BI dashboarding and DAX

## Notes

- The local demo is the easiest version to run.
- The Databricks / Fabric / Power BI assets are documented in `pipeline/`.
- The Power BI dashboard is the enterprise BI extension of the original React project, not a separate unrelated dashboard.
