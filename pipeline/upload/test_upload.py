"""Test functions from upload.py module"""

import pandas as pd
from unittest.mock import MagicMock, patch

from upload import (
    get_existing_plant_ids,
    upload_new_plants_with_location,
)

def test_get_existing_plant_ids_empty():
    """
    Test that if no plant_ids are passed, an empty set is returned
    and no query is executed.
    """
    mock_cursor = MagicMock()
    result = get_existing_plant_ids(mock_cursor, [])
    assert result == set()
    mock_cursor.execute.assert_not_called()

def test_get_existing_plant_ids_returns_set():
    """
    Test that get_existing_plant_ids returns the correct set given some fake database rows.
    """
    mock_cursor = MagicMock()
    # Suppose the database returns plant_ids 1 and 3 for the query.
    plant_ids = [1, 2, 3]
    mock_cursor.fetchall.return_value = [(1,), (3,)]
    result = get_existing_plant_ids(mock_cursor, plant_ids)
    placeholders = ", ".join(["%s"] * len(plant_ids))
    expected_query = f"SELECT plant_id FROM alpha.plant WHERE plant_id IN ({placeholders})"
    mock_cursor.execute.assert_called_once_with(expected_query, tuple(plant_ids))
    
    assert result == {1, 3}


@patch("upload.get_connection")
def test_upload_new_plants_with_location_no_new(mock_get_connection):
    """
    Test that if all plants in the DataFrame already exist, 
    the function prints a message and closes the connection without executing MERGE queries.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    test_plant_id = 9999
    data = pd.DataFrame([{
        "botanist_email": "test@example.com",
        "botanist_name": "Test Botanist",
        "botanist_phone": "123456789",
        "region": "Test Region",
        "country": "TR",
        "scientific_name": "Testus plantus",
        "image_license": 1,
        "license_name": "Test License",
        "image_original_url": "http://example.com/image.jpg",
        "last_watered": pd.to_datetime("2025-01-01 00:00:00"),
        "recording_taken": pd.to_datetime("2025-01-01 00:00:00"),
        "plant_id": test_plant_id,
        "soil_moisture": 50.0,
        "temperature": 20.0,
        "name": "Test Plant",
        "latitude": 10.0,
        "longitude": 20.0,
        "image_id": None
    }])
    
    mock_cursor.fetchall.return_value = [(test_plant_id,)]
    
    upload_new_plants_with_location(data)
    
    mock_conn.close.assert_called_once()
    # Because no new plant is uploaded, none of the MERGE queries should be executed.
    # (The first call to execute is in get_existing_plant_ids, but after that, nothing else should be executed.)
    assert mock_cursor.execute.call_count == 1


@patch("upload.get_connection")
def test_upload_new_plants_with_location_new(mock_get_connection):
    """
    Test that if a new plant is provided, the function executes the MERGE queries
    and commits/closes the connection.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    test_plant_id = 8888
    data = pd.DataFrame([{
        "botanist_email": "new@example.com",
        "botanist_name": "New Botanist",
        "botanist_phone": "987654321",
        "region": "New Region",
        "country": "NR",
        "scientific_name": "Newus plantus",
        "image_license": 1,
        "license_name": "New License",
        "image_original_url": "http://example.com/new_image.jpg",
        "last_watered": pd.to_datetime("2025-02-01 00:00:00"),
        "recording_taken": pd.to_datetime("2025-02-01 00:00:00"),
        "plant_id": test_plant_id,
        "soil_moisture": 60.0,
        "temperature": 22.0,
        "name": "New Plant",
        "latitude": 30.0,
        "longitude": 40.0,
        "image_id": None
    }])
    
    # Simulate that there are no existing plant_ids by returning an empty list.
    mock_cursor.fetchall.return_value = []
    
    upload_new_plants_with_location(data)
    
    # There are four MERGE statements in the loop for each plant.
    # In this case, we expect 4 execute calls inside the loop plus 1 call from get_existing_plant_ids.
    assert mock_cursor.execute.call_count == 5
    
    # Ensure that commit and close are called.
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()
