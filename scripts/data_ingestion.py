import os
import pandas as pd


def ingest_csv(filepath, delimiter=",", encoding="utf-8"):
    """
    Load a CSV file using explicit delimiter and encoding parameters.

    Args:
        filepath (str): Path to the CSV file.
        delimiter (str): CSV delimiter.
        encoding (str): File encoding.

    Returns:
        pandas.DataFrame: Loaded CSV data.
    """

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    if os.path.getsize(filepath) == 0:
        raise ValueError(f"File is empty: {filepath}")

    try:
        df = pd.read_csv(
            filepath,
            delimiter=delimiter,
            encoding=encoding
        )

        return df

    except UnicodeDecodeError:
        print(
            f"Cannot decode {filepath} using {encoding}. "
            "Try latin-1, iso-8859-1, or cp1252."
        )
        raise


def ingest_csv_with_fallback(filepath, delimiter=","):
    """
    Load a CSV file using multiple encoding options.

    Args:
        filepath (str): Path to the CSV file.
        delimiter (str): CSV delimiter.

    Returns:
        pandas.DataFrame: Loaded CSV data.
    """

    encodings = [
        "utf-8",
        "latin-1",
        "iso-8859-1",
        "cp1252"
    ]

    for encoding in encodings:
        try:
            df = pd.read_csv(
                filepath,
                delimiter=delimiter,
                encoding=encoding
            )

            print(f"CSV loaded successfully using encoding: {encoding}")

            return df

        except UnicodeDecodeError:
            continue

    raise ValueError(
        f"Could not load {filepath} using supported encodings."
    )


def ingest_json(filepath, is_nested=False):
    """
    Load a JSON file into a Pandas DataFrame.

    Args:
        filepath (str): Path to JSON file.
        is_nested (bool): Whether the JSON contains nested objects.

    Returns:
        pandas.DataFrame: Loaded JSON data.
    """

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    if os.path.getsize(filepath) == 0:
        raise ValueError(f"File is empty: {filepath}")

    if is_nested:
        df = pd.read_json(filepath)

        df = pd.json_normalize(
            df.to_dict(orient="records")
        )

        print("Nested JSON flattened successfully.")

    else:
        df = pd.read_json(filepath)

    return df


def document_ingestion(df, source):
    """
    Display an ingestion report.

    Args:
        df (pandas.DataFrame): Loaded dataset.
        source (str): Source file path.
    """

    print("\n" + "=" * 50)
    print("INGESTION REPORT")
    print("=" * 50)

    print(f"Source: {source}")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn Types:")
    print(df.dtypes)

    print("\nFirst 3 Rows:")
    print(df.head(3))

    print("=" * 50)


def main():
    """
    Run CSV and JSON ingestion examples.
    """

    print("\nStarting CSV & JSON Data Ingestion...\n")

    # Standard CSV
    csv_file = "data/raw/deliveries.csv"

    csv_data = ingest_csv(
        filepath=csv_file,
        delimiter=",",
        encoding="utf-8"
    )

    document_ingestion(
        csv_data,
        csv_file
    )

    # Semicolon-delimited CSV
    semicolon_file = "data/raw/deliveries_semicolon.csv"

    semicolon_data = ingest_csv(
        filepath=semicolon_file,
        delimiter=";",
        encoding="utf-8"
    )

    document_ingestion(
        semicolon_data,
        semicolon_file
    )

    # Nested JSON
    json_file = "data/raw/deliveries_nested.json"

    json_data = ingest_json(
        filepath=json_file,
        is_nested=True
    )

    document_ingestion(
        json_data,
        json_file
    )

    print("\nCSV & JSON ingestion completed successfully.")


if __name__ == "__main__":
    main()