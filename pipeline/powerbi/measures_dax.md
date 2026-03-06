# Power BI Measures (DAX)

This document describes the main DAX measures used in the opioid overdose analytics dashboard.

## Total Deaths

Calculates the total number of overdose deaths in the current filter context.

```DAX
Total Deaths =
SUM(gold_state_year[deaths])
```

## Total Population

Aggregates the total population in the current filter context.

```DAX
Total Population =
SUM(gold_state_year[population])
```

## Deaths per 100k

Normalizes deaths relative to population size.

```DAX
Deaths per 100k =
DIVIDE([Total Deaths], [Total Population]) * 100000
```

## Average Overdose Rate

Uses the age-adjusted rate field to summarize overdose burden.

```DAX
Average Overdose Rate =
AVERAGE(gold_state_year[age_adjusted_rate])
```

## YoY Death Change

Compares the selected year to the previous year.

```DAX
YoY Death Change =
VAR SelectedYear = SELECTEDVALUE(gold_state_year[year])
VAR CurrYearDeaths =
    CALCULATE(
        [Total Deaths],
        FILTER(ALL(gold_state_year), gold_state_year[year] = SelectedYear)
    )
VAR PrevYearDeaths =
    CALCULATE(
        [Total Deaths],
        FILTER(ALL(gold_state_year), gold_state_year[year] = SelectedYear - 1)
    )
RETURN
IF(
    ISBLANK(SelectedYear) || ISBLANK(PrevYearDeaths),
    BLANK(),
    CurrYearDeaths - PrevYearDeaths
)
```

## YoY % Change

Calculates the percentage change relative to the previous year.

```DAX
YoY % Change =
VAR SelectedYear = SELECTEDVALUE(gold_state_year[year])
VAR CurrYearDeaths =
    CALCULATE(
        [Total Deaths],
        FILTER(ALL(gold_state_year), gold_state_year[year] = SelectedYear)
    )
VAR PrevYearDeaths =
    CALCULATE(
        [Total Deaths],
        FILTER(ALL(gold_state_year), gold_state_year[year] = SelectedYear - 1)
    )
RETURN
IF(
    ISBLANK(SelectedYear) || ISBLANK(PrevYearDeaths),
    BLANK(),
    DIVIDE(CurrYearDeaths - PrevYearDeaths, PrevYearDeaths)
)
```

## Notes

These measures support:
- KPI cards
- state risk ranking
- population correlation analysis
- decomposition tree exploration
- year-over-year monitoring
