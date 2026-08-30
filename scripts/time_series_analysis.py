import os
import pandas as pd
import matplotlib.pyplot as plt


INPUT_FILE = "output/feature_engineered_dataset.csv"
DAILY_OUTPUT = "output/time_series_daily.csv"
WEEKLY_OUTPUT = "output/time_series_weekly.csv"
SUMMARY_OUTPUT = "output/time_series_summary.csv"


def load_data():
    """Load and prepare delivery data for time-series analysis."""

    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    if df.empty:
        raise ValueError("Input dataset is empty.")

    if "delivery_date" not in df.columns:
        raise ValueError("delivery_date column is missing.")

    df["delivery_date"] = pd.to_datetime(
        df["delivery_date"],
        errors="coerce"
    )

    invalid_dates = df["delivery_date"].isna().sum()

    if invalid_dates > 0:
        print(f"Warning: {invalid_dates} invalid delivery dates found.")
        df = df.dropna(subset=["delivery_date"])

    df = df.sort_values("delivery_date")

    return df


def create_daily_metrics(df):
    """Create daily time-series metrics."""

    daily = (
        df.set_index("delivery_date")
        .resample("D")
        .agg(
            delivery_count=("delivery_id", "count"),
            avg_delivery_time=("delivery_time_min", "mean"),
            avg_sla_ratio=("delivery_time_sla_ratio", "mean"),
            total_refund=("refund_amount", "sum")
        )
        .reset_index()
    )

    # Rolling averages
    daily["delivery_time_ma7"] = (
        daily["avg_delivery_time"]
        .rolling(window=7, min_periods=1)
        .mean()
    )

    daily["refund_ma7"] = (
        daily["total_refund"]
        .rolling(window=7, min_periods=1)
        .mean()
    )

    # Cumulative metrics
    daily["cumulative_deliveries"] = (
        daily["delivery_count"].cumsum()
    )

    daily["cumulative_refund"] = (
        daily["total_refund"].cumsum()
    )

    return daily


def create_weekly_metrics(df):
    """Create weekly aggregated metrics."""

    weekly = (
        df.set_index("delivery_date")
        .resample("W")
        .agg(
            delivery_count=("delivery_id", "count"),
            avg_delivery_time=("delivery_time_min", "mean"),
            avg_sla_ratio=("delivery_time_sla_ratio", "mean"),
            total_refund=("refund_amount", "sum")
        )
    )

    # Week-over-week percentage changes
    weekly["delivery_count_wow_pct"] = (
        weekly["delivery_count"]
        .pct_change()
        .mul(100)
    )

    weekly["refund_wow_pct"] = (
        weekly["total_refund"]
        .pct_change()
        .mul(100)
    )

    weekly["delivery_time_wow_pct"] = (
        weekly["avg_delivery_time"]
        .pct_change()
        .mul(100)
    )

    return weekly.reset_index()


def determine_trend(weekly):
    """Determine overall delivery-time trend."""

    if len(weekly) < 2:
        return "Insufficient data"

    first_value = weekly["avg_delivery_time"].iloc[0]
    last_value = weekly["avg_delivery_time"].iloc[-1]

    if pd.isna(first_value) or pd.isna(last_value):
        return "Insufficient data"

    if last_value > first_value:
        return "Uptrend - Average delivery time is increasing"
    elif last_value < first_value:
        return "Downtrend - Average delivery time is decreasing"
    else:
        return "Stable - Average delivery time is unchanged"


def create_summary(df, daily, weekly):
    """Create a summary of the time-series analysis."""

    summary = pd.DataFrame({
        "metric": [
            "total_deliveries",
            "total_refund",
            "overall_avg_delivery_time",
            "overall_avg_sla_ratio",
            "maximum_daily_refund",
            "maximum_daily_delivery_count",
            "delivery_time_trend"
        ],
        "value": [
            len(df),
            df["refund_amount"].sum(),
            df["delivery_time_min"].mean(),
            df["delivery_time_sla_ratio"].mean(),
            daily["total_refund"].max(),
            daily["delivery_count"].max(),
            determine_trend(weekly)
        ]
    })

    return summary


def create_charts(daily):
    """Create time-series visualizations."""

    plt.figure(figsize=(10, 5))

    plt.plot(
        daily["delivery_date"],
        daily["avg_delivery_time"],
        label="Daily Average"
    )

    plt.plot(
        daily["delivery_date"],
        daily["delivery_time_ma7"],
        label="7-Day Rolling Average"
    )

    plt.xlabel("Date")
    plt.ylabel("Average Delivery Time (minutes)")
    plt.title("Delivery Time Trend")
    plt.legend()
    plt.tight_layout()

    plt.savefig("output/delivery_time_trend.png")
    plt.close()

    plt.figure(figsize=(10, 5))

    plt.plot(
        daily["delivery_date"],
        daily["total_refund"],
        label="Daily Refund"
    )

    plt.plot(
        daily["delivery_date"],
        daily["refund_ma7"],
        label="7-Day Rolling Refund Average"
    )

    plt.xlabel("Date")
    plt.ylabel("Refund Amount")
    plt.title("Refund Trend Over Time")
    plt.legend()
    plt.tight_layout()

    plt.savefig("output/refund_trend.png")
    plt.close()


def main():
    print("Starting time-series analysis...")

    df = load_data()

    print(f"Input rows: {len(df)}")
    print(
        f"Date range: "
        f"{df['delivery_date'].min()} "
        f"to "
        f"{df['delivery_date'].max()}"
    )

    daily = create_daily_metrics(df)
    weekly = create_weekly_metrics(df)

    summary = create_summary(
        df,
        daily,
        weekly
    )

    daily.to_csv(
        DAILY_OUTPUT,
        index=False
    )

    weekly.to_csv(
        WEEKLY_OUTPUT,
        index=False
    )

    summary.to_csv(
        SUMMARY_OUTPUT,
        index=False
    )

    create_charts(daily)

    print("\nTime-Series Summary")
    print(summary.to_string(index=False))

    print("\nOutput files created:")
    print(DAILY_OUTPUT)
    print(WEEKLY_OUTPUT)
    print(SUMMARY_OUTPUT)
    print("output/delivery_time_trend.png")
    print("output/refund_trend.png")

    print("\nTime-series analysis completed successfully.")


if __name__ == "__main__":
    main()