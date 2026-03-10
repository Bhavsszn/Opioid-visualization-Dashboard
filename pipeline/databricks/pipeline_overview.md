# Databricks Medallion Pipeline

This pipeline implements:

Raw source files
-> `bronze.overdose_raw`
-> `silver.overdose_clean`
-> `gold.state_year_overdoses`
-> `gold.states_latest`
-> `gold.quality_report`
-> optional `gold.forecast_input` and `gold.forecast_output`

## Jobs order

1. `01_bronze_ingest.py`
2. `02_silver_clean.py`
3. `03_gold_aggregates.py`
4. `05_gold_quality_and_forecast.sql` (optional)
5. `04_publish_to_onelake.py`
6. `scripts/sync_databricks_to_postgres.py`

## Serving contract columns

- `state`
- `year`
- `deaths`
- `population`
- `crude_rate`
- `age_adjusted_rate`
