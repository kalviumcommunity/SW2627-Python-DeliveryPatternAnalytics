# Delivery Pattern Analytics Platform

## Dataset Profiling & Quality Assessment

### Overview

This assignment implements the **Dataset Profiling & Quality Assessment** module for the Delivery Pattern Analytics Platform.

The purpose of this module is to understand the quality of the dataset before any cleaning, transformation, or analysis is performed.

The profiling process measures completeness, uniqueness, numerical statistics, value distributions, and potential quality issues.

The profiling step **does not modify or clean the data**. Instead, it produces a structured report that can be used to make informed data-cleaning decisions later.

---

## Objectives

The profiling module is designed to:

- Calculate null counts and null percentages for every column.
- Identify exact duplicate records.
- Calculate duplicate percentages.
- Generate numerical statistics.
- Profile categorical value distributions.
- Identify potential data-quality issues.
- Apply configurable thresholds for nulls and duplicates.
- Save profiling results as a structured JSON report.
- Display a readable profiling summary in the terminal.

---

## Technologies Used

- Python 3.13
- Pandas
- OpenPyXL
- JSON

---

## Project Structure

```text
SW2627-Python-DeliveryPatternAnalytics/
│
├── app/
│
├── data/
│   ├── raw/
│   │   ├── deliveries.csv
│   │   ├── deliveries_semicolon.csv
│   │   ├── deliveries_nested.json
│   │   └── delivery_profiling_dataset.xlsx
│   │
│   └── processed/
│
├── scripts/
│   ├── delivery_workflow.py
│   ├── data_ingestion.py
│   └── data_profiling.py
│
├── logs/
│   └── workflow.log
│
├── output/
│   ├── processed_deliveries.csv
│   ├── intake_report.json
│   └── profiling_report.json
│
├── requirements.txt
├── README.md
└── WORKFLOW.md