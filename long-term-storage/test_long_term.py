"""Tests for long term storage script."""
import os
from datetime import datetime
from long_term import get_old_data, format_dataframe, upload_to_bucket, get_connection
from unittest.mock import patch, MagicMock
import pytest
import pandas as pd
import moto
import boto3


@pytest.fixture
def old_data():
    return [
        {"reading_id": 3, "plant_id": 1, "soil_moisture": 30,
         "temperature": 22, "at": datetime.strptime("2025-02-02 15:10:00", "%Y-%m-%d %H:%M:%S"), "botanist_id": 2,
         "last_watered": datetime.strptime("2025-02-01 12:00:00", "%Y-%m-%d %H:%M:%S")},
        {"reading_id": 4, "plant_id": 2, "soil_moisture": 38,
         "temperature": 23, "at": datetime.strptime("2025-02-03 07:50:45", "%Y-%m-%d %H:%M:%S"), "botanist_id": 2,
         "last_watered": datetime.strptime("2025-02-02 18:45:30", "%Y-%m-%d %H:%M:%S")}
    ]


@pytest.fixture
def empty_bucket():
    moto_fake = moto.mock_s3()
    try:
        moto_fake.start()
        conn = boto3.resource('s3')
        conn.create_bucket(Bucket="OS_BUCKET")
        yield conn
    finally:
        moto_fake.stop()


@patch("long_term.get_connection")
def test_get_old_data(mock_connection, old_data):
    """Test to ensure pymssql connection is called."""

    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = old_data
    expected_output = pd.DataFrame(old_data)

    pd.testing.assert_frame_equal(
        get_old_data(mock_connection), expected_output)


@patch("long_term.get_connection")
def test_get_old_data_expected_datatype(mock_connection, old_data):
    """Test to ensure pymssql connection is called."""

    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = old_data

    assert type(get_old_data(mock_connection)) == pd.DataFrame


@pytest.mark.parametrize("column, datatype", [("at", "O"), ("last_watered", "O"), ("soil_moisture", "float"), ("temperature", "float")])
def test_format_dataframe_at(old_data, column, datatype):
    """Tests the formatting of 'at' column in the dataframe."""
    old_data_df = pd.DataFrame(old_data)
    assert format_dataframe(old_data_df)[f"{column}"].dtype == datatype


def test_format_dataframe_expected_output(old_data):
    old_data_df = pd.DataFrame(old_data)
    new_old_df = old_data_df.drop(columns="at")
    with pytest.raises(KeyError):
        format_dataframe(new_old_df)


@moto.mock_aws
def test_upload_bucket(tmp_path):
    """Tests that files are uploaded to the bucket."""
    temp_file = tmp_path/"data.parquet"
    temp_file.write_text("fake_data", encoding="utf-8")

    conn = boto3.resource("s3", region_name="eu-west-2")
    conn.create_bucket(Bucket="plant", CreateBucketConfiguration={
                       'LocationConstraint': "eu-west-2"})
    s3 = boto3.client("s3", aws_access_key_id="fake key",
                      aws_secret_access_key="fake secret key", region_name="eu-west-2")
    upload_to_bucket(s3, temp_file, "plant")

    uploaded_objects = [o["Key"]
                        for o in s3.list_objects(Bucket="plant")["Contents"]]
    assert "plant_data_2025-02-05.parquet" in uploaded_objects


@patch.dict(os.environ, {"DB_HOST": "host", "DB_USER": "user", "DB_PASSWORD": "password", "DB_NAME": "namee"})
@patch("long_term.connect")
def test_get_connection(mock_conn):
    """Test connection object is called."""
    mock_conn.return_value = MagicMock()
    get_connection()
    mock_conn.assert_called()


@patch("long_term.get_connection")
def test_get_old_data_raises_error(mock_connection, old_data):
    """Tests get old data raises error if no data older than 24 hours in the database."""

    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = []

    with pytest.raises(ValueError):
        get_old_data(mock_connection)
