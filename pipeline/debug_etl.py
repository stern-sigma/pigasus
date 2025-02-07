#!/usr/bin/env python
"""
Debug ETL Script

This script extracts and transforms data then prints detailed information
about the transformed dataframe to help diagnose why a SQL query might be
receiving a literal 'nan' value (which SQL Server sees as an invalid column name).
"""

import logging
import sys
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Import the extraction and transformation functions
from extract.extract import extract_plant_batch
from transform.transform import transform_and_clean_data

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def debug_transformed_data():
    logging.info("Starting debug for transformed data.")

    # --- Extraction Stage ---
    try:
        logging.info("Extracting data...")
        raw_data = extract_plant_batch()
        if not raw_data:
            logging.info("No data extracted. Exiting debug.")
            sys.exit(0)
    except Exception as e:
        logging.error("Extraction failed: %s", e)
        sys.exit(1)

    # --- Transformation Stage ---
    try:
        logging.info("Transforming data...")
        df = transform_and_clean_data(raw_data)
    except Exception as e:
        logging.error("Transformation failed: %s", e)
        sys.exit(1)

    # Print a sample of the transformed dataframe
    logging.info("Transformed Data Sample:\n%s", df.head())

    # Log the datatypes of each column
    logging.info("Data Types:\n%s", df.dtypes)

    # Log the count of missing values in each column
    logging.info("Missing Values Count:\n%s", df.isna().sum())

    # Show summary statistics (optional)
    logging.info("Data Summary:\n%s", df.describe(include='all'))

    # Convert NaN values to Python None and log a sample
    df_none = df.where(pd.notnull(df), None)
    logging.info("Data Sample After Converting NaN to None:\n%s", df_none.head())

    # Check if any object-type column contains the literal string "nan"
    for col in df.columns:
        if df[col].dtype == object:
            if df[col].isin(["nan"]).any():
                logging.warning("Column '%s' contains the literal string 'nan'", col)

    logging.info("Debugging complete.")


if __name__ == "__main__":
    debug_transformed_data()
