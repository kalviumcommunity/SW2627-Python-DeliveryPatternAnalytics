import json
from datetime import datetime
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

INPUT_FILE = Path("data/raw/delivery_profiling_dataset.xlsx")
OUTPUT_DATASET = Path("output/type_enforced_deliveries.csv")
OUTPUT_REPORT = Path("output/type_enforcement_report.json")


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

def load_dataset(filepath):
    """Load the Excel dataset."""

    if not filepath.exists():
        raise FileNotFoundError(
            f"Dataset not found: {filepath}"
        )

    if filepath.stat().st_size == 0:
        raise ValueError(
            f"Dataset is empty: {filepath}"
        )

    df = pd.read_excel(filepath)

    if df.empty:
        raise ValueError(
            f"Dataset contains no rows: {filepath}"
        )

    return df


# ---------------------------------------------------------
# Capture data types
# ---------------------------------------------------------

def capture_dtypes(df):
    """Capture the data types of all columns."""

    return {
        column: str(dtype)
        for column, dtype in df.dtypes.items()
    }


# ---------------------------------------------------------
# Convert delivery date
# ---------------------------------------------------------

def enforce_date_type(df, column="delivery_date"):
    """
    Convert delivery_date to datetime using
    an explicit YYYY-MM-DD format.
    """

    if column not in df.columns:
        raise KeyError(
            f"Required column not found: {column}"
        )

    original_values = df[column].copy()

    try:
        converted = pd.to_datetime(
            df[column],
            format="%Y-%m-%d",
            errors="coerce"
        )
    except Exception as error:
        raise ValueError(
            f"Date conversion failed for {column}: {error}"
        )

    invalid_values = []

    for original, converted_value in zip(
        original_values,
        converted
    ):
        if pd.notna(original) and pd.isna(converted_value):
            invalid_values.append(str(original))

    df[column] = converted.astype("datetime64[ns]")

    return {
        "column": column,
        "conversion": "string/date → datetime",
        "format": "%Y-%m-%d",
        "invalid_values": invalid_values,
        "invalid_count": len(invalid_values)
    }


# ---------------------------------------------------------
# Convert currency to float
# ---------------------------------------------------------

