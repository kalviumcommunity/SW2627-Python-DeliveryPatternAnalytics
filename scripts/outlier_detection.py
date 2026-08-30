from pathlib import Path
from datetime import datetime
import json

import numpy as np
import pandas as pd
from scipy import stats

# Configuration


INPUT_FILE = Path("data/raw/delivery_profiling_dataset.xlsx")

OUTPUT_DIR = Path("output")

REPORT_FILE = OUTPUT_DIR / "outlier_detection_report.json"
AUDIT_FILE = OUTPUT_DIR / "outlier_cleaning_log.csv"


NUMERICAL_COLUMNS = [
    "delivery_time_min",
    "sla_limit_min",
    "refund_amount",
]

# Load Dataset


def load_dataset(filepath):
    """Load the delivery dataset from Excel."""

    if not filepath.exists():
        raise FileNotFoundError(
            f"Dataset not found: {filepath}"
        )

    df = pd.read_excel(filepath)

    if df.empty:
        raise ValueError(
            f"Dataset is empty: {filepath}"
        )

    return df

# Z-Score Detection

def detect_zscore_outliers(series, threshold=3):
    """
    Detect outliers using Z-score.

    A value is considered an outlier when its absolute
    Z-score is greater than the specified threshold.
    """

    numeric = pd.to_numeric(series, errors="coerce")

    valid = numeric.dropna()

    if len(valid) < 2:
        return pd.Series(False, index=series.index)

    z_scores = pd.Series(
        np.nan,
        index=series.index,
        dtype="float64"
    )

    z_scores.loc[valid.index] = np.abs(
        stats.zscore(valid)
    )

    return z_scores > threshold

# IQR Detection


def detect_iqr_outliers(series, multiplier=1.5):
    """
    Detect outliers using the Interquartile Range method.

    Outlier boundaries:

        Lower = Q1 - 1.5 * IQR
        Upper = Q3 + 1.5 * IQR
    """

    numeric = pd.to_numeric(series, errors="coerce")

    q1 = numeric.quantile(0.25)
    q3 = numeric.quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr

    outliers = (
        (numeric < lower_bound)
        | (numeric > upper_bound)
    )

    return outliers, lower_bound, upper_bound

# Safe JSON Conversion

def make_json_safe(value):
    """Convert Pandas/Numpy values into JSON-compatible values."""

    if pd.isna(value):
        return None

    if isinstance(value, (np.integer,)):
        return int(value)

    if isinstance(value, (np.floating,)):
        return float(value)

    if isinstance(value, (np.bool_,)):
        return bool(value)

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    return value

# Outlier Analysis

def analyze_outliers(df):
    """
    Detect outliers for all configured numerical columns.

    Both Z-score and IQR methods are applied.
    """

    analysis = {}
    audit_records = []

    for column in NUMERICAL_COLUMNS:

        if column not in df.columns:
            continue

        series = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        zscore_flags = detect_zscore_outliers(series)

        iqr_flags, lower_bound, upper_bound = (
            detect_iqr_outliers(series)
        )

        combined_flags = (
            zscore_flags.fillna(False)
            | iqr_flags.fillna(False)
        )

        zscore_count = int(
            zscore_flags.fillna(False).sum()
        )

        iqr_count = int(
            iqr_flags.fillna(False).sum()
        )

        combined_count = int(
            combined_flags.sum()
        )

        analysis[column] = {
            "zscore": {
                "threshold": 3,
                "outlier_count": zscore_count,
            },
            "iqr": {
                "multiplier": 1.5,
                "q1": make_json_safe(series.quantile(0.25)),
                "q3": make_json_safe(series.quantile(0.75)),
                "iqr": make_json_safe(
                    series.quantile(0.75)
                    - series.quantile(0.25)
                ),
                "lower_bound": make_json_safe(lower_bound),
                "upper_bound": make_json_safe(upper_bound),
                "outlier_count": iqr_count,
            },
            "combined_outlier_count": combined_count,
            "handling_strategy": "flag",
            "reason": (
                "Flag unusual delivery values without deleting "
                "records because statistical anomalies may "
                "represent legitimate operational events."
            ),
        }

        # Create binary flag column
        flag_column = f"{column}_outlier"

        df[flag_column] = combined_flags.astype(int)

        # Create audit records for detected outliers
        for index in df.index[combined_flags]:

            audit_records.append({
                "row_index": int(index),
                "column": column,
                "original_value": make_json_safe(
                    df.loc[index, column]
                ),
                "zscore_outlier": bool(
                    zscore_flags.loc[index]
                ),
                "iqr_outlier": bool(
                    iqr_flags.loc[index]
                ),
                "handling_action": "flag",
                "reason": (
                    "Value detected as statistically unusual "
                    "using Z-score and/or IQR."
                ),
            })

    return df, analysis, audit_records

