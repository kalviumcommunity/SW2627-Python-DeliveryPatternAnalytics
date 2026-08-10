# Delivery Pattern Analytics Platform

## CSV & JSON Data Ingestion

### Overview

This assignment implements the **CSV & JSON Data Ingestion** module for the Delivery Pattern Analytics Platform.

The purpose of this module is to load business data from multiple source formats into analysis-ready Pandas DataFrames.

The ingestion process uses explicit parameters for delimiters and encodings instead of relying only on default values. This helps prevent silent data-loading errors when incoming datasets use different formats or encodings.

---

## Objectives

The ingestion module is designed to:

- Load standard CSV files.
- Load CSV files with different delimiters.
- Handle different file encodings.
- Provide an encoding fallback strategy.
- Load JSON files.
- Handle nested JSON structures.
- Flatten nested JSON using `pandas.json_normalize()`.
- Document what data was loaded.
- Display dataset shape, data types, and sample records.

---

## Technologies Used

- Python 3.13
- Pandas
- Chardet

---

## Project Structure

```text
SW2627-Python-DeliveryPatternAnalytics/
│
├── app/
│   ├── database/
│   ├── models/
│   ├── routes/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   └── utils/
│
├── data/
│   ├── raw/
│   │   ├── deliveries.csv
│   │   ├── deliveries_semicolon.csv
│   │   └── deliveries_nested.json
│   │
│   └── processed/
│
├── validation/
│   └── intake_validation.py
│
├── scripts/
│   ├── delivery_workflow.py
│   └── data_ingestion.py
│
├── logs/
│   └── workflow.log
│
├── output/
│   ├── processed_deliveries.csv
│   └── intake_report.json
│
├── requirements.txt
├── README.md
└── WORKFLOW.md
```

---

# Ingestion Module

The ingestion module is located at:

```text
scripts/data_ingestion.py
```

It contains reusable functions for loading CSV and JSON files into Pandas DataFrames.

---

## CSV Ingestion

The `ingest_csv()` function loads CSV files using explicit delimiter and encoding parameters.

Example:

```python
ingest_csv(
    filepath="data/raw/deliveries.csv",
    delimiter=",",
    encoding="utf-8"
)
```

The delimiter and encoding are explicitly provided so that the ingestion process does not depend entirely on library defaults.

This makes the ingestion process more predictable when the format of an incoming dataset changes.

---

## Semicolon-Delimited CSV

CSV files do not always use commas as separators.

The module supports semicolon-delimited CSV files by explicitly providing:

```python
delimiter=";"
```

Example:

```python
ingest_csv(
    filepath="data/raw/deliveries_semicolon.csv",
    delimiter=";",
    encoding="utf-8"
)
```

The test dataset:

```text
data/raw/deliveries_semicolon.csv
```

is used to verify that the ingestion module correctly handles semicolon-delimited data.

The expected dataset contains:

```text
6 columns
5 rows
```

---

## Encoding Handling

CSV files may be received using different character encodings.

The ingestion module provides an encoding fallback strategy using:

```text
utf-8
latin-1
iso-8859-1
cp1252
```

The `ingest_csv_with_fallback()` function tries these encodings one by one.

If the first encoding fails, the function attempts the next encoding.

If none of the supported encodings work, the function raises an error explaining that the file could not be loaded.

This prevents the pipeline from silently assuming that every incoming file uses UTF-8.

---

## JSON Ingestion

The `ingest_json()` function loads JSON files into Pandas DataFrames.

Example:

```python
ingest_json(
    filepath="data/raw/deliveries_nested.json",
    is_nested=True
)
```

The function first checks that:

- The file exists.
- The file is not empty.

It then loads the JSON data using Pandas.

---

## Nested JSON Flattening

JSON data can contain hierarchical or nested objects.

For example:

```json
{
    "customer": {
        "name": "Alice",
        "city": "Delhi"
    },
    "rider": {
        "id": "R010",
        "name": "Rahul"
    }
}
```

These nested objects are flattened using:

```python
pd.json_normalize()
```

The resulting DataFrame can contain columns such as:

```text
customer.name
customer.city
rider.id
rider.name
```

This converts hierarchical JSON data into a tabular structure that can be used for analysis.

---

# Ingestion Documentation

The `document_ingestion()` function creates an ingestion report in the terminal.

The report includes:

- Source file
- Number of rows
- Number of columns
- Column data types
- First three rows

Example:

```text
==================================================
INGESTION REPORT
==================================================
Source: data/raw/deliveries.csv
Rows: 7
Columns: 6

Column Types:
...

First 3 Rows:
...
==================================================
```

This provides an audit trail showing what was loaded by the ingestion process.

