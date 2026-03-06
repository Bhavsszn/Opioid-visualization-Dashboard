# Power BI Measures (DAX)

This document describes the key DAX measures used in the opioid overdose analytics dashboard.

The dataset contains state-level overdose statistics including deaths, population, crude death rate, and age-adjusted death rate.

---

## Total Deaths

Calculates the total number of overdose deaths within the current filter context.

```DAX
Total Deaths =
SUM(gold_state_year[deaths])
Total Population

Aggregates the total population for the selected states and years.

Total Population =
SUM(gold_state_year[population])
Deaths per 100k

Normalizes deaths relative to population size.

Deaths per 100k =
DIVIDE(
    [Total Deaths],
    [Total Population]
) * 100000
Average Overdose Rate

Average of the age-adjusted overdose rate across selected states.

Average Overdose Rate =
AVERAGE(gold_state_year[age_adjusted_rate])
Previous Year Deaths

Calculates deaths for the previous year within the current filter context.

PrevYearDeaths =
CALCULATE(
    [Total Deaths],
    FILTER(
        ALL(gold_state_year[year]),
        gold_state_year[year] = MAX(gold_state_year[year]) - 1
    )
)
Year-over-Year Death Change

Difference in deaths between current year and previous year.

YoY Death Change =
[Total Deaths] - [PrevYearDeaths]
YoY Percentage Change

Measures the percentage increase or decrease in overdose deaths compared to the previous year.

YoY % Change =
DIVIDE(
    [YoY Death Change],
    [PrevYearDeaths]
)
Notes

The measures were designed to support:

• KPI cards
• state-level comparison
• trend analysis
• decomposition tree exploration
• population vs overdose correlation analysis

All measures operate dynamically based on the filter context applied in the Power BI report.
