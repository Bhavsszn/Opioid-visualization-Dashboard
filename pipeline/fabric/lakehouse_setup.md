# Microsoft Fabric Lakehouse Setup

This document describes how the opioid overdose dataset is stored and managed in Microsoft Fabric.

## Lakehouse overview

The project uses a Fabric Lakehouse to store the curated overdose dataset.

- **Lakehouse name:** `opioid`
- **Schema:** `dbo`
- **Primary table:** `gold_state_year`

## Table structure

Table: `gold_state_year`

Columns:
- `year`
- `state`
- `population`
- `deaths`
- `crude_rate`
- `age_adjusted_rate`

Each row represents a unique `state + year` combination.

## Data flow

```text
CDC Overdose Data
↓
Python / Databricks data processing
↓
Curated dataset
↓
Fabric Lakehouse table (dbo.gold_state_year)
```

## Why Fabric Lakehouse

Using a Lakehouse provides:
- centralized analytical storage
- compatibility with Power BI Direct Lake
- simpler integration with downstream BI workflows
- a clean handoff point between engineering and reporting
