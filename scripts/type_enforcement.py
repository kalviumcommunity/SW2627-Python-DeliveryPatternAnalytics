import json
import os

import pandas as pd


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = "data/raw/delivery_profiling_dataset.xlsx"

OUTPUT_FILE = "output/type_enforced_deliveries.csv"

REPORT_FILE = "output/type_enforcement_report.json"


# ============================================================
# Load Dataset
# ============================================================

def load_dataset(filepath):
    """
    Load the delivery dataset from Excel.

    The original source file is never modified.
    """

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Dataset not found: {filepath}"
        )

    if os.path.getsize(filepath) == 0:
        raise ValueError(
            f"Dataset is empty: {filepath}"
        )

    df = pd.read_excel(filepath)

    if df.empty:
        raise ValueError(
            f"Dataset contains no records: {filepath}"
        )

    return df


# ============================================================
# Capture Data Types
# ============================================================

def capture_dtypes(df):
    """
    Capture the current data type of every column.
    """

    return {
        column: str(dtype)
        for column, dtype in df.dtypes.items()
    }


# ============================================================
# String -> Datetime
# ============================================================

def enforce_date_type(df):
    """
    Convert delivery_date to datetime using an explicit format.

    Expected format:
        YYYY-MM-DD

    Explicit format is used instead of allowing pandas
    to infer the format.
    """

    column = "delivery_date"

    if column not in df.columns:
        raise KeyError(
            f"Required column not found: {column}"
        )

    before_type = str(df[column].dtype)

    conversion_errors = []

    converted_values = []

    for value in df[column]:

        if pd.isna(value):
            converted_values.append(pd.NaT)
            continue

        try:
            converted_value = pd.to_datetime(
                value,
                format="%Y-%m-%d"
            )

            converted_values.append(
                converted_value
            )

        except (ValueError, TypeError):

            conversion_errors.append(
                str(value)
            )

            converted_values.append(
                pd.NaT
            )

    df[column] = pd.to_datetime(
        converted_values
    )

    after_type = str(df[column].dtype)

    return {
        "column": column,
        "conversion": "string_to_datetime",
        "before_type": before_type,
        "after_type": after_type,
        "format": "%Y-%m-%d",
        "conversion_errors": conversion_errors
    }


# ============================================================
# Currency -> Float
# ============================================================

