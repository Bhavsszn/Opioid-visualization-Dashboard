# Power BI Semantic Model

This document explains the semantic model used by the Power BI dashboard.

The semantic model sits on top of the Fabric Lakehouse dataset.

Lakehouse Table:
gold_state_year

---

# Model Structure

The dataset is modeled as a single fact table containing yearly overdose statistics.

Fact Table

gold_state_year

Dimensions

state  
year

Measures

Total Deaths  
Total Population  
Deaths per 100k  
Average Overdose Rate  
YoY Death Change  
YoY Percentage Change

---

# Key Measures

Total Deaths

SUM(gold_state_year[deaths])

---

Deaths per 100k

DIVIDE([Total Deaths], [Total Population]) * 100000

---

YoY Percentage Change

DIVIDE(
    [YoY Death Change],
    [PrevYearDeaths]
)

---

# Semantic Layer Purpose

The semantic model enables:

• KPI monitoring  
• trend analysis over time  
• state-level overdose comparisons  
• year-over-year change analysis

The model is consumed by the Power BI dashboard.

---

# Connection Mode

Power BI connects to the dataset using:

Direct Lake Mode

Benefits:

• no data duplication  
• real-time queries  
• improved performance