# Validation

def validate_results(df, analysis):
    """
    Validate that outlier flag columns were created and
    contain only binary values.
    """

    validation = {}

    for column in analysis:

        flag_column = f"{column}_outlier"

        if flag_column not in df.columns:

            validation[column] = {
                "status": "FAIL",
                "reason": "Outlier flag column was not created.",
            }

            continue

        unique_values = set(
            df[flag_column].dropna().unique()
        )

        valid_binary = unique_values.issubset({0, 1})

        validation[column] = {
            "status": "PASS" if valid_binary else "FAIL",
            "flag_column": flag_column,
            "unique_flag_values": [
                int(value) for value in unique_values
            ],
        }

    return validation

# Save Audit Log

def save_audit_log(records):
    """Save detected outliers to a CSV audit file."""

    if records:
        audit_df = pd.DataFrame(records)
    else:
        audit_df = pd.DataFrame(
            columns=[
                "row_index",
                "column",
                "original_value",
                "zscore_outlier",
                "iqr_outlier",
                "handling_action",
                "reason",
            ]
        )

    audit_df.to_csv(
        AUDIT_FILE,
        index=False
    )

# Generate Report

def generate_report(
    df_original,
    df_processed,
    analysis,
    validation,
):
    """Create the JSON outlier detection report."""

    total_outliers = sum(
        details["combined_outlier_count"]
        for details in analysis.values()
    )

    report = {
        "timestamp": datetime.now().isoformat(),

        "source": str(INPUT_FILE),

        "dataset": {
            "rows_before": int(len(df_original)),
            "rows_after": int(len(df_processed)),
            "columns_before": int(len(df_original.columns)),
            "columns_after": int(len(df_processed.columns)),
        },

        "methods": {
            "zscore": {
                "threshold": 3,
                "description": (
                    "Values with absolute Z-score greater "
                    "than 3 are treated as statistical outliers."
                ),
            },
            "iqr": {
                "multiplier": 1.5,
                "description": (
                    "Values outside Q1 - 1.5*IQR and "
                    "Q3 + 1.5*IQR are treated as outliers."
                ),
            },
        },

        "columns_analyzed": list(analysis.keys()),

        "outlier_analysis": analysis,

        "handling_strategy": {
            "action": "flag",
            "reason": (
                "Flagging preserves the original records while "
                "allowing downstream analysis to identify unusual "
                "delivery values."
            ),
        },

        "summary": {
            "columns_analyzed": len(analysis),
            "total_outlier_flags": int(total_outliers),
            "rows_removed": 0,
            "data_preserved": True,
        },

        "validation": validation,

        "outputs": {
            "audit_log": str(AUDIT_FILE),
            "report": str(REPORT_FILE),
        },
    }

    return report

# Main Workflow

def main():

    print()
    print("=" * 60)
    print("Assignment 2.23")
    print("Outlier Detection with Statistical Methods")
    print("=" * 60)
    print()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Loading dataset...")

    df_original = load_dataset(INPUT_FILE)

    print(
        f"Dataset loaded successfully: "
        f"{len(df_original)} rows, "
        f"{len(df_original.columns)} columns"
    )

    print()
    print("Detecting outliers using Z-score and IQR...")

    df_processed = df_original.copy()

    (
        df_processed,
        analysis,
        audit_records
    ) = analyze_outliers(df_processed)

    print()
    print("Outlier Detection Results")
    print("-" * 60)

    for column, details in analysis.items():

        print(f"\nColumn: {column}")

        print(
            f"  Z-score outliers: "
            f"{details['zscore']['outlier_count']}"
        )

        print(
            f"  IQR outliers: "
            f"{details['iqr']['outlier_count']}"
        )

        print(
            f"  Combined flags: "
            f"{details['combined_outlier_count']}"
        )

        print(
            f"  Handling: "
            f"{details['handling_strategy']}"
        )

    print()
    print("Creating validation results...")

    validation = validate_results(
        df_processed,
        analysis
    )

    print()
    print("Saving audit log...")

    save_audit_log(audit_records)

    print(
        f"Audit log saved to: {AUDIT_FILE}"
    )

    print()
    print("Generating report...")

    report = generate_report(
        df_original,
        df_processed,
        analysis,
        validation
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    print(
        f"Report saved to: {REPORT_FILE}"
    )

    print()
    print("=" * 60)
    print("Before rows :", len(df_original))
    print("After rows  :", len(df_processed))
    print("Rows removed: 0")
    print(
        "Outlier records were flagged, "
        "not deleted."
    )
    print("=" * 60)
    print()

    print("Assignment 2.23 completed successfully.")


if __name__ == "__main__":
    main()