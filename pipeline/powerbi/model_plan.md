# Data Model Plan

This document outlines the data modeling strategy used for the opioid overdose analytics dashboard.

## Dataset overview

The primary analytical dataset is:
- `gold_state_year`

Each row represents a unique `state + year` observation.

Columns:
- `year`
- `state`
- `population`
- `deaths`
- `crude_rate`
- `age_adjusted_rate`

## Modeling approach

The project uses a simplified fact-style analytical table in Power BI backed by Fabric Direct Lake.

This model supports:
- trend analysis over time
- state comparison
- KPI cards
- scatter analysis
- decomposition tree exploration

## Analytics goals

### Trend analysis
Visualize overdose deaths over time.

### Geographic / state risk analysis
Compare states by overdose burden.

### Population impact analysis
Explore how population size relates to overdose rates.

### KPI monitoring
Track total deaths, normalized rates, and YoY changes.

## Fabric integration

The dataset is stored in:
- Fabric Lakehouse table `dbo.gold_state_year`

Power BI connects using:
- Direct Lake mode

## Downstream output

The model powers the enterprise BI dashboard documented in `dashboard_overview.md`.
