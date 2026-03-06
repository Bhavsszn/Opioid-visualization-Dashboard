# Power BI Analytics Dashboard

This dashboard is the enterprise BI layer of the Opioid Visualization project.

It analyzes opioid overdose trends across U.S. states using data produced by the project pipeline.

## Key metrics

- Total deaths
- Deaths per 100k population
- Average overdose rate
- Year-over-year change

## Visualizations

- KPI cards
- Overdose death trend over time
- Highest risk states
- Population vs overdose death rate scatter plot
- Decomposition tree for state/year drill-down

## Data source

The dashboard uses the curated dataset produced upstream by the project pipeline.

```text
CDC Overdose Data
→ Backend / Databricks processing
→ Curated dataset
→ Fabric Lakehouse table
→ Power BI semantic model
→ Power BI dashboard
```

## Purpose

The React dashboard in this repository is the public-facing visualization layer.
The Power BI dashboard is the enterprise reporting layer focused on KPI monitoring, trend analysis, and stakeholder reporting.
