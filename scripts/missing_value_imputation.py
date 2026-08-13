import json
import os

import pandas as pd


# ==========================================
# Configuration
# ==========================================

INPUT_FILE = "data/raw/delivery_profiling_dataset.xlsx"

OUTPUT_FILE = "output/imputed_deliveries.csv"

AUDIT_FILE = "output/imputation_audit.json"


# ==========================================
# Load Dataset
# ==========================================

def load_dataset(filepath):
    """
    Load the delivery dataset from Excel.

    Args:
        filepath (str): Path to the input Excel file.

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
# Analyze Missing Values
# ==========================================

def analyze_missing_before(df):
    """
    Analyze and report missing values before treatment.

    Args:
        df (pandas.DataFrame): Input dataset.

    Returns:
        dict: Missing-value information.
    """

    missing = {}

    print("\nBEFORE IMPUTATION")
    print("=" * 60)

    for column in df.columns:

        null_count = int(
            df[column].isnull().sum()
        )

        null_percentage = (
            (null_count / len(df)) * 100
            if len(df) > 0
            else 0
        )

        if null_count > 0:

            missing[column] = {
                "null_count": null_count,
                "null_percentage": round(
                    null_percentage,
                    2
                )
            }

            print(
                f"{column}: "
                f"{null_count} nulls "
                f"({null_percentage:.2f}%)"
            )

    if not missing:
        print("No missing values found.")

    return missing


# ==========================================
# Calculate Missing Values After Treatment
# ==========================================

def analyze_missing_after(df):
    """
    Analyze missing values after imputation.

    Args:
        df (pandas.DataFrame): Dataset after treatment.

    Returns:
        dict: Remaining missing-value information.
    """

    missing = {}

    for column in df.columns:

        null_count = int(
            df[column].isnull().sum()
        )

        null_percentage = (
            (null_count / len(df)) * 100
            if len(df) > 0
            else 0
        )

        if null_count > 0:

            missing[column] = {
                "null_count": null_count,
                "null_percentage": round(
                    null_percentage,
                    2
                )
            }

    return missing


# ==========================================
# Impute Numerical Columns
# ==========================================

def impute_numerical_column(df, column):
    """
    Fill missing numerical values using the median.

    Median is used because it is less affected by
    extreme values and is appropriate for numerical
    delivery metrics.

    Args:
        df (pandas.DataFrame): Dataset.
        column (str): Numerical column.

    Returns:
        pandas.DataFrame: Updated dataset.
        dict: Audit information.
    """

    if column not in df.columns:
        raise KeyError(
            f"Column not found: {column}"
        )

    before_count = int(
        df[column].isnull().sum()
    )

    median_value = df[column].median()

    df[column] = df[column].fillna(
        median_value
    )

    after_count = int(
        df[column].isnull().sum()
    )

    filled_count = (
        before_count - after_count
    )

    return df, {
        "column": column,
        "strategy": "median",
        "before_nulls": before_count,
        "after_nulls": after_count,
        "values_imputed": filled_count,
        "imputation_value": (
            float(median_value)
            if pd.notna(median_value)
            else None
        ),
        "reason": (
            "Median was selected for the numerical "
            "delivery metric because it is resistant "
            "to extreme values."
        )
    }


# ==========================================
# Impute Categorical Columns
# ==========================================

def impute_categorical_column(df, column):
    """
    Fill missing categorical values using the mode.

    Args:
        df (pandas.DataFrame): Dataset.
        column (str): Categorical column.

    Returns:
        pandas.DataFrame: Updated dataset.
        dict: Audit information.
    """

    if column not in df.columns:
        raise KeyError(
            f"Column not found: {column}"
        )

    before_count = int(
        df[column].isnull().sum()
    )

    mode_values = df[column].mode()

    if mode_values.empty:
        raise ValueError(
            f"Cannot determine mode for column: {column}"
        )

    mode_value = mode_values.iloc[0]

    df[column] = df[column].fillna(
        mode_value
    )

    after_count = int(
        df[column].isnull().sum()
    )

    filled_count = (
        before_count - after_count
    )

    return df, {
        "column": column,
        "strategy": "mode",
        "before_nulls": before_count,
        "after_nulls": after_count,
        "values_imputed": filled_count,
        "imputation_value": str(mode_value),
        "reason": (
            "Mode was selected for the categorical "
            "column because it preserves the most "
            "common category."
        )
    }


# ==========================================
# Critical Identifier Check
# ==========================================

def handle_critical_ids(df, critical_columns):
    """
    Check critical identifier columns for missing values.

    Critical identifiers cannot be safely imputed.
    If an identifier is missing, the affected rows
    are dropped and the decision is recorded.

    Args:
        df (pandas.DataFrame): Dataset.
        critical_columns (list): Critical ID columns.

    Returns:
        pandas.DataFrame: Updated dataset.
        list: Audit information.
    """

    audit = []

    for column in critical_columns:

        if column not in df.columns:
            continue

        before_count = int(
            df[column].isnull().sum()
        )

        if before_count == 0:

            audit.append({
                "column": column,
                "strategy": "no_action",
                "before_nulls": 0,
                "after_nulls": 0,
                "rows_dropped": 0,
                "reason": (
                    "No missing critical identifiers "
                    "were found."
                )
            })

            continue

        df = df.dropna(
            subset=[column]
        )

        after_count = int(
            df[column].isnull().sum()
        )

        audit.append({
            "column": column,
            "strategy": "drop_rows",
            "before_nulls": before_count,
            "after_nulls": after_count,
            "rows_dropped": (
                before_count - after_count
            ),
            "reason": (
                "Critical identifiers cannot be "
                "reliably imputed because they are "
                "required to trace a delivery record."
            )
        })

    return df, audit


# ==========================================
# Generate Audit Report
# ==========================================

def generate_audit_report(
    before_missing,
    after_missing,
    imputation_decisions,
    critical_id_decisions,
    original_row_count,
    final_row_count
):
    """
    Generate a complete audit report for missing-value treatment.
    """

    rows_removed = (
        original_row_count - final_row_count
    )

    return {
        "timestamp": pd.Timestamp.now().isoformat(),

        "source": INPUT_FILE,

        "strategy_summary": {
            "numerical": "median",
            "categorical": "mode",
            "time_series": "forward_fill_not_required",
            "critical_identifiers": "drop_rows_if_missing"
        },

        "before_imputation": before_missing,

        "imputation_decisions": imputation_decisions,

        "critical_identifier_decisions": (
            critical_id_decisions
        ),

        "after_imputation": after_missing,

        "impact": {
            "original_rows": original_row_count,
            "final_rows": final_row_count,
            "rows_removed": rows_removed
        },

        "all_missing_values_handled": (
            len(after_missing) == 0
        )
    }


# ==========================================
# Save Audit Report
# ==========================================

def save_audit_report(report, filepath):
    """
    Save the imputation audit report as JSON.
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
# Save Imputed Dataset
# ==========================================

