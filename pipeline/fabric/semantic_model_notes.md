# Power BI Semantic Model Notes

This document explains the semantic model used by the Power BI dashboard.

The semantic model sits on top of the Fabric Lakehouse dataset and uses `dbo.gold_state_year` as the main fact-style table.

## Model structure

### Base table
- `gold_state_year`

### Core fields
- `year`
- `state`
- `population`
- `deaths`
- `crude_rate`
- `age_adjusted_rate`

### Key measures
- `Total Deaths`
- `Total Population`
- `Deaths per 100k`
- `Average Overdose Rate`
- `YoY Death Change`
- `YoY % Change`

## Semantic layer purpose

The semantic model enables:
- KPI monitoring
- trend analysis over time
- state-level overdose comparison
- year-over-year change analysis
- decomposition tree exploration

## Connection mode

Power BI connects to Fabric using **Direct Lake**.

Benefits:
- no separate imported data copy
- lower duplication of storage
- tighter integration with the Lakehouse
- fast report development on curated tables

## Downstream consumer

The semantic model is consumed by the Power BI dashboard documented in `pipeline/powerbi/`.
