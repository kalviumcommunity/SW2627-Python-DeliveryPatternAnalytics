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
    "output/cleaned_deliveries.csv"
)

OUTPUT_REPORT = Path(
    "output/string_cleaning_report.json"
)


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

def load_dataset(filepath):
    """Load the delivery dataset."""

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
# Reusable text cleaning function
# ---------------------------------------------------------

def clean_text_column(
    series,
    lowercase=True,
    strip=True,
    remove_special=False,
    mapping=None
):
    """
    Reusable text cleaning function.

    Parameters:
        series: Pandas Series
        lowercase: convert text to lowercase
        strip: remove leading/trailing whitespace
        remove_special: remove unwanted special characters
        mapping: dictionary for standardising values
    """

    result = series.copy()

    # Convert values to pandas string type
    result = result.astype("string")

    # Remove leading/trailing whitespace
    if strip:
        result = result.str.strip()

    # Normalize casing
    if lowercase:
        result = result.str.lower()

    # Remove unwanted special characters
    if remove_special:
        result = result.str.replace(
            r"[^a-zA-Z0-9 ]",
            "",
            regex=True
        )

    # Standardize known variations
    if mapping:
        result = result.replace(mapping)

    return result


# ---------------------------------------------------------
# Count changes
# ---------------------------------------------------------

def count_changes(before, after):
    """Count values that changed after cleaning."""

    comparison = (
        before.astype("string")
        != after.astype("string")
    )

    comparison = comparison.fillna(False)

    return int(comparison.sum())


# ---------------------------------------------------------
# Clean customer names
# ---------------------------------------------------------

def clean_customer_names(df):
    """Clean customer names."""

    before = df["customer_name"].copy()

    # Strip leading/trailing whitespace
    df["customer_name"] = (
        df["customer_name"]
        .astype("string")
        .str.strip()
    )

    # Collapse multiple spaces into one
    df["customer_name"] = (
        df["customer_name"]
        .str.replace(r"\s+", " ", regex=True)
    )

    # Standardize casing while preserving readable names
    df["customer_name"] = (
        df["customer_name"]
        .str.title()
    )

    changes = count_changes(
        before,
        df["customer_name"]
    )

    return changes


# ---------------------------------------------------------
# Clean cities
# ---------------------------------------------------------

def clean_cities(df):
    """Clean city names."""

    before = df["city"].copy()

    city_mapping = {
        "delhi": "Delhi",
        "mumbai": "Mumbai",
        "bangalore": "Bangalore",
        "bengaluru": "Bangalore",
        "pune": "Pune",
        "chennai": "Chennai",
        "hyderabad": "Hyderabad"
    }

    df["city"] = clean_text_column(
        df["city"],
        lowercase=True,
        strip=True,
        remove_special=True,
        mapping=city_mapping
    )

    # Convert canonical values to title case
    df["city"] = df["city"].str.title()

    changes = count_changes(
        before,
        df["city"]
    )

    return changes


# ---------------------------------------------------------
# Clean delivery status
# ---------------------------------------------------------

def clean_delivery_status(df):
    """Standardize delivery status values."""

    before = df["delivery_status"].copy()

    status_mapping = {
        "on time": "On Time",
        "ontime": "On Time",
        "on-time": "On Time",
        "delayed": "Delayed"
    }

    df["delivery_status"] = clean_text_column(
        df["delivery_status"],
        lowercase=True,
        strip=True,
        remove_special=False,
        mapping=status_mapping
    )

    changes = count_changes(
        before,
        df["delivery_status"]
    )

    return changes


# ---------------------------------------------------------
# Clean complaint values
# ---------------------------------------------------------

def clean_complaint(df):
    """Standardize complaint values."""

    before = df["complaint"].copy()

    complaint_mapping = {
        "yes": "Yes",
        "no": "No"
    }

    df["complaint"] = clean_text_column(
        df["complaint"],
        lowercase=True,
        strip=True,
        remove_special=False,
        mapping=complaint_mapping
    )

    changes = count_changes(
        before,
        df["complaint"]
    )

    return changes


# ---------------------------------------------------------
# Clean payment methods
# ---------------------------------------------------------

