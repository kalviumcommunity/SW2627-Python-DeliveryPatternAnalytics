import json
import os
import pandas as pd

# ==========================================
# Configuration
# ==========================================

INPUT_FILE = "data/raw/delivery_profiling_dataset.xlsx"
OUTPUT_FILE = "output/type_enforcement_report.json"
PROCESSED_FILE = "output/type_enforced_deliveries.csv"


# ==========================================
# Load Dataset
# ==========================================

def load_dataset(filepath):
    """
    Load the delivery dataset from Excel.

    Args:
        filepath (str): Path to the Excel dataset.

    Returns:
        pandas.DataFrame: Loaded dataset.
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


# ==========================================
# Capture Original Data Types
# ==========================================

def capture_dtypes(df):
    """
    Capture the original data types of all columns.

    Args:
        df (pandas.DataFrame): Input dataset.

    Returns:
        dict: Column names and their original data types.
    """

    return {
        column: str(dtype)
        for column, dtype in df.dtypes.items()
    }


# ==========================================
# Enforce Date Type
# ==========================================

def enforce_date_type(df):
    """
    Convert delivery_date to datetime.

    The source Excel file contains dates in YYYY-MM-DD format.
    An explicit format is used to avoid relying on automatic
    date inference.

    Args:
        df (pandas.DataFrame): Input dataset.

    Returns:
        pandas.DataFrame: Dataset with enforced date type.
        dict: Conversion details.
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
            converted_values.append(
                pd.to_datetime(
                    value,
                    format="%Y-%m-%d"
                )
            )

        except (ValueError, TypeError):
            conversion_errors.append(str(value))
            converted_values.append(pd.NaT)

    df[column] = converted_values

    after_type = str(df[column].dtype)

    return df, {
        "column": column,
        "before": before_type,
        "after": after_type,
        "format": "%Y-%m-%d",
        "conversion_errors": conversion_errors
    }


# ==========================================
# Enforce Currency Type
# ==========================================

def enforce_currency_type(df):
    """
    Convert refund_amount into a numeric float.

    Currency symbols and commas are removed before conversion.

    The delivery dataset currently contains numeric refund
    values, but this function also supports values such as
    '$150.50' or '$1,250.00'.

    Args:
        df (pandas.DataFrame): Input dataset.

    Returns:
        pandas.DataFrame: Dataset with enforced numeric refund.
        dict: Conversion details.
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

    converted_values = pd.to_numeric(
        cleaned_values,
        errors="coerce"
    )

    conversion_errors = []

    for original, converted in zip(
        original_values,
        converted_values
    ):
        if (
            pd.notna(original)
            and pd.isna(converted)
        ):
            conversion_errors.append(
                str(original)
            )

    df[column] = converted_values.astype(float)

    after_type = str(df[column].dtype)

    return df, {
        "column": column,
        "before": before_type,
        "after": after_type,
        "conversion_errors": conversion_errors
    }


# ==========================================
# Enforce Boolean Type
# ==========================================

def enforce_boolean_type(df):
    """
    Convert complaint values into proper Boolean values.

    Supported values:
        Yes -> True
        No  -> False

    Missing values remain missing.

    Args:
        df (pandas.DataFrame): Input dataset.

    Returns:
        pandas.DataFrame: Dataset with Boolean complaint values.
        dict: Conversion details.
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
        "1": True,
        "0": False,
        "true": True,
        "false": False
    }

    conversion_errors = []

    converted_values = []

    for value in df[column]:

        if pd.isna(value):
            converted_values.append(pd.NA)
            continue

        normalized_value = str(value).strip().lower()

        if normalized_value in mapping:
            converted_values.append(
                mapping[normalized_value]
            )
        else:
            conversion_errors.append(str(value))
            converted_values.append(pd.NA)

    df[column] = pd.Series(
        converted_values,
        index=df.index,
        dtype="boolean"
    )

    after_type = str(df[column].dtype)

    return df, {
        "column": column,
        "before": before_type,
        "after": after_type,
        "mapping": mapping,
        "conversion_errors": conversion_errors
    }


# ==========================================
# Validate Data Types
# ==========================================

def validate_types(df):
    """
    Validate that required columns have the expected types.

    Returns:
        dict: Validation results.
    """

    results = {}

    results["delivery_date"] = {
        "expected": "datetime64[ns]",
        "actual": str(df["delivery_date"].dtype),
        "valid": pd.api.types.is_datetime64_any_dtype(
            df["delivery_date"]
        )
    }

    results["refund_amount"] = {
        "expected": "float64",
        "actual": str(df["refund_amount"].dtype),
        "valid": pd.api.types.is_float_dtype(
            df["refund_amount"]
        )
    }

    results["complaint"] = {
        "expected": "boolean",
        "actual": str(df["complaint"].dtype),
        "valid": str(df["complaint"].dtype) == "boolean"
    }

    return results


# ==========================================
# Compare Data Types
# ==========================================

