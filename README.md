# Missing Value Detection & Imputation

## Overview

This assignment implements the **Missing Value Detection & Imputation** stage of the Delivery Pattern Analytics Platform.

Real-world delivery datasets can contain incomplete records. Missing delivery times, delivery statuses, or complaint information can affect calculations and downstream analysis.

The purpose of this module is to:

- Detect missing values before treatment.
- Select an appropriate strategy based on column type and business context.
- Impute numerical values using the median.
- Impute categorical values using the mode.
- Protect critical identifier fields from artificial values.
- Compare missing values before and after treatment.
- Record every imputation decision.
- Save an audit report explaining the impact of the treatment.
- Save an imputed dataset for downstream processing.

The module does **not blindly fill every missing value**. Each treatment is selected intentionally and documented for auditability.

---

## Assignment

**2.18 — Missing Value Detection & Imputation**

The assignment focuses on handling incomplete records using defensible and auditable strategies.

The main principle is:

> Missing values should be handled intentionally based on data type and business context, rather than being filled or deleted without documentation.

---

## Objectives

The module is designed to:

1. Analyze missing values before treatment.
2. Calculate null counts and percentages.
3. Use median imputation for numerical columns.
4. Use mode imputation for categorical columns.
5. Avoid inventing values for critical identifiers.
6. Drop rows only when a critical identifier is missing.
7. Analyze missing values after treatment.
8. Compare before and after results.
9. Record the reasoning behind every decision.
10. Save the final imputed dataset.
11. Save an auditable JSON report.

---

# Technologies Used

- Python 3.13
- Pandas
- OpenPyXL
- JSON

---

# Project Structure

The relevant project files are:

```text
SW2627-Python-DeliveryPatternAnalytics/
│
├── data/
│   └── raw/
│       └── delivery_profiling_dataset.xlsx
│
├── scripts/
│   ├── delivery_workflow.py
│   ├── data_ingestion.py
│   ├── data_profiling.py
│   ├── type_enforcement.py
│   └── missing_value_imputation.py
│
├── output/
│   ├── profiling_report.json
│   ├── type_enforcement_report.json
│   ├── type_enforced_deliveries.csv
│   ├── imputed_deliveries.csv
│   └── imputation_audit.json
│
├── requirements.txt
├── README.md
└── WORKFLOW.md