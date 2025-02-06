"""Script to extract data older than 24 hours from the database 
in preparation for loading into the S3 bucket as parquet files."""

# pylint: disable=unused-argument, no-name-in-module

import logging
from os import environ, remove
from datetime import date
import pandas as pd
from pymssql import connect, Connection
from dotenv import load_dotenv
from boto3 import client


def get_connection() -> Connection:
    """Returns a connection object to connect to the database."""
    conn = connect(
        server=environ["DB_HOST"],
        user=environ["DB_USER"],
        password=environ["DB_PASSWORD"],
        database=environ["DB_NAME"],
        as_dict=True
    )
    return conn


def configure_logs() -> None:
    """Configures logger."""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')


def get_old_data(conn: Connection) -> pd.DataFrame:
    """Returns old data from the database as a dataframe."""
    query = """USE plants;
            SELECT * FROM alpha.reading
            WHERE DATEDIFF(HOUR, at, CURRENT_TIMESTAMP) > 24"""

    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    if rows == []:
        cur.close()
        logging.error("No present data older than 24 hours in the database.")
        raise ValueError(
            "No present data older than 24 hours in the database.")

    old_data_df = pd.DataFrame(rows)
    cur.close()
    return old_data_df


def format_dataframe(old_data: pd.DataFrame) -> pd.DataFrame:
    """Returns a dataframe formatted for conversion to parquet."""
    if any(key not in old_data for key in ["at", "last_watered", "soil_moisture", "temperature"]):
        logging.info("Database is missing keys!")
        raise KeyError("Database is missing keys!")

    old_data["at"] = old_data['at'].dt.strftime("%Y-%m-%d %H:%M:%S")
    old_data["last_watered"] = old_data["last_watered"].dt.strftime(
        "%Y-%m-%d %H:%M:%S")
    old_data['soil_moisture'] = old_data['soil_moisture'].astype(float)
    old_data['temperature'] = old_data['temperature'].astype(float)
    return old_data


def delete_old_data(conn: Connection) -> None:
    """Deletes data older than 24 hours from the database."""
    query = """
        USE plants;
        DELETE FROM alpha.reading
        WHERE DATEDIFF(HOUR, at, CURRENT_TIMESTAMP) > 24;
        """

    with conn.cursor() as cur:
        cur.execute(query)
        conn.commit()
    logging.info("Expired data deleted from plant database.")


def upload_to_bucket(s3_client: client, filepath: str, bucket=str) -> None:
    """Uploads parquet file to S3 bucket."""
    name = f"plant_data_{date.today()}.parquet"
    s3_client.upload_file(filepath, bucket, name)
    logging.info("Plant data uploaded to S3 bucket.")


def handler(event=None, context=None) -> None:
    """Lambda handler to connect to the database, 
    get data older than 24 hours and save to parquet."""

    configure_logs()

    conn = get_connection()
    data = get_old_data(conn)
    logging.info("Expired data retrieved from database.")
    formatted_data = format_dataframe(data)
    formatted_data.to_parquet("/tmp/df.parquet")

    s3 = client("s3", aws_access_key_id=environ["AWS_ACCESS_KEY"],
                aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"])
    upload_to_bucket(s3, "/tmp/df.parquet", environ["BUCKET_NAME"])

    remove("/tmp/df.parquet")

    delete_old_data(conn)

    logging.info("Finished!")
    return "Finished"


if __name__ == "__main__":

    load_dotenv()

    print(handler())