def clean_payment_methods(df):
    """Standardize payment method values."""

    before = df["payment_method"].copy()

    payment_mapping = {
        "upi": "UPI",
        "card": "Card",
        "cash": "Cash"
    }

    df["payment_method"] = clean_text_column(
        df["payment_method"],
        lowercase=True,
        strip=True,
        remove_special=False,
        mapping=payment_mapping
    )

    changes = count_changes(
        before,
        df["payment_method"]
    )

    return changes


# ---------------------------------------------------------
# Generate value distributions
# ---------------------------------------------------------

def get_distributions(df, columns):
    """Return value counts for selected text columns."""

    distributions = {}

    for column in columns:
        if column not in df.columns:
            continue

        counts = (
            df[column]
            .astype("string")
            .value_counts(dropna=False)
        )

        distributions[column] = {
            str(key): int(value)
            for key, value in counts.items()
        }

    return distributions


# ---------------------------------------------------------
# Main cleaning workflow
# ---------------------------------------------------------

def main():

    print(
        "\nStarting String Cleaning "
        "& Text Normalisation...\n"
    )

    # Load dataset
    df = load_dataset(
        INPUT_FILE
    )

    print(
        f"Dataset loaded: {INPUT_FILE}"
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    # Preserve original values for reporting
    original_df = df.copy()

    # Columns being cleaned
    text_columns = [
        "customer_name",
        "city",
        "delivery_status",
        "complaint",
        "payment_method"
    ]

    # Capture distributions before cleaning
    distributions_before = get_distributions(
        original_df,
        text_columns
    )

    # -----------------------------------------------------
    # Apply cleaning
    # -----------------------------------------------------

    changes = {}

    changes["customer_name"] = clean_customer_names(df)

    changes["city"] = clean_cities(df)

    changes["delivery_status"] = clean_delivery_status(df)

    changes["complaint"] = clean_complaint(df)

    changes["payment_method"] = clean_payment_methods(df)

    # -----------------------------------------------------
    # Capture distributions after cleaning
    # -----------------------------------------------------

    distributions_after = get_distributions(
        df,
        text_columns
    )

    # -----------------------------------------------------
    # Calculate total changes
    # -----------------------------------------------------

    total_changes = sum(
        changes.values()
    )

    # -----------------------------------------------------
    # Create output directory
    # -----------------------------------------------------

    OUTPUT_DATASET.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_REPORT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Save cleaned dataset
    # -----------------------------------------------------

    df.to_csv(
        OUTPUT_DATASET,
        index=False
    )

    # -----------------------------------------------------
    # Create report
    # -----------------------------------------------------

    report = {
        "timestamp": datetime.now().isoformat(),

        "source": str(INPUT_FILE),

        "dataset": {
            "rows": len(df),
            "columns": len(df.columns)
        },

        "cleaning_operations": {
            "customer_name": [
                "strip whitespace"
            ],
            "city": [
                "strip whitespace",
                "normalize casing",
                "remove special characters",
                "standardize city names"
            ],
            "delivery_status": [
                "strip whitespace",
                "normalize casing",
                "standardize status labels"
            ],
            "complaint": [
                "strip whitespace",
                "normalize casing",
                "standardize Yes/No labels"
            ],
            "payment_method": [
                "strip whitespace",
                "normalize casing",
                "standardize payment labels"
            ]
        },

        "changes": changes,

        "total_values_changed": total_changes,

        "value_distributions_before": (
            distributions_before
        ),

        "value_distributions_after": (
            distributions_after
        )
    }

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
    # Display results
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print(
        "STRING CLEANING & TEXT NORMALISATION REPORT"
    )
    print("=" * 60)

    print("\nValues changed:")

    for column, count in changes.items():
        print(
            f"  {column}: {count}"
        )

    print(
        f"\nTotal values changed: "
        f"{total_changes}"
    )

    print(
        f"\nCleaned dataset saved to:"
        f"\n{OUTPUT_DATASET}"
    )

    print(
        f"\nCleaning report saved to:"
        f"\n{OUTPUT_REPORT}"
    )

    print(
        "\nString cleaning and text "
        "normalisation completed successfully."
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()