def enforce_currency_type(df):
    """
    Convert refund_amount into float.

    Currency symbols and thousands separators are removed
    before numeric conversion.
    """

    column = "refund_amount"

    if column not in df.columns:
        raise KeyError(
            f"Required column not found: {column}"
        )

    before_type = str(df[column].dtype)

    original_values = df[column].copy()

    cleaned_values = (
        df[column]
        .astype("string")
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    numeric_values = pd.to_numeric(
        cleaned_values,
        errors="coerce"
    )

    conversion_errors = []

    for original, converted in zip(
        original_values,
        numeric_values
    ):

        if (
            pd.notna(original)
            and pd.isna(converted)
        ):
            conversion_errors.append(
                str(original)
            )

    df[column] = numeric_values.astype(float)

    after_type = str(df[column].dtype)

    return {
        "column": column,
        "conversion": "currency_to_float",
        "before_type": before_type,
        "after_type": after_type,
        "currency_symbols_removed": [
            "$",
            ","
        ],
        "conversion_errors": conversion_errors
    }


# ============================================================
# Integer / Text -> Boolean
# ============================================================

def enforce_boolean_type(df):
    """
    Convert complaint values to proper Boolean values.

    Supported values include:

        Yes / No
        yes / no
        True / False
        1 / 0

    Missing values remain missing.
    """

    column = "complaint"

    if column not in df.columns:
        raise KeyError(
            f"Required column not found: {column}"
        )

    before_type = str(df[column].dtype)

    mapping = {
        "yes": True,
        "no": False,
        "true": True,
        "false": False,
        "1": True,
        "0": False
    }

    conversion_errors = []

    converted_values = []

    for value in df[column]:

        if pd.isna(value):

            converted_values.append(
                pd.NA
            )

            continue

        normalized_value = (
            str(value)
            .strip()
            .lower()
        )

        if normalized_value in mapping:

            converted_values.append(
                mapping[normalized_value]
            )

        else:

            conversion_errors.append(
                str(value)
            )

            converted_values.append(
                pd.NA
            )

    df[column] = pd.Series(
        converted_values,
        index=df.index,
        dtype="boolean"
    )

    after_type = str(df[column].dtype)

    return {
        "column": column,
        "conversion": "value_to_boolean",
        "before_type": before_type,
        "after_type": after_type,
        "mapping": mapping,
        "conversion_errors": conversion_errors
    }


# ============================================================
# Validate Types
# ============================================================

def validate_types(df):
    """
    Validate that required columns have the expected
    final data types.
    """

    results = {}

    # --------------------------------------------
    # Date
    # --------------------------------------------

    results["delivery_date"] = {
        "expected_type": "datetime64[ns]",
        "actual_type": str(
            df["delivery_date"].dtype
        ),
        "valid": pd.api.types.is_datetime64_any_dtype(
            df["delivery_date"]
        )
    }

    # --------------------------------------------
    # Currency
    # --------------------------------------------

    results["refund_amount"] = {
        "expected_type": "float64",
        "actual_type": str(
            df["refund_amount"].dtype
        ),
        "valid": pd.api.types.is_float_dtype(
            df["refund_amount"]
        )
    }

    # --------------------------------------------
    # Boolean
    # --------------------------------------------

    results["complaint"] = {
        "expected_type": "boolean",
        "actual_type": str(
            df["complaint"].dtype
        ),
        "valid": str(
            df["complaint"].dtype
        ) == "boolean"
    }

    return results


# ============================================================
# Compare Before and After Types
# ============================================================

def compare_dtypes(before_dtypes, after_dtypes):
    """
    Identify columns whose data types changed.
    """

    changes = {}

    for column in after_dtypes:

        before_type = before_dtypes.get(
            column
        )

        after_type = after_dtypes[column]

        if before_type != after_type:

            changes[column] = {
                "before": before_type,
                "after": after_type
            }

    return changes


# ============================================================
# Generate Report
# ============================================================

def generate_report(
    before_dtypes,
    after_dtypes,
    conversion_logs,
    validation_results,
    dtype_changes
):
    """
    Generate the complete type-enforcement report.
    """

    all_valid = all(
        result["valid"]
        for result in validation_results.values()
    )

    return {

        "timestamp": pd.Timestamp.now().isoformat(),

        "source": INPUT_FILE,

        "summary": {
            "all_required_types_valid": all_valid,
            "columns_changed": len(
                dtype_changes
            )
        },

        "before_dtypes": before_dtypes,

        "after_dtypes": after_dtypes,

        "dtype_changes": dtype_changes,

        "conversion_logs": conversion_logs,

        "validation": validation_results
    }


# ============================================================
# Save Report
# ============================================================

def save_report(report, filepath):
    """
    Save the report as JSON.
    """

    directory = os.path.dirname(filepath)

    if directory:
        os.makedirs(
            directory,
            exist_ok=True
        )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            default=str
        )


# ============================================================
# Save Processed Dataset
# ============================================================

def save_processed_dataset(df, filepath):
    """
    Save the type-enforced dataset.
    """

    directory = os.path.dirname(filepath)

    if directory:
        os.makedirs(
            directory,
            exist_ok=True
        )

    df.to_csv(
        filepath,
        index=False
    )


# ============================================================
# Print Report
# ============================================================

