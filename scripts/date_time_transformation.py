from pathlib import Path
from datetime import datetime
import json

import pandas as pd

#PATHS

INPUT_FILE = Path("data/raw/delivery_profiling_dataset.xlsx")
OUTPUT_DATASET = Path("data/processed/delivery_datetime_transformed.csv")
OUTPUT_REPORT = Path("output/date_time_transformation_report.json")


# Date format used by the source Excel dataset
DATE_FORMAT = "%Y-%m-%d"


# LOADING DATASET

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

    print(f"✓ Dataset loaded successfully")
    print(f"  Source: {filepath}")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {len(df.columns)}")

    return df

# BEFORE DTYPES

def capture_dtypes(df):
    """Capture column data types before transformation."""

    return {
        column: str(dtype)
        for column, dtype in df.dtypes.items()
    }


# DATETIME CONVERSION
def convert_delivery_date(df):
    """
    Convert delivery_date from string to datetime.

    Explicit date format is used to avoid relying on
    pandas date inference.
    """

    if "delivery_date" not in df.columns:
        raise KeyError(
            "Required column 'delivery_date' was not found."
        )

    print("\nConverting delivery_date...")

    original_values = df["delivery_date"].copy()

    # Convert using explicit format.
    converted = pd.to_datetime(
        df["delivery_date"],
        format=DATE_FORMAT,
        errors="coerce"
    )

    invalid_mask = (
        converted.isna()
        & original_values.notna()
    )

    invalid_values = (
        original_values[invalid_mask]
        .astype(str)
        .tolist()
    )

    df["delivery_date"] = converted

    print(f"✓ Date conversion completed")
    print(f"  Format used: {DATE_FORMAT}")
    print(f"  Invalid values: {len(invalid_values)}")

    return df, {
        "column": "delivery_date",
        "conversion": "string/date → datetime",
        "format": DATE_FORMAT,
        "invalid_values": invalid_values,
        "invalid_count": len(invalid_values)
    }


# EXTRACTING DATE FEATURES


def extract_date_features(df):
    """Extract useful features from delivery_date."""

    print("\nExtracting date/time features...")

    # Day name
    df["day_of_week"] = (
        df["delivery_date"].dt.day_name()
    )

    # Numeric day of week
    df["dow_numeric"] = (
        df["delivery_date"].dt.dayofweek
    )

    # Hour of day
    df["hour"] = (
        df["delivery_date"].dt.hour
    )

    # ISO week number
    df["week_num"] = (
        df["delivery_date"]
        .dt.isocalendar()
        .week
        .astype("Int64")
    )

    # Month number
    df["month"] = (
        df["delivery_date"].dt.month
    )

    # Quarter
    df["quarter"] = (
        df["delivery_date"].dt.quarter
    )

    print("✓ Extracted:")
    print("  - day_of_week")
    print("  - dow_numeric")
    print("  - hour")
    print("  - week_num")
    print("  - month")
    print("  - quarter")

    return df

# CALCULATE DAYS SINCE DELIVERY


def calculate_days_since_delivery(df):
    """
    Calculate the number of days between the current date
    and each delivery date.
    """

    print("\nCalculating days_since_delivery...")

    today = pd.Timestamp.now().normalize()

    df["days_since_delivery"] = (
        today - df["delivery_date"]
    ).dt.days

    print(f"✓ Reference date: {today.date()}")

    return df



# TIME-SERIES AGGREGATION

def create_weekly_summary(df):
    """
    Demonstrate weekly time-series aggregation using resample().
    """

    print("\nCreating weekly time-series summary...")

    if "delivery_date" not in df.columns:
        raise KeyError(
            "delivery_date is required for resampling."
        )

    # Creating a temporary time-indexed dataframe
    df_ts = df.set_index("delivery_date")

    # Counting deliveries per week
    weekly_summary = (
        df_ts["delivery_id"]
        .resample("W")
        .count()
        .rename("delivery_count")
        .reset_index()
    )

    print("✓ Weekly aggregation completed")

    return weekly_summary

# VALIDATION

