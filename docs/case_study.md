# Portfolio Case Study

## Problem
Public health teams need a state-level view of opioid overdose burden with transparent data quality and forecast confidence.

## Approach
- Built ETL to standardize CDC-style overdose data into a state-year analytical table.
- Added FastAPI endpoints for metrics, forecast, anomalies, and quality status.
- Added data contract checks and exported quality evidence as static JSON artifacts.
- Benchmarked naive last-value forecasting against SARIMAX using rolling backtests and selected the lower-MAE model.

## Key Findings
- Latest-year overdose burden varies across states; the dashboard highlights top-rate states and trend direction.
- Rolling backtests show where naive is sufficient and where SARIMAX improves error.
- Quality checks make schema and completeness expectations explicit and auditable.

## Limits
- Forecasts are state-level and historical-only; no exogenous predictors are included.
- Sparse series reduce model reliability for some states.
- Static demo mode trades real-time updates for reproducibility and lower hosting cost.

## Policy and Product Implications
- Use forecasts for directional planning and triage, not individual-level decisions.
- Validate quality status before sharing stakeholder outputs.
- Next production step is monitored retraining and quality-regression alerting.
