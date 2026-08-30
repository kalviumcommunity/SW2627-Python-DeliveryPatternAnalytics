import streamlit as st
import pandas as pd


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Delivery Pattern Analytics",
    page_icon="🚚",
    layout="wide"
)


# --------------------------------------------------
# Sidebar Navigation
# --------------------------------------------------

st.sidebar.title("🚚 Delivery Analytics")

page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "Trends",
        "Segments",
        "Data Explorer",
        "Dataset Upload"
    ]
)


# --------------------------------------------------
# Overview
# --------------------------------------------------

if page == "Overview":

    st.title("Delivery Pattern Analytics")

    st.header("Business Overview")

    st.write(
        "Overview of delivery performance and business metrics."
    )

    st.divider()

    st.info(
        "Use the Dataset Upload section to upload your own CSV or JSON file."
    )


# --------------------------------------------------
# Trends
# --------------------------------------------------

elif page == "Trends":

    st.title("Trend Analysis")

    st.write(
        "This section is used for time-series analysis."
    )

    st.info(
        "Existing time-series analysis can be displayed here."
    )


# --------------------------------------------------
# Segments
# --------------------------------------------------

elif page == "Segments":

    st.title("Segment Breakdown")

    st.write(
        "This section is used for segment-level analysis."
    )

    st.info(
        "Existing segment analysis can be displayed here."
    )


# --------------------------------------------------
# Data Explorer
# --------------------------------------------------

elif page == "Data Explorer":

    st.title("Data Explorer")

    st.write(
        "Explore the processed delivery dataset."
    )

    st.info(
        "Use Dataset Upload to bring a new dataset into the application."
    )


# --------------------------------------------------
# Dataset Upload
# --------------------------------------------------

elif page == "Dataset Upload":

    st.title("Dataset Upload")

    st.write(
        "Upload a CSV or JSON dataset to preview and analyse it."
    )

    st.divider()

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload your dataset",
        type=["csv", "json"]
    )

    # --------------------------------------------------
    # No file uploaded
    # --------------------------------------------------

    if uploaded_file is None:

        st.info(
            "Upload a CSV or JSON file to begin."
        )

    # --------------------------------------------------
    # File uploaded
    # --------------------------------------------------

    else:

        try:

            # Load CSV
            if uploaded_file.name.lower().endswith(".csv"):

                df = pd.read_csv(uploaded_file)

            # Load JSON
            elif uploaded_file.name.lower().endswith(".json"):

                df = pd.read_json(uploaded_file)

            # Unsupported format
            else:

                st.error(
                    "Unsupported file type. Please upload CSV or JSON."
                )

                st.stop()


            # --------------------------------------------------
            # Empty Dataset Check
            # --------------------------------------------------

            if len(df) == 0:

                st.warning(
                    "The uploaded file is empty. Please check your data."
                )

                st.stop()


            # --------------------------------------------------
            # Successful Upload
            # --------------------------------------------------

            st.success(
                f"File loaded successfully: {uploaded_file.name}"
            )


            # --------------------------------------------------
            # Dataset Summary
            # --------------------------------------------------

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

                total_nulls = df.isnull().sum().sum()

                total_cells = df.shape[0] * df.shape[1]

                if total_cells > 0:

                    null_percentage = (
                        total_nulls / total_cells
                    ) * 100

                else:

                    null_percentage = 0

                st.metric(
                    "Null %",
                    f"{null_percentage:.1f}%"
                )


            st.divider()


            # --------------------------------------------------
            # First 10 Rows
            # --------------------------------------------------

            st.subheader("First 10 Rows")

            st.dataframe(
                df.head(10),
                use_container_width=True
            )


            st.divider()


            # --------------------------------------------------
            # Column Summary
            # --------------------------------------------------

            st.subheader("Column Summary")

            summary = pd.DataFrame({

                "Column": df.columns,

                "Type": df.dtypes.astype(str).values,

                "Non-Null": df.notnull().sum().values,

                "Null Count": df.isnull().sum().values,

                "Null %": (
                    df.isnull().sum()
                    / len(df)
                    * 100
                ).round(1).values

            })

            st.dataframe(
                summary,
                use_container_width=True
            )


            st.divider()


            # --------------------------------------------------
            # Descriptive Statistics
            # --------------------------------------------------

            st.subheader("Descriptive Statistics")

            st.dataframe(
                df.describe(),
                use_container_width=True
            )


        # --------------------------------------------------
        # Error Handling
        # --------------------------------------------------

        except Exception:

            st.error(
                "Could not read this file. "
                "Please check that the file format is valid."
            )

            st.stop()