def validate_transformation(df):
    """Validate the transformed date column and generated features."""

    print("\nValidating transformation...")

    required_columns = [
        "delivery_date",
        "day_of_week",
        "dow_numeric",
        "hour",
        "week_num",
        "month",
        "quarter",
        "days_since_delivery"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing transformed columns: {missing_columns}"
        )

    # Confirm datetime type
    date_is_datetime = pd.api.types.is_datetime64_any_dtype(
        df["delivery_date"]
    )

    # Counting invalid dates
    invalid_dates = int(
        df["delivery_date"].isna().sum()
    )

    validation = {
        "delivery_date_is_datetime": bool(date_is_datetime),
        "invalid_dates": invalid_dates,
        "required_features_present": len(missing_columns) == 0,
        "status": (
            "PASS"
            if date_is_datetime and not missing_columns
            else "FAIL"
        )
    }

    print(f"  delivery_date datetime: {date_is_datetime}")
    print(f"  Invalid dates: {invalid_dates}")
    print(f"  Required features: {len(missing_columns) == 0}")
    print(f"  Validation: {validation['status']}")

    return validation

# SAVEING TRANSFORMED DATASET

def save_dataset(df, filepath):
    """Save transformed dataset to CSV."""

    filepath.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        filepath,
        index=False
    )

    print(f"\n✓ Transformed dataset saved:")
    print(f"  {filepath}")



# GENERATEING REPORT


def generate_report(
    df,
    before_dtypes,
    conversion_log,
    validation,
    weekly_summary
):
    """Generate JSON audit report."""

    after_dtypes = capture_dtypes(df)

    dtype_changes = {}

    for column in before_dtypes:
        before = before_dtypes[column]
        after = after_dtypes.get(column)

        if before != after:
            dtype_changes[column] = {
                "before": before,
                "after": after
            }

    report = {
        "timestamp": datetime.now().isoformat(),

        "source": str(INPUT_FILE),

        "dataset": {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns)
        },

        "before_dtypes": before_dtypes,

        "after_dtypes": after_dtypes,

        "dtype_changes": dtype_changes,

        "date_features_created": [
            "day_of_week",
            "dow_numeric",
            "hour",
            "week_num",
            "month",
            "quarter",
            "days_since_delivery"
        ],

        "conversion_logs": [
            conversion_log
        ],

        "weekly_summary": weekly_summary.to_dict(
            orient="records"
        ),

        "validation": validation,

        "summary": {
            "features_created": 7,
            "dtype_changes": len(dtype_changes),
            "validation_status": validation["status"]
        }
    }

    return report


# SAVEING REPORT

def save_report(report, filepath):
    """Save transformation report as JSON."""

    filepath.parent.mkdir(
        parents=True,
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

    print(f"✓ Transformation report saved:")
    print(f"  {filepath}")


# ============================================================
# MAIN WORKFLOW
# ============================================================

def main():

    print("=" * 60)
    print("Assignment 2.22")
    print("Date & Time Transformation Pipeline")
    print("=" * 60)

    # Step 1: Load
    df = load_dataset(INPUT_FILE)

    # Step 2: Capture original types
    before_dtypes = capture_dtypes(df)

    print("\nBefore transformation dtypes:")
    for column, dtype in before_dtypes.items():
        print(f"  {column}: {dtype}")

    # Step 3: Convert delivery_date
    df, conversion_log = convert_delivery_date(df)

    # Step 4: Extract date features
    df = extract_date_features(df)

    # Step 5: Calculate elapsed time
    df = calculate_days_since_delivery(df)

    # Step 6: Weekly resampling
    weekly_summary = create_weekly_summary(df)

    # Step 7: Validate
    validation = validate_transformation(df)

    # Step 8: Save transformed data
    save_dataset(
        df,
        OUTPUT_DATASET
    )

    # Step 9: Generate report
    report = generate_report(
        df,
        before_dtypes,
        conversion_log,
        validation,
        weekly_summary
    )

    # Step 10: Save report
    save_report(
        report,
        OUTPUT_REPORT
    )

    # Step 11: Show sample
    print("\nTransformed dataset sample:")
    print(
        df[
            [
                "delivery_date",
                "day_of_week",
                "dow_numeric",
                "hour",
                "week_num",
                "month",
                "quarter",
                "days_since_delivery"
            ]
        ].head()
    )

    print("\n" + "=" * 60)
    print("Date & Time Transformation completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()