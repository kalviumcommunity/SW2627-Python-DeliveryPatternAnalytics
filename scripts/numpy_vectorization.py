from pathlib import Path
import json
import time

import numpy as np
import pandas as pd

# Configuration

SOURCE_FILE = Path("data/raw/delivery_profiling_dataset.xlsx")
PROCESSED_FILE = Path("data/processed/delivery_vectorized.csv")
REPORT_FILE = Path("output/numpy_vectorization_report.json")

TARGET_COLUMN = "delivery_time_min"

# Load Dataset

def load_dataset(file_path):
    """Load the delivery dataset from Excel."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    df = pd.read_excel(file_path)

    if df.empty:
        raise ValueError("The dataset is empty.")

    return df

# Loop-Based Min-Max Normalization

def normalize_with_loop(values):
    """
    Normalize values using a traditional Python loop.
    This represents the slower implementation.
    """

    minimum = min(values)
    maximum = max(values)

    if maximum == minimum:
        return [0.0 for _ in values]

    normalized = []

    for value in values:
        result = (value - minimum) / (maximum - minimum)
        normalized.append(result)

    return normalized

# NumPy Vectorized Min-Max Normalization

def normalize_with_numpy(values):
    """
    Normalize values using NumPy vectorized operations.
    """

    arr = np.asarray(values, dtype=float)

    minimum = arr.min()
    maximum = arr.max()

    if maximum == minimum:
        return np.zeros_like(arr)

    return (arr - minimum) / (maximum - minimum)

# NumPy Z-Score

def calculate_zscore(values):
    """
    Calculate Z-score using NumPy vectorization.
    """

    arr = np.asarray(values, dtype=float)

    mean = arr.mean()
    std = arr.std()

    if std == 0:
        return np.zeros_like(arr)

    return (arr - mean) / std

# Performance Measurement

def measure_performance(values):
    """Compare loop and NumPy execution times."""

    # Loop calculation
    start = time.perf_counter()

    loop_result = normalize_with_loop(values)

    loop_time = time.perf_counter() - start

    # NumPy calculation
    start = time.perf_counter()

    numpy_result = normalize_with_numpy(values)

    numpy_time = time.perf_counter() - start

    # Calculate speedup
    if numpy_time > 0:
        speedup = loop_time / numpy_time
    else:
        speedup = 0

    return (
        loop_result,
        numpy_result,
        loop_time,
        numpy_time,
        speedup
    )


def main():

    print("=" * 60)
    print("LU 2.24 - NumPy Vectorised Computation Workflow")
    print("=" * 60)

    # Load dataset
    df = load_dataset(SOURCE_FILE)

    print(f"\nDataset loaded successfully.")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    # Validate target column
    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Required column '{TARGET_COLUMN}' "
            "was not found in the dataset."
        )

    # Remove missing values only for numerical benchmark
    values = pd.to_numeric(
        df[TARGET_COLUMN],
        errors="coerce"
    )

    if values.isna().any():
        print(
            f"\nWarning: {values.isna().sum()} "
            "missing values found."
        )

    valid_values = values.dropna().to_numpy()

    if len(valid_values) == 0:
        raise ValueError(
            "No valid numerical values available."
        )

    # Performance comparison

    (
        loop_result,
        numpy_result,
        loop_time,
        numpy_time,
        speedup
    ) = measure_performance(valid_values)

    # Validate results

    results_match = np.allclose(
        np.array(loop_result),
        numpy_result
    )

    # Add vectorized features to dataframe

    minimum = values.min()
    maximum = values.max()

    if maximum == minimum:
        df["delivery_time_normalized"] = 0.0
    else:
        df["delivery_time_normalized"] = (
            (values - minimum)
            / (maximum - minimum)
        )

    df["delivery_time_zscore"] = calculate_zscore(
        values.fillna(values.mean()).to_numpy()
    )


    PROCESSED_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        PROCESSED_FILE,
        index=False
    )

    # Createing performance report


    report = {
        "assignment": "LU 2.24 - NumPy Vectorised Computation Workflow",
        "source": str(SOURCE_FILE),
        "target_column": TARGET_COLUMN,
        "dataset": {
            "rows": len(df),
            "columns": len(df.columns)
        },
        "operations": {
            "min_max_normalization": True,
            "z_score_normalization": True
        },
        "performance": {
            "loop_time_seconds": round(loop_time, 8),
            "numpy_time_seconds": round(numpy_time, 8),
            "speedup": round(speedup, 2)
        },
        "validation": {
            "loop_and_numpy_results_match": bool(results_match)
        },
        "output": str(PROCESSED_FILE)
    }

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            indent=4
        )

    # Terminal Report

    print("\nPerformance Comparison")
    print("-" * 40)

    print(
        f"Python Loop:     "
        f"{loop_time:.8f} seconds"
    )

    print(
        f"NumPy Vectorized:"
        f" {numpy_time:.8f} seconds"
    )

    print(
        f"Speedup:         "
        f"{speedup:.2f}x"
    )

    print(
        f"\nResults match:   "
        f"{results_match}"
    )

    print(
        f"\nProcessed dataset saved to:"
        f"\n{PROCESSED_FILE}"
    )

    print(
        f"\nPerformance report saved to:"
        f"\n{REPORT_FILE}"
    )

    print("\nWorkflow completed successfully.")


if __name__ == "__main__":
    main()