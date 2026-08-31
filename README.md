# Delivery Pattern Analytics Platform

## Project Overview

The **Delivery Pattern Analytics Platform** is a Python-based data analytics project built to process, clean, validate, analyse, and visualise delivery data.

The project takes raw delivery records and converts them into reliable, analysis-ready data while identifying data-quality issues and generating useful business insights around delivery performance, SLA compliance, complaints, refunds, customers, cities, and trends.

## What We Used

- **Python** for the overall data-processing workflow
- **Pandas** for data loading, cleaning, transformation, aggregation, and analysis
- **NumPy** for efficient vectorised numerical computations
- **Matplotlib** for statistical visualisations
- **OpenPyXL** for Excel dataset processing
- **Streamlit** for building the interactive frontend/dashboard
- **CSV, JSON, and Excel** for data handling
- **Git & GitHub** for version control and project collaboration

## What We Built

We built a complete data analytics pipeline that includes:

- Dataset validation and source checking
- CSV/JSON data ingestion
- Dataset profiling and quality assessment
- Missing-value handling and imputation
- Data type enforcement and standardisation
- Duplicate detection and deduplication
- String cleaning and text normalisation
- Date and time transformation
- Outlier detection
- Data validation and quality-control rules
- Feature engineering
- NumPy-based performance optimisation
- Distribution and correlation analysis
- GroupBy and segment-level analysis
- Time-series analysis
- Interactive Streamlit dashboard
- Dynamic dataset upload and preview
- Session-state based workflow persistence

## Final Application

The processed data and analytical features are brought together in an interactive **Streamlit dashboard**.

The dashboard provides a simple interface for exploring delivery data, viewing metrics, analysing trends and segments, and interacting with uploaded datasets.

The project therefore covers the complete journey from **raw data → data quality → processing → analysis → interactive visualisation**.

## Project Structure

```text
SW2627-Python-DeliveryPatternAnalytics/
│
├── data/
│   └── raw/
│
├── scripts/
│   ├── app.py
│   ├── data_ingestion.py
│   ├── data_profiling.py
│   ├── missing_value_handling.py
│   ├── type_enforcement.py
│   ├── duplicate_detection.py
│   ├── string_cleaning.py
│   ├── datetime_transformation.py
│   ├── outlier_detection.py
│   ├── data_validation.py
│   ├── feature_engineering.py
│   ├── numpy_vectorization.py
│   ├── distribution_analysis.py
│   ├── correlation_analysis.py
│   └── time_series_analysis.py
│
├── output/
│
└── README.md

Running the Application

Activate the virtual environment:

venv\Scripts\activate

Install dependencies:

python -m pip install pandas numpy matplotlib openpyxl streamlit

Run the dashboard:

python -m streamlit run scripts/app.py
Conclusion

The completed project combines data engineering, data cleaning, statistical analysis, feature engineering, performance optimisation, and frontend development into one end-to-end analytics platform.

It provides a strong foundation for understanding delivery patterns and generating reliable business insights from delivery data.
