-- PostgreSQL serving schema for FastAPI analytics application.
-- This contract is derived from backend repositories/services currently used in runtime.
-- Required read paths:
--   analytics.state_year_overdoses
--   analytics.states_latest
--   analytics.quality_report
--   analytics.pipeline_run_summary
--   analytics.forecast_output (optional precomputed forecast)

CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.state_year_overdoses (
  state TEXT NOT NULL,
  year INT NOT NULL,
  deaths DOUBLE PRECISION,
  population DOUBLE PRECISION,
  crude_rate DOUBLE PRECISION,
  age_adjusted_rate DOUBLE PRECISION,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT pk_state_year_overdoses PRIMARY KEY (state, year)
);

CREATE INDEX IF NOT EXISTS idx_state_year_overdoses_year ON analytics.state_year_overdoses (year);
CREATE INDEX IF NOT EXISTS idx_state_year_overdoses_state ON analytics.state_year_overdoses (state);

CREATE TABLE IF NOT EXISTS analytics.states_latest (
  state TEXT NOT NULL,
  year INT NOT NULL,
  deaths DOUBLE PRECISION,
  population DOUBLE PRECISION,
  crude_rate DOUBLE PRECISION,
  age_adjusted_rate DOUBLE PRECISION,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT pk_states_latest PRIMARY KEY (state, year)
);

CREATE INDEX IF NOT EXISTS idx_states_latest_rate ON analytics.states_latest (crude_rate DESC);

CREATE TABLE IF NOT EXISTS analytics.quality_report (
  checked_at TIMESTAMPTZ NOT NULL,
  check_name TEXT NOT NULL,
  status TEXT NOT NULL,
  value_json JSONB,
  threshold_json JSONB,
  detail TEXT,
  CONSTRAINT pk_quality_report PRIMARY KEY (checked_at, check_name)
);

CREATE INDEX IF NOT EXISTS idx_quality_report_checked_at ON analytics.quality_report (checked_at DESC);

CREATE TABLE IF NOT EXISTS analytics.pipeline_run_summary (
  run_id TEXT PRIMARY KEY,
  checked_at TIMESTAMPTZ NOT NULL,
  source TEXT NOT NULL,
  row_count INT NOT NULL,
  states INT NOT NULL,
  min_year INT,
  max_year INT,
  quality_status TEXT,
  stages_json JSONB,
  databricks_assets_json JSONB
);

CREATE INDEX IF NOT EXISTS idx_pipeline_run_summary_checked_at ON analytics.pipeline_run_summary (checked_at DESC);

CREATE TABLE IF NOT EXISTS analytics.forecast_output (
  state TEXT NOT NULL,
  year INT NOT NULL,
  forecast_deaths DOUBLE PRECISION,
  forecast_deaths_lo DOUBLE PRECISION,
  forecast_deaths_hi DOUBLE PRECISION,
  model_name TEXT,
  train_start_year INT,
  train_end_year INT,
  mae DOUBLE PRECISION,
  mape DOUBLE PRECISION,
  interval_coverage DOUBLE PRECISION,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT pk_forecast_output PRIMARY KEY (state, year)
);

CREATE INDEX IF NOT EXISTS idx_forecast_output_state ON analytics.forecast_output (state);
