import pandas as pd
from pathlib import Path


#Congiguration

INPUT_FILE = Path("output/feature_engineered_dataset.csv")
OUTPUT_DIR = Path("output")


#loading data

def load_data(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError("Input dataset is empty.")

    return df

# Segment Metrics

def create_segment_metrics(df):
    segment_metrics = df.groupby("city").agg(
        total_records=("city", "count"),
        average_delivery_time=("delivery_time_min", "mean"),
        average_refund=("refund_amount", "mean"),
        complaint_rate=("complaint", lambda x: (x == "Yes").mean()),
        delayed_rate=("delivery_status", lambda x: (x == "Delayed").mean())
    ).reset_index()

    segment_metrics["complaint_rate"] = (
        segment_metrics["complaint_rate"] * 100
    ).round(2)

    segment_metrics["delayed_rate"] = (
        segment_metrics["delayed_rate"] * 100
    ).round(2)

    segment_metrics["average_delivery_time"] = (
        segment_metrics["average_delivery_time"].round(2)
    )

    segment_metrics["average_refund"] = (
        segment_metrics["average_refund"].round(2)
    )

    return segment_metrics

# Multi-Level Aggregation


def create_segment_payment_summary(df):
    summary = (
        df.groupby(["city", "payment_method"])
        .agg(
            delivery_count=("city", "count"),
            average_delivery_time=("delivery_time_min", "mean"),
            total_refund=("refund_amount", "sum")
        )
        .reset_index()
    )

    summary["average_delivery_time"] = (
        summary["average_delivery_time"].round(2)
    )

    summary["total_refund"] = (
        summary["total_refund"].round(2)
    )

    return summary



# Pivot Table

def create_pivot_table(df):
    pivot = pd.pivot_table(
        df,
        values="delivery_time_min",
        index="city",
        columns="payment_method",
        aggfunc="mean"
    )

    return pivot.round(2)



# Rank Segments


def rank_segments(segment_metrics):
    ranked = segment_metrics.copy()

    ranked["delay_rank"] = (
        ranked["delayed_rate"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    ranked = ranked.sort_values(
        "delayed_rate",
        ascending=False
    )

    return ranked


# Generating Insights


def generate_insights(ranked_segments):

    highest_delay = ranked_segments.iloc[0]

    lowest_delay = ranked_segments.iloc[-1]

    print("\n--- Segment Insights ---")

    print(
        f"Highest delayed rate: {highest_delay['city']} "
        f"({highest_delay['delayed_rate']:.2f}%)"
    )

    print(
        f"Lowest delayed rate: {lowest_delay['city']} "
        f"({lowest_delay['delayed_rate']:.2f}%)"
    )

    print("\nSegment performance:")

    for _, row in ranked_segments.iterrows():
        print(
            f"- {row['city']}: "
            f"{row['delayed_rate']:.2f}% delayed, "
            f"{row['complaint_rate']:.2f}% complaints, "
            f"average delivery time "
            f"{row['average_delivery_time']:.2f} minutes"
        )



def main():

    print("Loading delivery dataset...")

    df = load_data(INPUT_FILE)

    print(f"Dataset loaded successfully: {df.shape}")

    # Create segment metrics
    segment_metrics = create_segment_metrics(df)

    # Create multi-dimensional summary
    segment_payment_summary = create_segment_payment_summary(df)

    # Create pivot table
    pivot_table = create_pivot_table(df)

    # Rank segments
    ranked_segments = rank_segments(segment_metrics)

    # Save outputs
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    segment_metrics.to_csv(
        OUTPUT_DIR / "segment_metrics.csv",
        index=False
    )

    segment_payment_summary.to_csv(
        OUTPUT_DIR / "segment_payment_summary.csv",
        index=False
    )

    pivot_table.to_csv(
        OUTPUT_DIR / "segment_payment_pivot.csv"
    )

    # Display results
    print("\n--- Segment Metrics ---")
    print(ranked_segments.to_string(index=False))

    print("\n--- Segment x Payment Method ---")
    print(segment_payment_summary.to_string(index=False))

    print("\n--- Pivot Table ---")
    print(pivot_table)

    # Generate business insights
    generate_insights(ranked_segments)

    print("\nAnalysis completed successfully.")

    print("\nGenerated files:")
    print("output/segment_metrics.csv")
    print("output/segment_payment_summary.csv")
    print("output/segment_payment_pivot.csv")


if __name__ == "__main__":
    main()