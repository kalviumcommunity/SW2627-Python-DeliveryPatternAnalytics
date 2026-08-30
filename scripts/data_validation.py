import json
from pathlib import Path

import pandas as pd

# PATH CONFIGURATION

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "raw" / "delivery_profiling_dataset.xlsx"
OUTPUT_DIR = BASE_DIR / "output"

REPORT_FILE = OUTPUT_DIR / "validation_report.json"
FAILURES_FILE = OUTPUT_DIR / "validation_failures.csv"

# DATA LOADING

def load_dataset(file_path):
    """Load the delivery dataset from Excel."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    df = pd.read_excel(file_path)

    if df.empty:
        raise ValueError("The dataset is empty.")

    return df

# VALIDATION RULES

def validate_delivery_id(df):
    """Delivery ID must not be null."""
    return df["delivery_id"].notna()


def validate_customer_name(df):
    """Customer name must not be null or empty."""
    return (
        df["customer_name"].notna()
        & df["customer_name"].astype("string").str.strip().ne("")
    )


def validate_rider_id(df):
    """Rider ID must not be null or empty."""
    return (
        df["rider_id"].notna()
        & df["rider_id"].astype("string").str.strip().ne("")
    )


def validate_delivery_time(df):
    """Delivery time must be non-negative."""
    return (
        df["delivery_time_min"].notna()
        & (df["delivery_time_min"] >= 0)
    )


def validate_delivery_time_upper_limit(df):
    """
    Delivery time should not exceed a reasonable
    operational threshold of 180 minutes.
    """
    return (
        df["delivery_time_min"].notna()
        & (df["delivery_time_min"] <= 180)
    )


def validate_sla_limit(df):
    """SLA limit must be positive."""
    return (
        df["sla_limit_min"].notna()
        & (df["sla_limit_min"] > 0)
    )


def validate_refund_amount(df):
    """Refund amount cannot be negative."""
    return (
        df["refund_amount"].notna()
        & (df["refund_amount"] >= 0)
    )


def validate_delivery_status(df):
    """Delivery status must be On Time or Delayed."""
    allowed_values = {"On Time", "Delayed"}

    return (
        df["delivery_status"].notna()
        & df["delivery_status"].isin(allowed_values)
    )


def validate_complaint(df):
    """Complaint must be Yes or No."""
    allowed_values = {"Yes", "No"}

    return (
        df["complaint"].notna()
        & df["complaint"].isin(allowed_values)
    )


def validate_city(df):
    """City must belong to the supported city list."""
    allowed_values = {
        "Delhi",
        "Mumbai",
        "Bangalore",
        "Pune",
        "Chennai",
        "Hyderabad",
    }

    return (
        df["city"].notna()
        & df["city"].isin(allowed_values)
    )


def validate_payment_method(df):
    """Payment method must be UPI, Card, or Cash."""
    allowed_values = {
        "UPI",
        "Card",
        "Cash",
    }

    return (
        df["payment_method"].notna()
        & df["payment_method"].isin(allowed_values)
    )


def validate_delivery_date(df):
    """Delivery date must exist and be a valid date."""
    return df["delivery_date"].notna()

# RULE DEFINITIONS

def get_validation_rules(df):
    """
    Return all validation rules.

    Each rule contains:
    - column
    - type
    - validation result
    """

    return {
        "delivery_id_required": {
            "column": "delivery_id",
            "type": "null_constraint",
            "result": validate_delivery_id(df),
        },

        "customer_name_required": {
            "column": "customer_name",
            "type": "null_constraint",
            "result": validate_customer_name(df),
        },

        "rider_id_required": {
            "column": "rider_id",
            "type": "null_constraint",
            "result": validate_rider_id(df),
        },

        "delivery_time_non_negative": {
            "column": "delivery_time_min",
            "type": "range_check",
            "result": validate_delivery_time(df),
        },

        "delivery_time_reasonable_limit": {
            "column": "delivery_time_min",
            "type": "range_check",
            "result": validate_delivery_time_upper_limit(df),
        },

        "sla_limit_positive": {
            "column": "sla_limit_min",
            "type": "range_check",
            "result": validate_sla_limit(df),
        },

        "refund_amount_non_negative": {
            "column": "refund_amount",
            "type": "range_check",
            "result": validate_refund_amount(df),
        },

        "delivery_status_valid": {
            "column": "delivery_status",
            "type": "categorical_check",
            "result": validate_delivery_status(df),
        },

        "complaint_valid": {
            "column": "complaint",
            "type": "categorical_check",
            "result": validate_complaint(df),
        },

        "city_valid": {
            "column": "city",
            "type": "categorical_check",
            "result": validate_city(df),
        },

        "payment_method_valid": {
            "column": "payment_method",
            "type": "categorical_check",
            "result": validate_payment_method(df),
        },

        "delivery_date_required": {
            "column": "delivery_date",
            "type": "null_constraint",
            "result": validate_delivery_date(df),
        },
    }

# VALIDATION REPORT

def build_rule_report(rule_name, rule_info, total_records):
    """Create a report entry for one validation rule."""

    result = rule_info["result"]

    passed = int(result.sum())
    failed = int(total_records - passed)

    return {
        "rule": rule_name,
        "column": rule_info["column"],
        "type": rule_info["type"],
        "records_checked": total_records,
        "passed": passed,
        "failed": failed,
        "status": "PASS" if failed == 0 else "FAIL",
    }

# RUN VALIDATION

def run_validation(df):
    """Run every validation rule and return results."""

    rules = get_validation_rules(df)

    validation_results = {}
    report_entries = []

    total_records = len(df)

    for rule_name, rule_info in rules.items():

        result = rule_info["result"]

        validation_results[rule_name] = result

        report_entry = build_rule_report(
            rule_name,
            rule_info,
            total_records,
        )

        report_entries.append(report_entry)

    return validation_results, report_entries

# IDENTIFY FAILED RECORDS

def identify_failures(df, validation_results):
    """Identify records that fail one or more validation rules."""

    validation_df = df.copy()

    validation_columns = []

    for rule_name, result in validation_results.items():

        column_name = f"valid_{rule_name}"

        validation_df[column_name] = result

        validation_columns.append(column_name)

    validation_df["passes_all_checks"] = (
        validation_df[validation_columns]
        .all(axis=1)
    )

    failures = validation_df[
        ~validation_df["passes_all_checks"]
    ].copy()

    return validation_df, failures, validation_columns

# SAVE OUTPUTS

def save_outputs(
    df,
    validation_df,
    failures,
    report_entries,
    validation_columns,
):
    """Save validation report and failed records."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    total_records = len(df)

    records_passed = int(
        validation_df["passes_all_checks"].sum()
    )

    records_failed = total_records - records_passed

    failed_rules = sum(
        1
        for entry in report_entries
        if entry["status"] == "FAIL"
    )

    passed_rules = len(report_entries) - failed_rules

    report = {
        "assignment": "2.27 - Systematic Data Validation",

        "dataset": {
            "source": str(
                INPUT_FILE.relative_to(BASE_DIR)
            ),
            "rows": int(len(df)),
            "columns": int(len(df.columns)),
            "column_names": list(df.columns),
        },

        "validation_summary": {
            "total_rules": len(report_entries),
            "passed_rules": passed_rules,
            "failed_rules": failed_rules,
            "records_checked": total_records,
            "records_passed": records_passed,
            "records_failed": records_failed,
        },

        "validation_rules": report_entries,

        "outputs": {
            "validation_report": str(
                REPORT_FILE.relative_to(BASE_DIR)
            ),
            "validation_failures": str(
                FAILURES_FILE.relative_to(BASE_DIR)
            ),
        },
    }

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            default=str,
        )

    # Save only original dataset columns plus validation information.
    output_columns = list(df.columns) + validation_columns + [
        "passes_all_checks"
    ]

    failures[output_columns].to_csv(
        FAILURES_FILE,
        index=False,
    )

    return report





if __name__ == "__main__":
    main()