---

# Test Datasets

The current implementation uses test datasets to verify different ingestion scenarios.

## Standard CSV

```text
data/raw/deliveries.csv
```

This tests standard comma-delimited CSV ingestion.

---

## Semicolon-Delimited CSV

```text
data/raw/deliveries_semicolon.csv
```

This tests explicit delimiter handling.

The file uses:

```text
;
```

as its delimiter.

---

## Nested JSON

```text
data/raw/deliveries_nested.json
```

This tests JSON ingestion and nested JSON flattening.

The JSON contains nested customer and rider information.

---

# Running the Ingestion Workflow

## 1. Activate the Virtual Environment

For Git Bash:

```bash
source venv/Scripts/activate
```

The terminal should display:

```text
(venv)
```

---

## 2. Install Dependencies

Install the project dependencies using:

```bash
python -m pip install -r requirements.txt
```

The main packages used by this module are:

```text
pandas
chardet
```

---

## 3. Run the Ingestion Script

From the project root directory, run:

```bash
python scripts/data_ingestion.py
```

---

# Expected Output

A successful execution should display reports for the standard CSV, semicolon-delimited CSV, and nested JSON files.

Example:

```text
Starting CSV & JSON Data Ingestion...

==================================================
INGESTION REPORT
==================================================
Source: data/raw/deliveries.csv
Rows: 7
Columns: 6

Column Types:
...

First 3 Rows:
...

==================================================
INGESTION REPORT
==================================================
Source: data/raw/deliveries_semicolon.csv
Rows: 5
Columns: 6

Column Types:
...

First 3 Rows:
...

Nested JSON flattened successfully.

==================================================
INGESTION REPORT
==================================================
Source: data/raw/deliveries_nested.json
Rows: 3
Columns: ...

Column Types:
...

First 3 Rows:
...

CSV & JSON ingestion completed successfully.
```

The exact data types displayed depend on the input dataset and Pandas type inference.

---

# Testing

The ingestion module was tested using:

```bash
python scripts/data_ingestion.py
```

The following scenarios were verified:

- Standard CSV ingestion.
- Semicolon-delimited CSV ingestion.
- Explicit CSV delimiter handling.
- Explicit UTF-8 encoding.
- CSV encoding fallback implementation.
- JSON ingestion.
- Nested JSON ingestion.
- Nested JSON flattening.
- Row count reporting.
- Column count reporting.
- Data type reporting.
- First three rows reporting.

---

# Relationship With Dataset Validation

The previous **Dataset Intake & Source Validation** module validates the incoming dataset before it enters the ingestion stage.

The ingestion module then loads the validated data into Pandas DataFrames.

The overall data workflow is:

```text
Incoming Dataset
       │
       ▼
Dataset Validation
       │
       ▼
CSV / JSON Ingestion
       │
       ▼
Pandas DataFrame
       │
       ▼
Dataset Profiling
       │
       ▼
Data Quality Processing
       │
       ▼
Analytics Dashboard
```

This separation ensures that validation and ingestion remain independent stages of the data pipeline.

---

# Project Workflow

The project follows a feature-branch workflow.

New functionality is developed in a separate branch before being submitted through a Pull Request.

For this assignment, the feature branch is:

```text
feature/csv-json-ingestion
```

Changes are committed using the project's conventional commit format.

Examples:

```text
feat: add csv and json ingestion module
test: add csv and nested json ingestion data
docs: document csv and json ingestion workflow
```

---

# Dependencies

The project's Python dependencies are stored in:

```text
requirements.txt
```

To install all dependencies:

```bash
python -m pip install -r requirements.txt
```

To regenerate the dependency file:

```bash
python -m pip freeze > requirements.txt
```

---

# Current Limitations

The current implementation focuses on:

- CSV ingestion.
- JSON ingestion.
- Nested JSON flattening.
- Common CSV encoding handling.

Excel and Parquet ingestion are not currently included in this module.

---

# Future Enhancements

The ingestion module can be extended to support:

- Excel files.
- Parquet files.
- Additional JSON structures.
- Automatic format detection.
- More advanced schema validation.
- Data ingestion metrics.
- Persistent ingestion audit logs.

---

# Assignment Outcome

This assignment establishes a reusable ingestion layer for the Delivery Pattern Analytics Platform.

The module demonstrates how to:

1. Load CSV data with explicit parameters.
2. Handle different CSV delimiters.
3. Handle common encoding variations.
4. Load JSON data.
5. Flatten nested JSON structures.
6. Document the shape and types of loaded data.
7. Create a predictable and auditable ingestion process.

The ingestion layer provides the foundation for the next stages of the data pipeline, including dataset profiling and data quality assessment.