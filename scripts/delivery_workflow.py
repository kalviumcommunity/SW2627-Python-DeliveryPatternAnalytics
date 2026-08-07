import pandas as pd
import logging
import os

# ==============================
# Configuration
# ==============================

INPUT_FILE = "data/raw/deliveries.csv"
OUTPUT_FILE = "output/processed_deliveries.csv"
LOG_FILE = "logs/workflow.log"

# Create directories if they don't exist
os.makedirs("output", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# ==============================
# Logging
# ==============================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==============================
# Function 1 : Ingest Data
# ==============================

def ingest_data(filepath):
    """
    Reads delivery data from a CSV file.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        pandas.DataFrame
    """
    try:
        df = pd.read_csv(filepath)
        logging.info(f"Loaded {len(df)} records.")
        return df

    except FileNotFoundError:
        logging.error("Input file not found.")
        raise


# ==============================
# Function 2 : Process Data
# ==============================

def process_data(df):
    """
    Processes delivery data and identifies SLA violations.

    Args:
        df (DataFrame)

    Returns:
        DataFrame
    """

    df = df.drop_duplicates()

    df["SLA_Status"] = df.apply(
        lambda row: "Violated"
        if row["delivery_time"] > row["sla_limit"]
        else "On Time",
        axis=1
    )

    logging.info("Processing completed.")

    return df


# ==============================
# Function 3 : Output Results
# ==============================

def output_results(df, filepath):
    """
    Saves processed delivery data.

    Args:
        df (DataFrame)
        filepath (str)
    """

    df.to_csv(filepath, index=False)

    logging.info("Output file generated.")

    print(f"\nProcessed file saved at:\n{filepath}")


# ==============================
# Main
# ==============================

def main():

    print("Starting Delivery Workflow...\n")

    logging.info("Workflow Started")

    data = ingest_data(INPUT_FILE)

    processed_data = process_data(data)

    output_results(processed_data, OUTPUT_FILE)

    logging.info("Workflow Completed")

    print("\nWorkflow Completed Successfully.")


if __name__ == "__main__":
    main()