def compare_dtypes(before, after):
    """
    Compare data types before and after enforcement.

    Args:
        before (dict): Original types.
        after (dict): Final types.

    Returns:
        dict: Type changes.
    """

    changes = {}

    for column in after:

        before_type = before.get(
            column,
            "not present"
        )

        after_type = after[column]

        if before_type != after_type:

            changes[column] = {
                "before": before_type,
                "after": after_type
            }

    return changes


# ==========================================
# Generate Type Enforcement Report
# ==========================================

def generate_report(
    before_dtypes,
    after_dtypes,
    conversion_results,
    validation_results,
    dtype_changes
):
    """
    Create a structured type-enforcement report.
    """

    return {
        "timestamp": pd.Timestamp.now().isoformat(),

        "source": INPUT_FILE,

        "conversions": conversion_results,

        "dtype_changes": dtype_changes,

        "validation": validation_results,

        "all_required_types_valid": all(
            result["valid"]
            for result in validation_results.values()
        ),

        "before_dtypes": before_dtypes,

        "after_dtypes": after_dtypes
    }


# ==========================================
# Save JSON Report
# ==========================================

def save_report(report, filepath):
    """
    Save the type enforcement report as JSON.
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


# ==========================================
# Save Processed Dataset
# ==========================================

def save_processed_dataset(df, filepath):
    """
    Save the type-enforced dataset as CSV.
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


# ==========================================
# Print Summary
# ==========================================

def print_summary(
    before_dtypes,
    after_dtypes,
    conversion_results,
    validation_results,
    dtype_changes
):
    """
    Print a readable type enforcement summary.
    """

    print("\n" + "=" * 60)
    print("TYPE ENFORCEMENT REPORT")
    print("=" * 60)

    print("\nData Type Changes:")

    if dtype_changes:

        for column, change in dtype_changes.items():

            print(
                f"  {column}: "
                f"{change['before']} -> "
                f"{change['after']}"
            )

    else:
        print("  No data type changes detected.")

    print("\nConversions:")

    for conversion in conversion_results:

        print(
            f"  {conversion['column']}: "
            f"{conversion['before']} -> "
            f"{conversion['after']}"
        )

        if conversion["conversion_errors"]:

            print(
                "    Conversion errors: "
                f"{conversion['conversion_errors']}"
            )

    print("\nValidation:")

    for column, result in validation_results.items():

        status = (
            "PASS"
            if result["valid"]
            else "FAIL"
        )

        print(
            f"  {column}: {status} "
            f"(expected={result['expected']}, "
            f"actual={result['actual']})"
        )

    print("\nOriginal Data Types:")

    for column, dtype in before_dtypes.items():

        print(
            f"  {column}: {dtype}"
        )

    print("\nFinal Data Types:")

    for column, dtype in after_dtypes.items():

        print(
            f"  {column}: {dtype}"
        )

    print("=" * 60)


# ==========================================
# Main
# ==========================================

def main():
    """
    Execute the complete type enforcement workflow.
    """

    print(
        "\nStarting Type Enforcement..."
    )

    # --------------------------------------
    # Load dataset
    # --------------------------------------

    df = load_dataset(
        INPUT_FILE
    )

    # --------------------------------------
    # Capture original types
    # --------------------------------------

    before_dtypes = capture_dtypes(
        df
    )

    conversion_results = []

    # --------------------------------------
    # Date conversion
    # --------------------------------------

    df, date_result = enforce_date_type(
        df
    )

    conversion_results.append(
        date_result
    )

    # --------------------------------------
    # Currency conversion
    # --------------------------------------

    df, currency_result = enforce_currency_type(
        df
    )

    conversion_results.append(
        currency_result
    )

    # --------------------------------------
    # Boolean conversion
    # --------------------------------------

    df, boolean_result = enforce_boolean_type(
        df
    )

    conversion_results.append(
        boolean_result
    )

    # --------------------------------------
    # Capture final types
    # --------------------------------------

    after_dtypes = capture_dtypes(
        df
    )

    # --------------------------------------
    # Compare types
    # --------------------------------------

    dtype_changes = compare_dtypes(
        before_dtypes,
        after_dtypes
    )

    # --------------------------------------
    # Validate conversions
    # --------------------------------------

    validation_results = validate_types(
        df
    )

    # --------------------------------------
    # Generate report
    # --------------------------------------

    report = generate_report(
        before_dtypes,
        after_dtypes,
        conversion_results,
        validation_results,
        dtype_changes
    )

    # --------------------------------------
    # Save report
    # --------------------------------------

    save_report(
        report,
        OUTPUT_FILE
    )

    # --------------------------------------
    # Save processed dataset
    # --------------------------------------

    save_processed_dataset(
        df,
        PROCESSED_FILE
    )

    # --------------------------------------
    # Print summary
    # --------------------------------------

    print_summary(
        before_dtypes,
        after_dtypes,
        conversion_results,
        validation_results,
        dtype_changes
    )

    print(
        f"\nType enforcement report saved to:"
        f"\n{OUTPUT_FILE}"
    )

    print(
        f"\nType-enforced dataset saved to:"
        f"\n{PROCESSED_FILE}"
    )

    print(
        "\nType enforcement completed successfully."
    )


# ==========================================
# Script Entry Point
# ==========================================

if __name__ == "__main__":
    main()