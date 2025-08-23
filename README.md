# Opioid Overdose Dashboard (Static Demo)

A data visualization project that makes the U.S. opioid overdose crisis easier to understand, explore, and communicate.  

This dashboard is designed as a portfolio piece to showcase skills in data engineering, analysis, and visualization, while also serving as a public-facing demo of how analytics tools can make complex public health data more approachable.

## Purpose

The opioid epidemic is one of the most pressing public health challenges in the United States. While a wealth of raw data is available from agencies like the CDC and Census Bureau, it is often locked in spreadsheets or databases that are difficult for the public, policymakers, or community organizations to digest.

This project transforms that data into an interactive dashboard that:

- Shows historical trends in overdose deaths and rates by state.  
- Lets users compare states via a color-coded U.S. map.  
- Provides a forecasting view that demonstrates how data science methods can anticipate future challenges.  
- Explains in plain language how each metric is calculated, making the analysis accessible to non-technical audiences.  

For portfolio purposes, the dashboard also highlights strong technical skills:
- ETL pipeline: converting raw CSV/SQLite data into structured JSON for the frontend.  
- Frontend engineering: React, TypeScript, Vite, Tailwind, Recharts, and mapping libraries.  
- API design: ability to connect to a FastAPI backend (future extension).  
- Deployment: building a static, free-to-host demo on Vercel or Netlify.  

## Usefulness

- Public health professionals & policymakers: Quickly see which states are most affected and how trends evolve over time.  
- General public: Understand complex data through simple charts, maps, and explanations.  
- Portfolio demo: Demonstrates ability to integrate data analysis, machine learning (forecasting), and modern web development into a coherent project.  
- Educational tool: Explains epidemiological metrics (rates per 100k, crude rates, population adjustments) in plain English.  

## Tech Stack

- Frontend: React + Vite + TypeScript, styled with TailwindCSS.  
- Charts: Recharts (time series, line charts, tables).  
- Maps: react-simple-maps (U.S. choropleth).  
- Backend (optional): FastAPI + SQLite (for live API & SARIMAX forecasts).  
- Static demo mode: SQLite data exported to JSON via `export_static.py`.  
- Hosting: deployable as a free static site on Vercel, Netlify, or GitHub Pages.  

## Project Structure

```
frontend/
  public/api/           # ← JSON data exported here
  src/
    components/         # Shared UI components (Footer, Nav, Explainer)
    pages/              # Overview, Map, Forecast
    lib/api.ts          # Handles static JSON vs live API
    App.tsx             # Routing + layout
backend/
  export_static.py      # Export SQLite data → JSON
data/
  opioid.db             # SQLite database (example dataset)
```

## Running the Project

### 1. Export data from SQLite → JSON

```cmd
cd backend
.\.venv\Scriptsctivate
set DB_PATH=..\data\opioid.db
python export_static.py
```

### 2. Build and preview locally

```cmd
cd ../frontend
set VITE_USE_STATIC=true
npm install --legacy-peer-deps
npm run build
npx serve -s dist -l 4173
```

Open: http://localhost:4173

### 3. Deploy

- Vercel (recommended):  
  ```cmd
  npx vercel login
  npx vercel deploy --prebuilt --prod
  ```
- Netlify: drag and drop the `frontend/dist/` folder.

## Features

### Overview
- Line chart: overdose rate (per 100k) + total deaths over time.  
- Quick stats: latest year, deaths, overdose rate.  
- Top-10 states table (latest year).  
- Full state-by-state time series.  
- Plain-language explanation of how metrics are calculated.  

### Map
- Color-coded U.S. map of overdose rates (latest year).  
- Legend for interpreting risk levels.  
- Explainer on how the map is computed.  

### Forecast
- Simple +2% per year linear projection (static demo).  
- Uncertainty band: ±10% to illustrate range of possible outcomes.  
- Explanation of formula used and how a real SARIMAX model would replace it in production.  

## Sources

- CDC WONDER — Multiple Cause of Death (Opioid Overdose): https://wonder.cdc.gov/mcd.html  
- U.S. Census Bureau — State Population Estimates: https://www.census.gov/data.html  

Both datasets are public domain (U.S. federal government works).

## Copyright & License

- Code copyright:  
  © 2025 Bhavya Sharma. All rights reserved.  
  This project is shared for portfolio/demo purposes.  
  Redistribution or commercial use is not permitted without permission.  

- package.json:  
  ```json
  { "license": "UNLICENSED" }
  ```

- Third-party libraries: React, Tailwind, Recharts, react-simple-maps, etc. — MIT-licensed.  
- Data: CDC WONDER + Census (public domain, attribution included).  

## Future Work

- Connect to live FastAPI backend for dynamic data.  
- Replace static projection with SARIMAX or other time-series models.  
- Add county-level drill-downs for finer granularity.  
- Expand with socioeconomic & prescription data for richer context.  
