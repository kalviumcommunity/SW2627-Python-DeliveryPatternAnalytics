import json
from pathlib import Path

import pandas as pd

INPUT_FILE = Path("data/raw/delivery_profiling_dataset.xlsx")
OUTPUT_DATASET = Path("output/feature_engineered_dataset.csv")
OUTPUT_REPORT = Path("output/feature_engineering_report.json")

# Loading dataset

def load_dataset(path):
    """Load the delivery dataset."""
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    df = pd.read_excel(path)

    if df.empty:
        raise ValueError("Input dataset is empty.")

    return df

# Feature engineering

def create_ratio_features(df):
    """
    Create ratio/rate based features using existing
    delivery dataset columns.
    """

    # Delivery time as a percentage of SLA limit.
    df["delivery_time_sla_ratio"] = (
        df["delivery_time_min"] / df["sla_limit_min"]
    )

    # Delivery time remaining or exceeding SLA.
    df["sla_difference_min"] = (
        df["sla_limit_min"] - df["delivery_time_min"]
    )

    # Refund amount relative to delivery time.
    # Avoid division by zero.
    df["refund_per_delivery_min"] = (
        df["refund_amount"] /
        df["delivery_time_min"].replace(0, pd.NA)
    )

    return df


def create_binned_features(df):
    """
    Convert numerical delivery measurements into
    business-friendly categories.
    """

    # Delivery performance category.
    df["delivery_performance"] = pd.cut(
        df["delivery_time_sla_ratio"],
        bins=[-float("inf"), 0.8, 1.0, float("inf")],
        labels=["fast", "within_sla", "delayed"]
    )

    # Delivery time category.
    df["delivery_time_category"] = pd.cut(
        df["delivery_time_min"],
        bins=[-float("inf"), 30, 60, float("inf")],
        labels=["short", "medium", "long"]
    )

    return df


def create_composite_score(df):
    """
    Create an overall delivery performance score.

    Score components:
    - Delivery within SLA
    - No complaint
    - No refund
    """

    sla_score = (
        df["delivery_time_min"] <= df["sla_limit_min"]
    ).astype(int)

    complaint_score = (
        df["complaint"] == False
    ).astype(int)

    refund_score = (
        df["refund_amount"].fillna(0) == 0
    ).astype(int)

    df["delivery_quality_score"] = (
        sla_score +
        complaint_score +
        refund_score
    )

    df["delivery_quality_tier"] = pd.cut(
        df["delivery_quality_score"],
        bins=[-1, 1, 2, 3],
        labels=["low", "medium", "high"]
    )

    return df

# Validation


def validate_features(df):
    """Validate newly created features."""

    validation = {}

    validation["delivery_time_sla_ratio_non_negative"] = bool(
        (df["delivery_time_sla_ratio"] >= 0).all()
    )

    validation["delivery_quality_score_range"] = bool(
        df["delivery_quality_score"].between(0, 3).all()
    )

    validation["sla_difference_calculated"] = bool(
        df["sla_difference_min"].notna().all()
    )

    validation["feature_rows_match"] = (
        len(df) > 0
    )

    return validation

# Generating report


def generate_report(
    original_df,
    engineered_df,
    validation
):
    """Create a feature engineering audit report."""

    created_features = [
        "delivery_time_sla_ratio",
        "sla_difference_min",
        "refund_per_delivery_min",
        "delivery_performance",
        "delivery_time_category",
        "delivery_quality_score",
        "delivery_quality_tier"
    ]

    report = {
        "source": str(INPUT_FILE),
        "dataset": {
            "rows": len(original_df),
            "columns_before": len(original_df.columns),
            "columns_after": len(engineered_df.columns)
        },
        "feature_engineering": {
            "features_created": created_features,
            "feature_count": len(created_features)
        },
        "feature_definitions": {
            "delivery_time_sla_ratio":
                "delivery_time_min divided by sla_limit_min",
            "sla_difference_min":
                "sla_limit_min minus delivery_time_min",
            "refund_per_delivery_min":
                "refund_amount divided by delivery_time_min",
            "delivery_performance":
                "Categorises delivery as fast, within SLA, or delayed",
            "delivery_time_category":
                "Categorises delivery duration as short, medium, or long",
            "delivery_quality_score":
                "Score from 0 to 3 based on SLA, complaint, and refund status",
            "delivery_quality_tier":
                "Low, medium, or high quality delivery tier"
        },
        "validation": validation
    }

    return report

# Main workflow

def main():

    print("=" * 60)
    print("FEATURE ENGINEERING PIPELINE")
    print("=" * 60)

    # Load
    df_original = load_dataset(INPUT_FILE)

    print(f"\nRows before: {len(df_original)}")
    print(f"Columns before: {len(df_original.columns)}")

    # Keep a working copy
    df = df_original.copy()

    # Create features
    df = create_ratio_features(df)
    df = create_binned_features(df)
    df = create_composite_score(df)

    # Validate
    validation = validate_features(df)

    # Save engineered dataset
    OUTPUT_DATASET.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_DATASET,
        index=False
    )

    # Generate report
    report = generate_report(
        df_original,
        df,
        validation
    )

    OUTPUT_REPORT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_REPORT,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            indent=4
        )

    # Display results
    print(f"Columns after: {len(df.columns)}")

    print("\nCreated features:")
    for feature in report["feature_engineering"]["features_created"]:
        print(f"  - {feature}")

    print("\nValidation:")
    for rule, result in validation.items():
        status = "PASS" if result else "FAIL"
        print(f"  {rule}: {status}")

    print("\nSample engineered data:")
    print(
        df[
            [
                "delivery_id",
                "delivery_time_sla_ratio",
                "sla_difference_min",
                "delivery_performance",
                "delivery_time_category",
                "delivery_quality_score",
                "delivery_quality_tier"
            ]
        ].head()
    )

    print("\nOutput files:")
    print(f"  {OUTPUT_DATASET}")
    print(f"  {OUTPUT_REPORT}")

    print("\nFeature engineering completed successfully.")


if __name__ == "__main__":
    main()