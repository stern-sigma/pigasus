"""Script to extract data older than 24 hours from the database 
in preparation for loading into the S3 bucket as parquet files."""

# pylint: disable=unused-argument, no-name-in-module

from os import environ
from datetime import date
import pandas as pd
from pymssql import connect, Connection
from dotenv import load_dotenv
from boto3 import client


def get_connection() -> Connection:
    """Returns a connection object to connect to the database."""
    conn = connect(
        server="host.docker.internal",
        user="sa",
        password="Password.1",
        database="plants",
        as_dict=True
    )
    return conn


def get_old_data(conn: Connection) -> pd.DataFrame:
    """Returns old data from the database as a dataframe."""
    query = """USE plants;
            SELECT * FROM alpha.reading
            WHERE DATEDIFF(HOUR, at, CURRENT_TIMESTAMP) > 24"""

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    old_data_df = pd.DataFrame(rows)

    return old_data_df


def format_dataframe(old_data: pd.DataFrame) -> pd.DataFrame:
    """Returns a dataframe formatted for conversion to parquet."""
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


def upload_to_bucket(s3_client: client, filepath: str, bucket=str) -> None:
    """Uploads parquet file to S3 bucket."""
    name = f"plant_data_{date.today()}.parquet"
    s3_client.upload_file(filepath, bucket, name)


def handler(event=None, context=None) -> None:
    """Lambda handler to connect to the database, 
    get data older than 24 hours and save to parquet."""

    conn = get_connection()

    data = get_old_data(conn)

    formatted_data = format_dataframe(data)

    formatted_data.to_parquet("/tmp/df.parquet")

    upload_to_bucket(s3, "/tmp/df.parquet", bucket_name)

    delete_old_data(conn)

    return "Finished"


if __name__ == "__main__":

    load_dotenv()

    print(handler())
