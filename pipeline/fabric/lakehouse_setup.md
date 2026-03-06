# Microsoft Fabric Lakehouse Setup

This document describes how the opioid overdose dataset is stored and managed in Microsoft Fabric.

## Lakehouse Overview

The project uses a Fabric Lakehouse to store the curated overdose dataset.

Lakehouse Name:
opioid

Schema:
dbo

Primary Table:
gold_state_year

---

## Table Structure

Table: gold_state_year

Columns:

year  
state  
population  
deaths  
crude_rate  
age_adjusted_rate  

Each row represents overdose statistics for a specific state and year.

Example:

State: Alabama  
Year: 2020  
Deaths: 1203  
Population: 4921532

---

## Data Flow

CDC Overdose Data  
↓  
Python Data Processing  
↓  
Cleaned Dataset  
↓  
Fabric Lakehouse Table (gold_state_year)

---

## Why Fabric Lakehouse

Using a Lakehouse provides:

• scalable storage for analytical data  
• compatibility with Power BI Direct Lake  
• simplified integration with data pipelines  
• centralized analytics dataset
