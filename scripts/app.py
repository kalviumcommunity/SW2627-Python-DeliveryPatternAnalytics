import os
import pandas as pd
import streamlit as st


DATA_FILE = "output/feature_engineered_dataset.csv"
DAILY_FILE = "output/time_series_daily.csv"
WEEKLY_FILE = "output/time_series_weekly.csv"


st.set_page_config(
    page_title="Delivery Pattern Analytics",
    page_icon="🚚",
    layout="wide"
)


@st.cache_data
def load_data():
    """Load the main feature-engineered dataset."""

    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    if "delivery_date" in df.columns:
        df["delivery_date"] = pd.to_datetime(
            df["delivery_date"],
            errors="coerce"
        )

    return df


@st.cache_data
def load_time_series():
    """Load time-series outputs."""

    daily = pd.read_csv(DAILY_FILE)
    weekly = pd.read_csv(WEEKLY_FILE)

    daily["delivery_date"] = pd.to_datetime(
        daily["delivery_date"],
        errors="coerce"
    )

    weekly["delivery_date"] = pd.to_datetime(
        weekly["delivery_date"],
        errors="coerce"
    )

    return daily, weekly


# --------------------------------------------------
# Load data
# --------------------------------------------------

df = load_data()

daily, weekly = load_time_series()


# --------------------------------------------------
# Sidebar Navigation
# --------------------------------------------------

st.sidebar.title("🚚 Delivery Analytics")

st.sidebar.subheader("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "Trends",
        "Segments",
        "Data Explorer"
    ]
)


# --------------------------------------------------
# Overview
# --------------------------------------------------

if page == "Overview":

    st.title("Delivery Pattern Analytics")

    st.subheader("Business Overview")

    st.write(
        "Overview of delivery performance, customer complaints, "
        "refunds, and SLA performance."
    )

    st.divider()

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Deliveries",
            len(df)
        )

    with col2:
        st.metric(
            "Avg Delivery Time",
            f"{df['delivery_time_min'].mean():.1f} min"
        )

    with col3:
        st.metric(
            "Total Refund",
            f"{df['refund_amount'].sum():.2f}"
        )

    with col4:
        complaint_rate = (
            df["complaint"].eq("Yes").mean() * 100
        )

        st.metric(
            "Complaint Rate",
            f"{complaint_rate:.1f}%"
        )

    st.divider()

    st.header("Delivery Performance")

    performance_counts = (
        df["delivery_performance"]
        .value_counts()
    )

    st.bar_chart(performance_counts)

    with st.expander("View Raw Delivery Data"):
        st.dataframe(
            df,
            use_container_width=True
        )


# --------------------------------------------------
# Trends
# --------------------------------------------------

elif page == "Trends":

    st.title("Trend Analysis")

    st.write(
        "Time-series view of delivery performance and refunds."
    )

    st.divider()

    st.header("Delivery Time Trend")

    st.line_chart(
        daily.set_index("delivery_date")[
            [
                "avg_delivery_time",
                "delivery_time_ma7"
            ]
        ]
    )

    st.divider()

    st.header("Refund Trend")

    st.line_chart(
        daily.set_index("delivery_date")[
            [
                "total_refund",
                "refund_ma7"
            ]
        ]
    )

    with st.expander("View Weekly Metrics"):
        st.dataframe(
            weekly,
            use_container_width=True
        )


# --------------------------------------------------
# Segments
# --------------------------------------------------

elif page == "Segments":

    st.title("Segment Breakdown")

    st.write(
        "Compare delivery performance across different cities "
        "and quality tiers."
    )

    st.divider()

    st.header("Performance by City")

    city_metrics = (
        df.groupby("city")
        .agg(
            deliveries=("delivery_id", "count"),
            avg_delivery_time=("delivery_time_min", "mean"),
            total_refund=("refund_amount", "sum")
        )
        .reset_index()
    )

    st.dataframe(
        city_metrics,
        use_container_width=True
    )

    st.bar_chart(
        city_metrics.set_index("city")[
            "avg_delivery_time"
        ]
    )

    st.divider()

    st.header("Delivery Quality Tiers")

    quality_counts = (
        df["delivery_quality_tier"]
        .value_counts()
    )

    st.bar_chart(quality_counts)


# --------------------------------------------------
# Data Explorer
# --------------------------------------------------

elif page == "Data Explorer":

    st.title("Data Explorer")

    st.write(
        "Explore the processed delivery dataset."
    )

    st.divider()

    st.header("Filters")

    selected_city = st.selectbox(
        "Select City",
        ["All"] + sorted(df["city"].dropna().unique().tolist())
    )

    filtered_df = df.copy()

    if selected_city != "All":
        filtered_df = filtered_df[
            filtered_df["city"] == selected_city
        ]

    st.subheader(
        f"Records: {len(filtered_df)}"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    with st.expander("Dataset Information"):

        st.write(
            f"Rows: {df.shape[0]}"
        )

        st.write(
            f"Columns: {df.shape[1]}"
        )

        st.write(
            "Available columns:"
        )

        st.write(
            df.columns.tolist()
        )

    csv_data = filtered_df.to_csv(index=False)

    st.download_button(
        label="Download Filtered Data",
        data=csv_data,
        file_name="filtered_delivery_data.csv",
        mime="text/csv"
    )