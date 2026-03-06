# Databricks Data Pipeline

This folder contains the Databricks ETL pipeline used to process opioid overdose data.

The pipeline follows a medallion architecture:

```text
Bronze → Silver → Gold → Publish to OneLake / Fabric
```

## Pipeline stages

### 1. Bronze layer — raw ingestion
**File:** `01_bronze_ingest.py`

Purpose:
- ingest the raw overdose dataset
- preserve source-level fidelity
- store minimally transformed records

Output:
- `bronze_overdose_raw`

### 2. Silver layer — cleaning and standardization
**File:** `02_silver_clean.py`

Purpose:
- remove obvious null / malformed values
- standardize data types
- normalize year and state fields
- prepare the dataset for downstream analytics

Output:
- `silver_overdose_clean`

### 3. Gold layer — BI-ready aggregates
**File:** `03_gold_aggregates.py`

Purpose:
- create analytics-ready state/year aggregates
- support Fabric and Power BI consumption
- produce a stable schema for dashboards

Output:
- `gold_state_year`

Core columns:
- `year`
- `state`
- `population`
- `deaths`
- `crude_rate`
- `age_adjusted_rate`

### 4. Publish to OneLake / Fabric
**File:** `04_publish_to_onelake.py`

Purpose:
- publish the Gold dataset to OneLake / Fabric
- make the curated table available to the Power BI semantic model

Final destination:
- Fabric Lakehouse table: `dbo.gold_state_year`

## End-to-end data flow

```text
CDC Overdose Data
↓
Databricks Bronze Layer
↓
Databricks Silver Layer
↓
Databricks Gold Layer
↓
Microsoft Fabric Lakehouse
↓
Power BI Semantic Model
↓
Power BI Dashboard
```
