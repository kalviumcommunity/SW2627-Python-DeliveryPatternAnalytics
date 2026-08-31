# Data Type Enforcement & Standardisation

## Overview

This assignment implements **Data Type Enforcement & Standardisation (2.19)** for the Delivery Pattern Analytics Platform.

The purpose is to ensure that important columns use correct and consistent data types before analysis.

The module handles:

- String to datetime conversion
- Currency to float conversion
- Text/integer to Boolean conversion
- Before/after dtype comparison
- Conversion validation
- Conversion error logging

## Technologies

- Python 3.13
- Pandas
- OpenPyXL
- JSON

## Input Dataset

```text
data/raw/delivery_profiling_dataset.xlsx
```

The dataset contains delivery information such as:

- delivery_id
- customer_name
- rider_id
- city
- delivery_time_min
- sla_limit_min
- delivery_status
- complaint
- refund_amount
- delivery_date
- payment_method

The original Excel file is not modified.

## Type Enforcement

| Column | Conversion | Final Type |
|---|---|---|
| delivery_date | String → Datetime | datetime64[ns] |
| refund_amount | Currency → Float | float64 |
| complaint | Text/Integer → Boolean | boolean |

### Date Conversion

The `delivery_date` column is converted using an explicit format:

```python
pd.to_datetime(
    value,
    format="%Y-%m-%d"
)
```

Using an explicit format prevents incorrect date interpretation.

### Currency Conversion

The `refund_amount` column is cleaned before conversion.

Currency symbols and commas are removed:

```text
$1,250.00 → 1250.00
```

The final type is:

```text
float64
```

Invalid values are recorded as conversion errors.

### Boolean Conversion

The `complaint` column supports:

```text
Yes → True
No  → False
1   → True
0   → False
```

The final Pandas type is:

```text
boolean
```

## Validation

The script captures data types before conversion and after conversion.

It validates that:

- delivery_date → datetime64[ns]
- refund_amount → float64
- complaint → boolean

Each conversion is reported as PASS or FAIL.

## Script

The implementation is located at:

```text
scripts/type_enforcement.py
```

## Workflow

```text
Load Dataset
     ↓
Capture Original Types
     ↓
Convert Date
     ↓
Convert Currency
     ↓
Convert Boolean
     ↓
Capture Final Types
     ↓
Compare Types
     ↓
Validate Conversions
     ↓
Generate Report
     ↓
Save Processed Dataset
```

## Output Files

The script generates:

```text
output/type_enforced_deliveries.csv
```

This contains the dataset after type conversion.

It also generates:

```text
output/type_enforcement_report.json
```

The report records:

- Original data types
- Final data types
- Type changes
- Conversion methods
- Conversion errors
- Validation results

## Running the Script

Activate the virtual environment:

```bash
source venv/Scripts/activate
```

Check dependencies:

```bash
python -c "import pandas; import openpyxl; print('Dependencies OK')"
```

Run the script:

```bash
python scripts/type_enforcement.py
```

## Expected Result

A successful execution should show:

```text
delivery_date: PASS
refund_amount: PASS
complaint: PASS
```

The terminal will also display the locations of the generated output files.

## Data Preservation

The original dataset remains unchanged:

```text
data/raw/delivery_profiling_dataset.xlsx
```

Only the processed copy is saved to:

```text
output/type_enforced_deliveries.csv
```

This keeps the original source data available for auditing and reproducibility.

## Relationship With Previous Assignments

The project workflow now follows:

```text
Validation
    ↓
Ingestion
    ↓
Profiling
    ↓
Missing Value Handling
    ↓
Type Enforcement
```

The previous assignments identified and handled data-quality problems.

This assignment ensures that the cleaned data uses reliable and predictable data types.

## Assignment Outcome

The completed module provides a reusable type-enforcement stage.

It explicitly converts dates, currency, and Boolean fields, validates the resulting types, records conversion information, and saves both the processed dataset and an audit report.

The resulting dataset is ready for reliable calculations, filtering, aggregation, time-based analysis, and future analytics.

Live Demo: https://sw2627-python-deliverypatternanalytics.onrender.com/