def enforce_currency_type(df, column="refund_amount"):
    """
    Remove currency symbols and commas and
    convert the column to float.
    """

    if column not in df.columns:
        raise KeyError(
            f"Required column not found: {column}"
        )

    original_values = df[column].copy()

    cleaned = (
        df[column]
        .astype("string")
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    converted = pd.to_numeric(
        cleaned,
        errors="coerce"
    )

    invalid_values = []

    for original, converted_value in zip(
        original_values,
        converted
    ):
        if pd.notna(original) and pd.isna(converted_value):
            invalid_values.append(str(original))

    df[column] = converted.astype(float)

    return {
        "column": column,
        "conversion": "currency → float",
        "invalid_values": invalid_values,
        "invalid_count": len(invalid_values)
    }


# ---------------------------------------------------------
# Convert complaint to boolean
# ---------------------------------------------------------

def enforce_boolean_type(df, column="complaint"):
    """
    Convert complaint values such as Yes/No
    and 1/0 into Boolean values.
    """

    if column not in df.columns:
        raise KeyError(
            f"Required column not found: {column}"
        )

    original_values = df[column].copy()

    mapping = {
        "yes": True,
        "no": False,
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        1: True,
        0: False,
        True: True,
        False: False
    }

    def convert_value(value):
        if pd.isna(value):
            return pd.NA

        if isinstance(value, str):
            cleaned = value.strip().lower()

            if cleaned in mapping:
                return mapping[cleaned]

        if value in mapping:
            return mapping[value]

        return pd.NA

    converted = original_values.map(convert_value)

    invalid_values = []

    for original, converted_value in zip(
        original_values,
        converted
    ):
        if pd.notna(original) and pd.isna(converted_value):
            invalid_values.append(str(original))

    df[column] = converted.astype("boolean")

    return {
        "column": column,
        "conversion": "text/integer → boolean",
        "invalid_values": invalid_values,
        "invalid_count": len(invalid_values)
    }


# ---------------------------------------------------------
# Compare data types
# ---------------------------------------------------------

def compare_dtypes(before, after):
    """Compare data types before and after enforcement."""

    changes = {}

    for column in before:
        if column in after and before[column] != after[column]:
            changes[column] = {
                "before": before[column],
                "after": after[column]
            }

    return changes


# ---------------------------------------------------------
# Validate final types
# ---------------------------------------------------------

def validate_types(df):
    """Validate that required columns have expected types."""

    expected_types = {
        "delivery_date": "datetime64[ns]",
        "refund_amount": "float64",
        "complaint": "boolean"
    }

    validation = {}
    all_valid = True

    for column, expected_type in expected_types.items():

        if column not in df.columns:
            validation[column] = {
                "status": "FAIL",
                "expected": expected_type,
                "actual": "column missing"
            }

            all_valid = False
            continue

        actual_type = str(df[column].dtype)

        passed = actual_type == expected_type

        validation[column] = {
            "status": "PASS" if passed else "FAIL",
            "expected": expected_type,
            "actual": actual_type
        }

        if not passed:
            all_valid = False

    return validation, all_valid


# ---------------------------------------------------------
# Generate report
# ---------------------------------------------------------

def generate_report(filepath):
    """Run the complete type enforcement workflow."""

    print("\nStarting Data Type Enforcement & Standardisation...\n")

    df = load_dataset(filepath)

    print(f"Dataset loaded: {filepath}")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    # Capture original data types
    before_dtypes = capture_dtypes(df)

    print("\nOriginal Data Types:")
    for column, dtype in before_dtypes.items():
        print(f"  {column}: {dtype}")

    # Apply conversions
    print("\nApplying type conversions...")

    conversion_logs = []

    date_log = enforce_date_type(
        df,
        "delivery_date"
    )
    conversion_logs.append(date_log)

    currency_log = enforce_currency_type(
        df,
        "refund_amount"
    )
    conversion_logs.append(currency_log)

    boolean_log = enforce_boolean_type(
        df,
        "complaint"
    )
    conversion_logs.append(boolean_log)

    # Capture final data types
    after_dtypes = capture_dtypes(df)

    # Compare data types
    dtype_changes = compare_dtypes(
        before_dtypes,
        after_dtypes
    )

    # Validate final types
    validation, all_valid = validate_types(df)

    # Create output folders
    OUTPUT_DATASET.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_REPORT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save processed dataset
    df.to_csv(
        OUTPUT_DATASET,
        index=False
    )

    # Create report
    report = {
        "timestamp": datetime.now().isoformat(),
        "source": str(filepath),

        "dataset": {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns)
        },

        "before_dtypes": before_dtypes,

        "after_dtypes": after_dtypes,

        "dtype_changes": dtype_changes,

        "conversion_logs": conversion_logs,

        "validation": validation,

        "summary": {
            "columns_changed": len(dtype_changes),
            "all_required_types_valid": all_valid
        }
    }

    # Save JSON report
    with open(
        OUTPUT_REPORT,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
            default=str
        )

    # Display results
    print("\n" + "=" * 60)
    print("DATA TYPE ENFORCEMENT REPORT")
    print("=" * 60)

    print("\nData Type Changes:")

    if dtype_changes:
        for column, change in dtype_changes.items():
            print(
                f"  {column}: "
                f"{change['before']} → "
                f"{change['after']}"
            )
    else:
        print("  No data type changes detected.")

    print("\nType Validation:")

    for column, result in validation.items():
        print(
            f"  {column}: {result['status']}"
        )
        print(
            f"    Expected: {result['expected']}"
        )
        print(
            f"    Actual:   {result['actual']}"
        )

    print("\nConversion Errors:")

    total_errors = 0

    for log in conversion_logs:
        count = log["invalid_count"]
        total_errors += count

        print(
            f"  {log['column']}: "
            f"{count} invalid value(s)"
        )

    print("\n" + "=" * 60)

    print(
        f"\nProcessed dataset saved to:"
        f"\n{OUTPUT_DATASET}"
    )

    print(
        f"\nType enforcement report saved to:"
        f"\n{OUTPUT_REPORT}"
    )

    if all_valid:
        print(
            "\nData type enforcement completed successfully."
        )
    else:
        print(
            "\nData type enforcement completed "
            "with validation failures."
        )

    return report


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    generate_report(INPUT_FILE)


if __name__ == "__main__":
    main()