"""
ETL Pipeline: Extract, Transform, and Upload.
This script is runnable as a single command.
First we will test this pipeline locally, then we will make it a Lambda handler and dockerise it.
It will be run once a minute by a scheduler.
"""
# pylint: disable=broad-exception-caught

import sys
import logging
from dotenv import load_dotenv

from extract.extract import extract_plant_batch
from transform.transform import transform_and_clean_data
from upload.upload import (
    get_connection,
    upload_new_plants_with_location,
    update_botanists,
    upload_reading_data
)


load_dotenv()



logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def etl_batch():
    """Single runnable script for whole pipeline process for one batch of plant readings"""
    logging.info("Starting ETL pipeline...")

    try:
        logging.info("Extracting data...")
        raw_data = extract_plant_batch()
        if not raw_data:
            logging.info("No data extracted. Exiting pipeline.")
            sys.exit(0)
    except Exception as e:
        logging.error("Extraction failed: %s", e)
        sys.exit(1)

    try:
        logging.info("Transforming data...")
        transformed_df = transform_and_clean_data(raw_data)
    except Exception as e:
        logging.error("Transformation failed: %s", e)
        sys.exit(1)


    try:
        logging.info("Connecting to the database...")
        conn = get_connection()
    except Exception as e:
        logging.error("Database connection failed: %s", e)
        sys.exit(1)

    try:
        logging.info("Uploading new plant data...")
        upload_new_plants_with_location(conn, transformed_df)
        logging.info("Updating botanists information...")
        update_botanists(conn, transformed_df)
        logging.info("Uploading sensor readings...")
        upload_reading_data(conn, transformed_df)
    except Exception as e:
        logging.error("Upload failed: %s", e)
        sys.exit(1)
    finally:
        conn.close()

    logging.info("ETL pipeline completed successfully.")


if __name__ == "__main__":
    etl_batch()
