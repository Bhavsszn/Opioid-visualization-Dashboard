
# Data Model Plan

This document outlines the data modeling strategy used for the opioid overdose analytics dashboard.

---

# Dataset Overview

The primary dataset contains annual overdose statistics for U.S. states.

Table:

gold_state_year

Columns:

year  
state  
population  
deaths  
crude_rate  
age_adjusted_rate  

Each record represents:

state + year combination

---

# Data Model Design

The model follows a simplified star schema approach.

Fact Table

gold_state_year

Measures derived from this table include:

• Total Deaths  
• Total Population  
• Deaths per 100k  
• Average Overdose Rate  
• YoY Death Change  
• YoY Percentage Change  

---

# Analytics Goals

The model supports the following analytics tasks:

## Trend Analysis
Visualizing overdose death trends over time.

Example visual:

Line chart

year → deaths

---

## Geographic Risk Analysis

Identifying states with the highest overdose rates.

Example visual:

Bar chart

state → average overdose rate

---

## Population Impact Analysis

Understanding how population size correlates with overdose deaths.

Example visual:

Scatter plot

population vs deaths per 100k

---

## KPI Monitoring

High-level indicators displayed in dashboard cards.

• Total deaths  
• Death rate per 100k  
• Average overdose rate  
• YoY change

---

# Microsoft Fabric Integration

The dataset is stored in a Fabric Lakehouse table:

dbo.gold_state_year

Power BI connects using:

Direct Lake mode

Benefits:

• real-time querying  
• no data import duplication  
• scalable analytics performance

---

# Dashboard Purpose

The dashboard provides a high-level view of the opioid overdose crisis across the United States.

It allows analysts and policymakers to:

• monitor trends over time  
• identify high-risk states  
• evaluate population-adjusted mortality rates  
• analyze year-over-year changes
