import json
from datetime import datetime
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

INPUT_FILE = Path(
    "data/raw/delivery_profiling_dataset.xlsx"
)

OUTPUT_DATASET = Path(
    "output/deduplicated_deliveries.csv"
)

OUTPUT_AUDIT = Path(
    "output/removed_duplicates_audit.csv"
)

OUTPUT_REPORT = Path(
    "output/deduplication_report.json"
)


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

def load_dataset(filepath):
    """Load the source delivery dataset."""

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
# Detect exact duplicates
# ---------------------------------------------------------

def detect_exact_duplicates(df):
    """
    Detect rows where every column is identical.
    """

    duplicate_mask = df.duplicated(
        keep=False
    )

    duplicates = df[duplicate_mask].copy()

    exact_duplicate_count = df.duplicated().sum()

    return duplicates, exact_duplicate_count


# ---------------------------------------------------------
# Detect near duplicates
# ---------------------------------------------------------

def detect_near_duplicates(
    df,
    key_columns
):
    """
    Detect records that share the same business key.

    The default strategy uses delivery_id.
    """

    missing_columns = [
        column
        for column in key_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise KeyError(
            f"Missing key columns: {missing_columns}"
        )

    duplicate_mask = df.duplicated(
        subset=key_columns,
        keep=False
    )

    duplicates = df[duplicate_mask].copy()

    near_duplicate_count = df.duplicated(
        subset=key_columns
    ).sum()

    return duplicates, near_duplicate_count


# ---------------------------------------------------------
# Remove exact duplicates
# ---------------------------------------------------------

def remove_exact_duplicates(df):
    """
    Remove exact duplicate rows while keeping
    the first occurrence.
    """

    return df.drop_duplicates(
        keep="first"
    ).copy()


# ---------------------------------------------------------
# Remove near duplicates
# ---------------------------------------------------------

def remove_near_duplicates(
    df,
    key_columns
):
    """
    Remove duplicate business keys while keeping
    the first occurrence.

    The keep-first strategy is used because the
    original occurrence is treated as the primary record.
    """

    return df.drop_duplicates(
        subset=key_columns,
        keep="first"
    ).copy()


# ---------------------------------------------------------
# Find removed records
# ---------------------------------------------------------

def find_removed_records(
    original_df,
    cleaned_df
):
    """
    Return records that were removed during
    deduplication.
    """

    removed = original_df[
        ~original_df.index.isin(
            cleaned_df.index
        )
    ].copy()

    return removed


# ---------------------------------------------------------
# Calculate comparison metrics
# ---------------------------------------------------------

def calculate_comparison(
    original_df,
    cleaned_df
):
    """Calculate before/after deduplication metrics."""

    rows_before = len(original_df)
    rows_after = len(cleaned_df)

    rows_removed = (
        rows_before - rows_after
    )

    if rows_before > 0:
        removal_pct = round(
            (rows_removed / rows_before) * 100,
            2
        )
    else:
        removal_pct = 0.0

    return {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "rows_removed": rows_removed,
        "removal_pct": removal_pct
    }


# ---------------------------------------------------------
# Generate audit report
# ---------------------------------------------------------

def generate_report(
    filepath,
    original_df,
    cleaned_df,
    exact_duplicate_count,
    near_duplicate_count,
    comparison,
    key_columns
):
    """Create the final deduplication audit report."""

    report = {
        "timestamp": datetime.now().isoformat(),

        "source": str(filepath),

        "dataset": {
            "rows_before": len(original_df),
            "columns": len(original_df.columns),
            "column_names": list(original_df.columns)
        },

        "duplicate_detection": {
            "exact_duplicate_rows": int(
                exact_duplicate_count
            ),
            "near_duplicate_rows": int(
                near_duplicate_count
            ),
            "near_duplicate_key": key_columns
        },

        "deduplication_strategy": {
            "exact_duplicates": "keep_first",
            "near_duplicates": "keep_first",
            "reason": (
                "Keep the first occurrence because "
                "the original record is treated as "
                "the primary record."
            )
        },

        "comparison": comparison,

        "validation": {
            "exact_duplicates_remaining": int(
                cleaned_df.duplicated().sum()
            ),
            "near_duplicates_remaining": int(
                cleaned_df.duplicated(
                    subset=key_columns
                ).sum()
            )
        }
    }

    return report


# ---------------------------------------------------------
# Main workflow
# ---------------------------------------------------------

def main():

    print(
        "\nStarting Duplicate Detection "
        "& Record Deduplication...\n"
    )

    # Load dataset
    df = load_dataset(
        INPUT_FILE
    )

    print(
        f"Dataset loaded: {INPUT_FILE}"
    )

    print(
        f"Rows before deduplication: {len(df)}"
    )

    # Preserve original dataset
    original_df = df.copy()

    # -----------------------------------------------------
    # Exact duplicate detection
    # -----------------------------------------------------

    exact_duplicates, exact_count = (
        detect_exact_duplicates(df)
    )

    print(
        f"\nExact duplicate rows detected: "
        f"{exact_count}"
    )

    # -----------------------------------------------------
    # Near duplicate detection
    # -----------------------------------------------------

    key_columns = [
        "delivery_id"
    ]

    near_duplicates, near_count = (
        detect_near_duplicates(
            df,
            key_columns
        )
    )

    print(
        f"Near-duplicate records detected: "
        f"{near_count}"
    )

    # -----------------------------------------------------
    # Deduplicate exact duplicates
    # -----------------------------------------------------

    df = remove_exact_duplicates(
        df
    )

    # -----------------------------------------------------
    # Deduplicate near duplicates
    # -----------------------------------------------------

    df = remove_near_duplicates(
        df,
        key_columns
    )

    # -----------------------------------------------------
    # Find removed records
    # -----------------------------------------------------

    removed_records = find_removed_records(
        original_df,
        df
    )

    # -----------------------------------------------------
    # Comparison metrics
    # -----------------------------------------------------

    comparison = calculate_comparison(
        original_df,
        df
    )

    # -----------------------------------------------------
    # Create output directories
    # -----------------------------------------------------

    OUTPUT_DATASET.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_AUDIT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_REPORT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Save deduplicated dataset
    # -----------------------------------------------------

    df.to_csv(
        OUTPUT_DATASET,
        index=False
    )

    # -----------------------------------------------------
    # Save removed records audit
    # -----------------------------------------------------

    removed_records.to_csv(
        OUTPUT_AUDIT,
        index=False
    )

    # -----------------------------------------------------
    # Generate report
    # -----------------------------------------------------

    report = generate_report(
        INPUT_FILE,
        original_df,
        df,
        exact_count,
        near_count,
        comparison,
        key_columns
    )

    # -----------------------------------------------------
    # Save JSON report
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # Display final results
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print(
        "DUPLICATE DETECTION & "
        "DEDUPLICATION REPORT"
    )
    print("=" * 60)

    print(
        f"\nRows before: "
        f"{comparison['rows_before']}"
    )

    print(
        f"Rows after: "
        f"{comparison['rows_after']}"
    )

    print(
        f"Rows removed: "
        f"{comparison['rows_removed']}"
    )

    print(
        f"Removal percentage: "
        f"{comparison['removal_pct']}%"
    )

    print(
        "\nDeduplication Strategy:"
    )

    print(
        "  Exact duplicates: Keep first"
    )

    print(
        "  Near duplicates: Keep first"
    )

    print(
        f"\nRemoved records saved to:"
        f"\n{OUTPUT_AUDIT}"
    )

    print(
        f"\nDeduplicated dataset saved to:"
        f"\n{OUTPUT_DATASET}"
    )

    print(
        f"\nAudit report saved to:"
        f"\n{OUTPUT_REPORT}"
    )

    print(
        "\nDuplicate detection and "
        "deduplication completed successfully."
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()