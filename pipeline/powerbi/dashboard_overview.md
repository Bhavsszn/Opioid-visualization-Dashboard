# Power BI Analytics Dashboard

This dashboard is the Business Intelligence layer of the Opioid Visualization project.

It analyzes overdose trends across U.S. states using data processed by the project pipeline.

## Key Metrics

- Total deaths
- Deaths per 100k population
- Average overdose rate
- Year-over-year change

## Visualizations

- Overdose death trend over time
- Highest risk states
- Population vs overdose correlation
- Decomposition tree for state/year exploration

## Data Source

The dashboard uses the curated dataset produced by the project data pipeline.

Pipeline flow:

CDC Overdose Data
→ Backend data processing
→ Cleaned dataset
→ Fabric Lakehouse table
→ Power BI semantic model
→ Power BI dashboard
