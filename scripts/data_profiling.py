import json
import os

import pandas as pd


# ==========================================
# Configuration
# ==========================================

INPUT_FILE = "data/raw/delivery_profiling_dataset.xlsx"
OUTPUT_FILE = "output/profiling_report.json"

NULL_THRESHOLD = 30
DUPLICATE_THRESHOLD = 5


# ==========================================
# Load Dataset
# ==========================================

def load_dataset(filepath):
    """
    Load the profiling dataset from an Excel file.

    Args:
        filepath (str): Path to the Excel dataset.

    Returns:
        pandas.DataFrame: Loaded dataset.

    Raises:
        FileNotFoundError: If the dataset does not exist.
        ValueError: If the dataset is empty.
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
# Profile Nulls and Duplicates
# ==========================================

def profile_nulls_and_duplicates(df):
    """
    Calculate null counts and percentages for every column
    and calculate the number of exact duplicate rows.

    Args:
        df (pandas.DataFrame): Dataset to profile.

    Returns:
        dict: Null and duplicate metrics.
    """

    profile = {}

    for column in df.columns:
        null_count = int(df[column].isnull().sum())
        null_percentage = (
            (null_count / len(df)) * 100
            if len(df) > 0
            else 0
        )

        profile[column] = {
            "nulls": null_count,
            "null_%": round(null_percentage, 2)
        }

    duplicate_count = int(df.duplicated().sum())

    duplicate_percentage = (
        (duplicate_count / len(df)) * 100
        if len(df) > 0
        else 0
    )

    profile["exact_duplicates"] = {
        "count": duplicate_count,
        "percentage": round(duplicate_percentage, 2)
    }

    return profile


# ==========================================
# Numerical Profiling
# ==========================================

def profile_numerical(df):
    """
    Generate statistical summaries for numerical columns.

    Args:
        df (pandas.DataFrame): Dataset to profile.

    Returns:
        dict: Numerical statistics.
    """

    statistics = {}

    numerical_columns = df.select_dtypes(
        include=["number"]
    ).columns

    for column in numerical_columns:

        statistics[column] = {
            "min": (
                float(df[column].min())
                if pd.notna(df[column].min())
                else None
            ),
            "max": (
                float(df[column].max())
                if pd.notna(df[column].max())
                else None
            ),
            "mean": (
                round(float(df[column].mean()), 2)
                if pd.notna(df[column].mean())
                else None
            ),
            "median": (
                float(df[column].median())
                if pd.notna(df[column].median())
                else None
            )
        }

    return statistics


# ==========================================
# Value Distribution Profiling
# ==========================================

def profile_distributions(df):
    """
    Generate value distributions for categorical columns.

    Args:
        df (pandas.DataFrame): Dataset to profile.

    Returns:
        dict: Value distribution information.
    """

    distributions = {}

    categorical_columns = df.select_dtypes(
        include=["object", "string", "category", "bool"]
    ).columns

    for column in categorical_columns:

        value_counts = (
            df[column]
            .value_counts(dropna=False)
            .head(20)
        )

        distributions[column] = {
            str(value): int(count)
            for value, count in value_counts.items()
        }

    return distributions


# ==========================================
# Identify Quality Issues
# ==========================================

def identify_issues(
    df,
    null_threshold=NULL_THRESHOLD,
    dup_threshold=DUPLICATE_THRESHOLD
):
    """
    Identify columns with high null percentages and datasets
    with a high percentage of duplicate rows.

    Args:
        df (pandas.DataFrame): Dataset to inspect.
        null_threshold (float): Maximum acceptable null percentage.
        dup_threshold (float): Maximum acceptable duplicate percentage.

    Returns:
        list: Detected quality issues.
    """

    issues = []

    # --------------------------------------
    # High Null Values
    # --------------------------------------

    for column in df.columns:

        null_percentage = (
            df[column].isnull().sum() / len(df)
        ) * 100

        if null_percentage > null_threshold:

            issues.append({
                "column": column,
                "type": "High nulls",
                "value": f"{null_percentage:.1f}%",
                "threshold": f"{null_threshold}%"
            })

    # --------------------------------------
    # High Duplicate Values
    # --------------------------------------

    duplicate_percentage = (
        df.duplicated().sum() / len(df)
    ) * 100

    if duplicate_percentage > dup_threshold:

        issues.append({
            "type": "High duplicates",
            "value": f"{duplicate_percentage:.1f}%",
            "threshold": f"{dup_threshold}%"
        })

    # --------------------------------------
    # Negative Numeric Values
    # --------------------------------------

    numerical_columns = df.select_dtypes(
        include=["number"]
    ).columns

    for column in numerical_columns:

        negative_count = int(
            (df[column] < 0).sum()
        )

        if negative_count > 0:

            issues.append({
                "column": column,
                "type": "Negative values",
                "value": negative_count,
                "description": (
                    "Negative values may violate business "
                    "rules for this field."
                )
            })

    return issues


# ==========================================
# Generate Profiling Report
# ==========================================

def generate_profile_report(filepath):
    """
    Generate a complete dataset profiling report.

    Args:
        filepath (str): Path to the input dataset.

    Returns:
        dict: Complete profiling report.
    """

    df = load_dataset(filepath)

    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "source": filepath,

        "dataset": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "column_names": list(df.columns)
        },

        "nulls_and_duplicates": (
            profile_nulls_and_duplicates(df)
        ),

        "numerical_statistics": (
            profile_numerical(df)
        ),

        "value_distributions": (
            profile_distributions(df)
        ),

        "quality_issues": (
            identify_issues(df)
        )
    }

    return report


# ==========================================
# Save Report
# ==========================================

def save_report(report, filepath):
    """
    Save the profiling report as a JSON file.

    Args:
        report (dict): Profiling report.
        filepath (str): Output JSON path.
    """

    os.makedirs(
        os.path.dirname(filepath),
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
# Print Summary
# ==========================================

def print_summary(report):
    """
    Print a readable profiling summary.

    Args:
        report (dict): Profiling report.
    """

    print("\n" + "=" * 60)
    print("DATASET PROFILING & QUALITY REPORT")
    print("=" * 60)

    print(
        f"Source: {report['source']}"
    )

    print(
        f"Rows: {report['dataset']['rows']}"
    )

    print(
        f"Columns: {report['dataset']['columns']}"
    )

    print("\nNull Percentages:")

    null_profile = report[
        "nulls_and_duplicates"
    ]

    for column, values in null_profile.items():

        if column == "exact_duplicates":
            continue

        print(
            f"  {column}: "
            f"{values['null_%']}% "
            f"({values['nulls']} nulls)"
        )

    duplicate_info = null_profile[
        "exact_duplicates"
    ]

    print(
        "\nExact Duplicates: "
        f"{duplicate_info['count']} "
        f"({duplicate_info['percentage']}%)"
    )

    print("\nNumerical Statistics:")

    for column, stats in report[
        "numerical_statistics"
    ].items():

        print(
            f"  {column}: "
            f"min={stats['min']}, "
            f"max={stats['max']}, "
            f"mean={stats['mean']}, "
            f"median={stats['median']}"
        )

    print("\nQuality Issues:")

    if report["quality_issues"]:

        for issue in report["quality_issues"]:
            print(f"  - {issue}")

    else:
        print("  No issues exceeded the configured thresholds.")

    print("=" * 60)


# ==========================================
# Main
# ==========================================

def main():
    """
    Run the complete dataset profiling workflow.
    """

    print(
        "\nStarting Dataset Profiling & "
        "Quality Assessment...\n"
    )

    report = generate_profile_report(
        INPUT_FILE
    )

    save_report(
        report,
        OUTPUT_FILE
    )

    print_summary(report)

    print(
        f"\nProfiling report saved to:"
        f"\n{OUTPUT_FILE}"
    )

    print(
        "\nDataset profiling completed successfully."
    )


if __name__ == "__main__":
    main()