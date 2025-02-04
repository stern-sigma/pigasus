"""This script tests for the transform script."""
import pytest
import pandas as pd
from transform import get_botanist_data


def test_get_botanist_data():
    """Tests for the right transformation of the botanist data."""
    raw_data = [{
        "botanist": {
            "email": "gertrude.jekyll@lnhm.co.uk",
            "name": "Gertrude Jekyll",
            "phone": "001-481-273-3691x127"
        },
        "last_watered": "Tue, 04 Feb 2025 13:54:32 GMT",
        "name": "Venus flytrap",
        "origin_location": [
            "33.95015", "-118.03917", "South Whittier", "US", "America/Los_Angeles"
        ],
        "plant_id": 1,
        "recording_taken": "2025-02-04 15:33:05",
        "soil_moisture": 94.17996217913385,
        "temperature": 12.041279102130597
    },
        {
        "botanist": {
            "email": "gertrude.jekyll@lnhm.co.uk",
            "name": "Gertrude Jekyll",
            "phone": "001-481-273-3691x127"
        },
        "last_watered": "Tue, 04 Feb 2025 13:54:32 GMT",
        "name": "Venus flytrap",
        "origin_location": [
            "33.95015", "-118.03917", "South Whittier", "US", "America/Los_Angeles"
        ],
        "plant_id": 1,
        "recording_taken": "2025-02-04 15:33:05",
        "soil_moisture": 94.17996217913385,
        "temperature": 12.041279102130597
    }]
    expected_data = [{
        "botanist_email": "gertrude.jekyll@lnhm.co.uk",
        "botanist_name": "Gertrude Jekyll",
        "botanist_phone": "001-481-273-3691x127",
        "last_watered": "Tue, 04 Feb 2025 13:54:32 GMT",
        "name": "Venus flytrap",
        "origin_location": ["33.95015", "-118.03917", "South Whittier", "US", "America/Los_Angeles"],
        "plant_id": 1,
        "recording_taken": "2025-02-04 15:33:05",
        "soil_moisture": 94.17996217913385,
        "temperature": 12.041279102130597
    },
        {
        "botanist_email": "gertrude.jekyll@lnhm.co.uk",
        "botanist_name": "Gertrude Jekyll",
        "botanist_phone": "001-481-273-3691x127",
        "last_watered": "Tue, 04 Feb 2025 13:54:32 GMT",
        "name": "Venus flytrap",
        "origin_location": ["33.95015", "-118.03917", "South Whittier", "US", "America/Los_Angeles"],
        "plant_id": 1,
        "recording_taken": "2025-02-04 15:33:05",
        "soil_moisture": 94.17996217913385,
        "temperature": 12.041279102130597
    }]

    expected_df = pd.DataFrame(expected_data)

    transformed_df = get_botanist_data(raw_data)

    pd.testing.assert_frame_equal(transformed_df, expected_df)


def test_botanist_data_column_missing_for_one_plant():
    """ Tests when the 'botanist' field is missing entirely for one record (botanist key missing)"""
    raw_data = [
        {'botanist': {'email': 'john.doe@example.com', 'name': 'John Doe', 'phone': '123456789'},
         'last_watered': '2025-02-01', 'name': 'Plant 1', 'origin_location': 'Location 1', 'plant_id': 1,
         'recording_taken': '2025-02-01', 'soil_moisture': 0.3, 'temperature': 22},
        {'last_watered': '2025-02-02', 'name': 'Plant 2', 'origin_location': 'Location 2', 'plant_id': 2,
         'recording_taken': '2025-02-02', 'soil_moisture': 0.4, 'temperature': 21},
        {'botanist': {'email': 'jane.doe@example.com', 'name': 'Jane Doe', 'phone': '987654321'},
         'last_watered': '2025-02-03', 'name': 'Plant 3', 'origin_location': 'Location 3', 'plant_id': 3,
         'recording_taken': '2025-02-03', 'soil_moisture': 0.5, 'temperature': 23}
    ]

    expected_result = pd.DataFrame({
        'botanist_email': ['john.doe@example.com', None, 'jane.doe@example.com'],
        'botanist_name': ['John Doe', None, 'Jane Doe'],
        'botanist_phone': ['123456789', None, '987654321'],
        'last_watered': ['2025-02-01', '2025-02-02', '2025-02-03'],
        'name': ['Plant 1', 'Plant 2', 'Plant 3'],
        'origin_location': ['Location 1', 'Location 2', 'Location 3'],
        'plant_id': [1, 2, 3],
        'recording_taken': ['2025-02-01', '2025-02-02', '2025-02-03'],
        'soil_moisture': [0.3, 0.4, 0.5],
        'temperature': [22, 21, 23]
    })

    result = get_botanist_data(raw_data)
    pd.testing.assert_frame_equal(result, expected_result)