def save_dataset(df, filepath):
    """
    Save the imputed dataset as CSV.
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
    before_missing,
    after_missing,
    imputation_decisions,
    critical_id_decisions,
    original_row_count,
    final_row_count
):
    """
    Print a readable summary of the imputation process.
    """

    print("\n" + "=" * 60)
    print("MISSING VALUE IMPUTATION REPORT")
    print("=" * 60)

    print("\nMissing Values Before Treatment:")

    if before_missing:

        for column, values in before_missing.items():

            print(
                f"  {column}: "
                f"{values['null_count']} nulls "
                f"({values['null_percentage']}%)"
            )

    else:
        print("  No missing values.")

    print("\nImputation Decisions:")

    for decision in imputation_decisions:

        print(
            f"  {decision['column']}: "
            f"{decision['strategy']} "
            f"-> {decision['values_imputed']} "
            f"values filled"
        )

        print(
            f"    Imputation value: "
            f"{decision['imputation_value']}"
        )

    print("\nCritical Identifier Decisions:")

    for decision in critical_id_decisions:

        print(
            f"  {decision['column']}: "
            f"{decision['strategy']} "
            f"-> {decision.get('rows_dropped', 0)} "
            f"rows removed"
        )

    print("\nMissing Values After Treatment:")

    if after_missing:

        for column, values in after_missing.items():

            print(
                f"  {column}: "
                f"{values['null_count']} nulls"
            )

    else:
        print("  No missing values remain.")

    rows_removed = (
        original_row_count - final_row_count
    )

    print(
        f"\nRows before treatment: "
        f"{original_row_count}"
    )

    print(
        f"Rows after treatment: "
        f"{final_row_count}"
    )

    print(
        f"Rows removed: "
        f"{rows_removed}"
    )

    print("=" * 60)


# ==========================================
# Main
# ==========================================

def main():
    """
    Execute the complete missing-value workflow.
    """

    print(
        "\nStarting Missing Value Detection "
        "& Imputation..."
    )

    # --------------------------------------
    # Load dataset
    # --------------------------------------

    df = load_dataset(
        INPUT_FILE
    )

    original_row_count = len(df)

    # --------------------------------------
    # Analyze missing values
    # --------------------------------------

    before_missing = analyze_missing_before(
        df
    )

    # --------------------------------------
    # Handle critical identifiers
    # --------------------------------------

    critical_columns = [
        "delivery_id",
        "rider_id"
    ]

    df, critical_id_decisions = (
        handle_critical_ids(
            df,
            critical_columns
        )
    )

    # --------------------------------------
    # Numerical imputation
    # --------------------------------------

    imputation_decisions = []

    if "delivery_time_min" in df.columns:

        df, decision = impute_numerical_column(
            df,
            "delivery_time_min"
        )

        imputation_decisions.append(
            decision
        )

    # --------------------------------------
    # Categorical imputation
    # --------------------------------------

    if "delivery_status" in df.columns:

        df, decision = impute_categorical_column(
            df,
            "delivery_status"
        )

        imputation_decisions.append(
            decision
        )

    if "complaint" in df.columns:

        df, decision = impute_categorical_column(
            df,
            "complaint"
        )

        imputation_decisions.append(
            decision
        )

    # --------------------------------------
    # Analyze after treatment
    # --------------------------------------

    after_missing = analyze_missing_after(
        df
    )

    final_row_count = len(df)

    # --------------------------------------
    # Generate audit report
    # --------------------------------------

    report = generate_audit_report(
        before_missing,
        after_missing,
        imputation_decisions,
        critical_id_decisions,
        original_row_count,
        final_row_count
    )

    # --------------------------------------
    # Save outputs
    # --------------------------------------

    save_dataset(
        df,
        OUTPUT_FILE
    )

    save_audit_report(
        report,
        AUDIT_FILE
    )

    # --------------------------------------
    # Print results
    # --------------------------------------

    print_summary(
        before_missing,
        after_missing,
        imputation_decisions,
        critical_id_decisions,
        original_row_count,
        final_row_count
    )

    print(
        f"\nImputed dataset saved to:"
        f"\n{OUTPUT_FILE}"
    )

    print(
        f"\nImputation audit saved to:"
        f"\n{AUDIT_FILE}"
    )

    print(
        "\nMissing value handling completed successfully."
    )


# ==========================================
# Script Entry Point
# ==========================================

if __name__ == "__main__":
    main()