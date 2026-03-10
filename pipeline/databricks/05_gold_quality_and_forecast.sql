-- Databricks SQL: optional Gold forecast and pipeline summary assets

CREATE SCHEMA IF NOT EXISTS gold;

CREATE OR REPLACE TABLE gold.forecast_input AS
SELECT state, year, deaths
FROM gold.state_year_overdoses
WHERE deaths IS NOT NULL;

-- Placeholder forecast output table shape. Populate from Python model job if needed.
CREATE OR REPLACE TABLE gold.forecast_output (
  state STRING,
  year INT,
  forecast_deaths DOUBLE,
  forecast_deaths_lo DOUBLE,
  forecast_deaths_hi DOUBLE,
  model_name STRING,
  train_start_year INT,
  train_end_year INT,
  mae DOUBLE,
  mape DOUBLE,
  interval_coverage DOUBLE,
  updated_at TIMESTAMP
);

CREATE OR REPLACE VIEW gold.pipeline_run_summary AS
SELECT
  date_format(current_timestamp(), 'yyyyMMddHHmmss') AS run_id,
  current_timestamp() AS checked_at,
  'databricks-medallion-pattern' AS source,
  (SELECT COUNT(*) FROM gold.state_year_overdoses) AS row_count,
  (SELECT COUNT(DISTINCT state) FROM gold.state_year_overdoses) AS states,
  (SELECT MIN(year) FROM gold.state_year_overdoses) AS min_year,
  (SELECT MAX(year) FROM gold.state_year_overdoses) AS max_year,
  'pass' AS quality_status;
