import streamlit as st
import pandas as pd


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Delivery Pattern Analytics",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# Session State Initialization
# --------------------------------------------------

if "selected_segment" not in st.session_state:
    st.session_state["selected_segment"] = "All"

if "workflow_step" not in st.session_state:
    st.session_state["workflow_step"] = 1

if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None


# ============================================================
# SIMPLE CLEAN THEME
# ============================================================

st.markdown(
    """
    <style>
        .main {
            background-color: #f7f8fa;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        [data-testid="stMetric"] {
            background-color: white;
            border: 1px solid #e5e7eb;
            padding: 15px;
            border-radius: 10px;
        }

        .stButton > button {
            width: 100%;
            border-radius: 8px;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid #e5e7eb;
        }

        h1, h2, h3 {
            color: #1f2937;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("🚚 Delivery Analytics")
st.sidebar.caption("Delivery Pattern Analytics Platform")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Trends",
        "Segments",
        "Data Explorer",
        "Dataset Upload"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Interactive analytics dashboard")


# ============================================================
# HELPER FUNCTION
# ============================================================

def show_kpis(data):
    """Display basic delivery KPIs."""

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Deliveries",
            f"{len(data):,}"
        )

    with col2:
        avg_time = data["delivery_time_min"].mean()
        st.metric(
            "Avg Delivery Time",
            f"{avg_time:.1f} min"
        )

    with col3:
        refund_total = data["refund_amount"].sum()
        st.metric(
            "Total Refund",
            f"{refund_total:,.0f}"
        )

    with col4:
        if len(data) > 0:
            within_sla = (
                data["delivery_time_min"]
                <= data["sla_limit_min"]
            ).mean() * 100
        else:
            within_sla = 0

        st.metric(
            "Within SLA",
            f"{within_sla:.1f}%"
        )


# ============================================================
# OVERVIEW
# ============================================================

if page == "Overview":

    st.title("Delivery Pattern Analytics")

    st.write(
        "Monitor delivery performance, SLA compliance, "
        "refunds and delivery patterns."
    )

    st.divider()

    try:
        df = pd.read_csv(
            "output/feature_engineered_dataset.csv"
        )

        df["delivery_date"] = pd.to_datetime(
            df["delivery_date"],
            errors="coerce"
        )

        st.header("Business Overview")

        show_kpis(df)

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Delivery Status")

            status_counts = (
                df["delivery_status"]
                .value_counts()
            )

            st.bar_chart(status_counts)

        with col2:

            st.subheader("Deliveries by City")

            city_counts = (
                df["city"]
                .value_counts()
                .head(10)
            )

            st.bar_chart(city_counts)

    except Exception:

        st.info(
            "Upload a dataset from the Dataset Upload section "
            "to view the dashboard."
        )


# ============================================================
# TRENDS
# ============================================================

elif page == "Trends":

    st.title("Trend Analysis")

    st.write(
        "Explore delivery performance over time."
    )

    st.divider()

    try:

        df = pd.read_csv(
            "output/feature_engineered_dataset.csv"
        )

        df["delivery_date"] = pd.to_datetime(
            df["delivery_date"],
            errors="coerce"
        )

        daily = (
            df.dropna(subset=["delivery_date"])
            .groupby("delivery_date")
            .agg(
                deliveries=("delivery_id", "count"),
                avg_delivery_time=(
                    "delivery_time_min",
                    "mean"
                )
            )
        )

        daily["rolling_7_day"] = (
            daily["avg_delivery_time"]
            .rolling(7)
            .mean()
        )

        st.subheader("Daily Deliveries")

        st.line_chart(
            daily["deliveries"]
        )

        st.subheader("Average Delivery Time")

        st.line_chart(
            daily[
                [
                    "avg_delivery_time",
                    "rolling_7_day"
                ]
            ]
        )

    except Exception:

        st.info(
            "No dataset available. Upload a dataset first."
        )


# ============================================================
# SEGMENTS
# ============================================================

elif page == "Segments":

    st.title("Segment Breakdown")

    st.write(
        "Compare delivery performance across cities "
        "and delivery categories."
    )

    st.divider()

    if st.button("Reset Workflow"):

        for key in [
            "selected_segment",
            "workflow_step",
            "analysis_result"
        ]:

            if key in st.session_state:
                del st.session_state[key]

        st.rerun()

    try:

        df = pd.read_csv(
            "output/feature_engineered_dataset.csv"
        )

        st.subheader("City Performance")

        city_metrics = (
            df.groupby("city")
            .agg(
                deliveries=("delivery_id", "count"),
                avg_delivery_time=(
                    "delivery_time_min",
                    "mean"
                ),
                total_refund=(
                    "refund_amount",
                    "sum"
                )
            )
            .sort_values(
                "deliveries",
                ascending=False
            )
        )

        st.dataframe(
            city_metrics,
            use_container_width=True
        )

        st.divider()

        st.subheader("Delivery Performance")

        performance_counts = (
            df["delivery_performance"]
            .value_counts()
        )

        st.bar_chart(
            performance_counts
        )

    except Exception:

           st.header("Step 1: Select Segment")

    # Get segment options from uploaded/processed data if available
    segment_options = ["All", "Enterprise", "Mid-Market", "SMB"]

    current_segment = st.session_state["selected_segment"]

    if current_segment not in segment_options:
        current_segment = "All"

    selected_segment = st.selectbox(
        "Choose a segment",
        segment_options,
        index=segment_options.index(current_segment)
    )

    if st.button("Confirm Segment"):
        st.session_state["selected_segment"] = selected_segment
        st.session_state["workflow_step"] = 2
        st.rerun()


# ============================================================
# DATA EXPLORER
# ============================================================

elif page == "Data Explorer":

    st.title("Data Explorer")

    st.write(
        "Use interactive filters to explore delivery records."
    )

    st.divider()

    try:

        df = pd.read_csv(
            "output/feature_engineered_dataset.csv"
        )

        df["delivery_date"] = pd.to_datetime(
            df["delivery_date"],
            errors="coerce"
        )

        # ----------------------------------------------------
        # SIDEBAR FILTERS
        # ----------------------------------------------------

        st.sidebar.header("🔎 Filters")

        # Date range
        valid_dates = df["delivery_date"].dropna()

        if valid_dates.empty:
            st.warning("No valid delivery dates found.")
            st.stop()

        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()

        date_range = st.sidebar.date_input(
            "Delivery Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        # Make sure date range contains two dates
        if len(date_range) != 2:
            st.warning(
                "Please select both a start date and an end date."
            )
            st.stop()

        # City multiselect
        all_cities = sorted(
            df["city"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_cities = st.sidebar.multiselect(
            "City",
            options=all_cities,
            default=all_cities
        )

        # Delivery time slider
        min_time = int(
            df["delivery_time_min"]
            .min()
        )

        max_time = int(
            df["delivery_time_min"]
            .max()
        )

        delivery_time_range = st.sidebar.slider(
            "Delivery Time (minutes)",
            min_value=min_time,
            max_value=max_time,
            value=(min_time, max_time)
        )

        # Delivery status radio
        statuses = sorted(
            df["delivery_status"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_status = st.sidebar.radio(
            "Delivery Status",
            options=["All"] + statuses
        )

        # Reset
        if st.sidebar.button("↻ Reset Filters"):
            st.rerun()

        # ----------------------------------------------------
        # APPLY FILTERS
        # ----------------------------------------------------

        filtered_df = df[
            (df["delivery_date"].dt.date >= date_range[0])
            &
            (df["delivery_date"].dt.date <= date_range[1])
            &
            (df["city"].isin(selected_cities))
            &
            (
                df["delivery_time_min"]
                >= delivery_time_range[0]
            )
            &
            (
                df["delivery_time_min"]
                <= delivery_time_range[1]
            )
        ]

        if selected_status != "All":

            filtered_df = filtered_df[
                filtered_df["delivery_status"]
                == selected_status
            ]

        # ----------------------------------------------------
        # EMPTY RESULT
        # ----------------------------------------------------

        if filtered_df.empty:

            st.warning(
                "No deliveries match the selected filters. "
                "Try broadening your filters."
            )

            st.stop()

        # ----------------------------------------------------
        # FILTERED KPIs
        # ----------------------------------------------------

        st.header("Filtered Results")

        show_kpis(filtered_df)

        st.divider()

        # ----------------------------------------------------
        # FILTERED DATA
        # ----------------------------------------------------

        st.subheader("Delivery Records")

        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=450
        )

        # ----------------------------------------------------
        # QUICK ANALYSIS
        # ----------------------------------------------------

        st.divider()

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Delivery Performance")

            performance = (
                filtered_df[
                    "delivery_performance"
                ]
                .value_counts()
            )

            st.bar_chart(performance)

        with col2:

            st.subheader("Deliveries by City")

            cities = (
                filtered_df["city"]
                .value_counts()
                .head(10)
            )

            st.bar_chart(cities)

    except FileNotFoundError:

        st.warning(
            "Feature-engineered dataset was not found. "
            "Please upload or generate the dataset first."
        )

    except Exception as e:

        st.error(
            f"Unable to load the dataset: {str(e)}"
        )


# ============================================================
# DATASET UPLOAD
# ============================================================

elif page == "Dataset Upload":

    st.title("Dataset Upload")

    st.write(
        "Upload a CSV or JSON dataset to preview and analyse it."
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload your dataset",
        type=["csv", "json"]
    )

    if uploaded_file is None:

        st.info(
            "Upload a CSV or JSON file to begin."
        )

    else:

        try:

            # ------------------------------------------------
            # LOAD FILE
            # ------------------------------------------------

            if uploaded_file.name.lower().endswith(".csv"):

                df = pd.read_csv(
                    uploaded_file
                )

            elif uploaded_file.name.lower().endswith(".json"):

                df = pd.read_json(
                    uploaded_file
                )

            else:

                st.error(
                    "Unsupported file type. "
                    "Please upload CSV or JSON."
                )

                st.stop()

            # ------------------------------------------------
            # EMPTY FILE CHECK
            # ------------------------------------------------

            if len(df) == 0:

                st.warning(
                    "The uploaded file is empty. "
                    "Please check your data."
                )

                st.stop()

            st.success(
                f"File loaded successfully: "
                f"{uploaded_file.name}"
            )

            # ------------------------------------------------
            # DATASET SUMMARY
            # ------------------------------------------------

            st.header("Dataset Summary")

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Rows",
                    f"{len(df):,}"
                )

            with col2:

                st.metric(
                    "Columns",
                    str(len(df.columns))
                )

            with col3:

                total_nulls = (
                    df.isnull()
                    .sum()
                    .sum()
                )

                total_cells = (
                    df.shape[0]
                    *
                    df.shape[1]
                )

                null_percentage = (
                    total_nulls
                    /
                    total_cells
                    *
                    100
                    if total_cells > 0
                    else 0
                )

                st.metric(
                    "Null %",
                    f"{null_percentage:.1f}%"
                )

            st.divider()

            # ------------------------------------------------
            # PREVIEW
            # ------------------------------------------------

            st.subheader("First 10 Rows")

            st.dataframe(
                df.head(10),
                use_container_width=True
            )

            st.divider()

            # ------------------------------------------------
            # COLUMN SUMMARY
            # ------------------------------------------------

            st.subheader("Column Summary")

            summary = pd.DataFrame(
                {
                    "Column": df.columns,
                    "Type": (
                        df.dtypes
                        .astype(str)
                        .values
                    ),
                    "Non-Null": (
                        df.notnull()
                        .sum()
                        .values
                    ),
                    "Null Count": (
                        df.isnull()
                        .sum()
                        .values
                    ),
                    "Null %": (
                        (
                            df.isnull().sum()
                            /
                            len(df)
                            *
                            100
                        )
                        .round(1)
                        .values
                    )
                }
            )

            st.dataframe(
                summary,
                use_container_width=True
            )

            st.divider()

            # ------------------------------------------------
            # STATISTICS
            # ------------------------------------------------

            st.subheader(
                "Descriptive Statistics"
            )

            st.dataframe(
                df.describe(
                    include="all"
                ).transpose(),
                use_container_width=True
            )

            # ------------------------------------------------
            # UPLOAD-SPECIFIC FILTERS
            # ------------------------------------------------

            st.divider()

            st.header("Explore Uploaded Dataset")

            # Only create filters when relevant columns exist
            if "city" in df.columns:

                selected_upload_cities = st.multiselect(
                    "Filter by City",
                    sorted(
                        df["city"]
                        .dropna()
                        .unique()
                        .tolist()
                    )
                )

                if selected_upload_cities:

                    filtered_upload = df[
                        df["city"].isin(
                            selected_upload_cities
                        )
                    ]

                    st.dataframe(
                        filtered_upload,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "Select a city to filter the uploaded data."
                    )

        except Exception:

            st.error(
                "Could not read this file. "
                "Please check that the file format is valid."
            )

            st.stop()