def print_report(
    before_dtypes,
    after_dtypes,
    conversion_logs,
    validation_results,
    dtype_changes
):
    """
    Print a readable report to the terminal.
    """

    print("\n" + "=" * 65)
    print("DATA TYPE ENFORCEMENT REPORT")
    print("=" * 65)

    # --------------------------------------------
    # Data type changes
    # --------------------------------------------

    print("\nDATA TYPE CHANGES")

    if dtype_changes:

        for column, change in dtype_changes.items():

            print(
                f"  {column}: "
                f"{change['before']} -> "
                f"{change['after']}"
            )

    else:

        print(
            "  No data type changes detected."
        )

    # --------------------------------------------
    # Conversion logs
    # --------------------------------------------

    print("\nCONVERSIONS")

    for log in conversion_logs:

        print(
            f"  Column: {log['column']}"
        )

        print(
            f"  Conversion: "
            f"{log['conversion']}"
        )

        print(
            f"  Before: "
            f"{log['before_type']}"
        )

        print(
            f"  After: "
            f"{log['after_type']}"
        )

        if log["conversion_errors"]:

            print(
                "  Conversion errors: "
                f"{log['conversion_errors']}"
            )

        else:

            print(
                "  Conversion errors: None"
            )

        print()

    # --------------------------------------------
    # Validation
    # --------------------------------------------

    print("TYPE VALIDATION")

    for column, result in validation_results.items():

        status = (
            "PASS"
            if result["valid"]
            else "FAIL"
        )

        print(
            f"  {column}: {status}"
        )

        print(
            f"    Expected: "
            f"{result['expected_type']}"
        )

        print(
            f"    Actual: "
            f"{result['actual_type']}"
        )

    # --------------------------------------------
    # Original types
    # --------------------------------------------

    print("\nORIGINAL DATA TYPES")

    for column, dtype in before_dtypes.items():

        print(
            f"  {column}: {dtype}"
        )

    # --------------------------------------------
    # Final types
    # --------------------------------------------

    print("\nFINAL DATA TYPES")

    for column, dtype in after_dtypes.items():

        print(
            f"  {column}: {dtype}"
        )

    print("=" * 65)


# ============================================================
# Main Workflow
# ============================================================

def main():

    print(
        "\nStarting Data Type Enforcement "
        "& Standardisation..."
    )

    # --------------------------------------------
    # Load dataset
    # --------------------------------------------

    df = load_dataset(
        INPUT_FILE
    )

    # --------------------------------------------
    # Capture original types
    # --------------------------------------------

    before_dtypes = capture_dtypes(
        df
    )

    conversion_logs = []

    # --------------------------------------------
    # Date conversion
    # --------------------------------------------

    date_log = enforce_date_type(
        df
    )

    conversion_logs.append(
        date_log
    )

    # --------------------------------------------
    # Currency conversion
    # --------------------------------------------

    currency_log = enforce_currency_type(
        df
    )

    conversion_logs.append(
        currency_log
    )

    # --------------------------------------------
    # Boolean conversion
    # --------------------------------------------

    boolean_log = enforce_boolean_type(
        df
    )

    conversion_logs.append(
        boolean_log
    )

    # --------------------------------------------
    # Capture final types
    # --------------------------------------------

    after_dtypes = capture_dtypes(
        df
    )

    # --------------------------------------------
    # Compare data types
    # --------------------------------------------

    dtype_changes = compare_dtypes(
        before_dtypes,
        after_dtypes
    )

    # --------------------------------------------
    # Validate conversions
    # --------------------------------------------

    validation_results = validate_types(
        df
    )

    # --------------------------------------------
    # Generate report
    # --------------------------------------------

    report = generate_report(
        before_dtypes,
        after_dtypes,
        conversion_logs,
        validation_results,
        dtype_changes
    )

    # --------------------------------------------
    # Save outputs
    # --------------------------------------------

    save_processed_dataset(
        df,
        OUTPUT_FILE
    )

    save_report(
        report,
        REPORT_FILE
    )

    # --------------------------------------------
    # Display results
    # --------------------------------------------

    print_report(
        before_dtypes,
        after_dtypes,
        conversion_logs,
        validation_results,
        dtype_changes
    )

    print(
        f"\nType-enforced dataset saved to:"
        f"\n{OUTPUT_FILE}"
    )

    print(
        f"\nType enforcement report saved to:"
        f"\n{REPORT_FILE}"
    )

    print(
        "\nData type enforcement completed successfully."
    )


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()