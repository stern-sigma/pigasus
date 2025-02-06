"""
Tests for both functions in the combination module.
Mocking API calls and user functions to keep tests isolated.
"""

from unittest.mock import patch, Mock
import pytest
import combination
import pandas as pd
import numpy as np

@pytest.fixture
def base_url():
    """Fixture providing a dummy API base URL for tests."""
    return "https://dummyapi.com/"


@patch('combination.get')
def test_get_plant_data_success_returns_dict(mock_get, base_url):
    """
    Test that get_plant_data returns a dict when the API call succeeds.
    """
    dummy_response = Mock()
    dummy_response.status_code = 200
    dummy_response.json.return_value = {"plant_id": 1, "name": "Test Plant"}
    mock_get.return_value = dummy_response

    result = combination.get_plant_data(base_url, 1)
    assert isinstance(result, dict)


@patch('combination.get')
def test_get_plant_data_success_returns_correct_plant_id(mock_get, base_url):
    """
    Test that get_plant_data returns the correct plant_id.
    """
    dummy_response = Mock()
    dummy_response.status_code = 200
    dummy_response.json.return_value = {"plant_id": 1, "name": "Test Plant"}
    mock_get.return_value = dummy_response

    result = combination.get_plant_data(base_url, 1)
    assert result["plant_id"] == 1


@patch('combination.get')
def test_get_plant_data_success_returns_correct_name(mock_get, base_url):
    """
    Test that get_plant_data returns the correct name.
    """
    dummy_response = Mock()
    dummy_response.status_code = 200
    dummy_response.json.return_value = {"plant_id": 1, "name": "Test Plant"}
    mock_get.return_value = dummy_response

    result = combination.get_plant_data(base_url, 1)
    assert result["name"] == "Test Plant"


@patch('combination.get')
def test_get_plant_data_failure_message(mock_get, base_url):
    """
    Test that get_plant_data raises a ValueError with the correct message
    when the API returns a non-200 status.
    """
    dummy_response = Mock()
    dummy_response.status_code = 404
    dummy_response.json.return_value = {}
    mock_get.return_value = dummy_response

    with pytest.raises(ValueError) as exc_info:
        combination.get_plant_data(base_url, 1)
    assert "Failed to fetch data for plant ID 1" in str(exc_info.value)


@patch('combination.get', side_effect=combination.exceptions.ReadTimeout("Simulated timeout"))
def test_get_plant_data_timeout_message(base_url):
    """
    Test that get_plant_data raises a ValueError with the correct message
    when a timeout occurs.
    """
    with pytest.raises(ValueError) as exc_info:
        combination.get_plant_data(base_url, 1)
    assert "Request timed out for plant ID 1" in str(exc_info.value)


@patch('combination.get_plant_data', return_value=[{}])
def test_extract_plant_batch_returns_list_type(mock_get_plant_data):
    """
    Test that extract_plant_batch() returns a list.
    """
    def dummy_get_plant_data(_base_url, plant_id):
        return {"plant_id": plant_id, "name": f"Plant {plant_id}"}
    mock_get_plant_data.side_effect = dummy_get_plant_data

    result = combination.extract_plant_batch()
    assert isinstance(result, list)


@patch('combination.get_max_plant_id', return_value=100)
@patch('combination.get_plant_data')
def test_extract_plant_batch_returns_list_length(mock_get_plant_data, mock_max_plant_id):
    """
    Test that extract_plant_batch() returns the correct number of items when all API calls succeed.
    """
    def dummy_get_plant_data(_base_url, plant_id):
        return {"plant_id": plant_id, "name": f"Plant {plant_id}"}
    mock_get_plant_data.side_effect = dummy_get_plant_data

    result = combination.extract_plant_batch()
    expected_length = 100 + 100 // 10  # Assuming get_max_plant_id returns 100, plus 10%
    assert len(result) == expected_length


@patch('combination.get_plant_data')
def test_extract_plant_batch_first_item_plant_id(mock_get_plant_data):
    """
    Test that the first item returned by extract_plant_batch() has plant_id equal to 1.
    """
    def dummy_get_plant_data(_base_url, plant_id):
        return {"plant_id": plant_id, "name": f"Plant {plant_id}"}
    mock_get_plant_data.side_effect = dummy_get_plant_data

    result = combination.extract_plant_batch()
    assert result[0]["plant_id"] == 1


@patch('combination.get_plant_data')
def test_extract_plant_batch_first_item_name(mock_get_plant_data):
    """
    Test that the first item returned by extract_plant_batch() has the correct name.
    """
    def dummy_get_plant_data(_base_url, plant_id):
        return {"plant_id": plant_id, "name": f"Plant {plant_id}"}
    mock_get_plant_data.side_effect = dummy_get_plant_data

    result = combination.extract_plant_batch()
    assert result[0]["name"] == "Plant 1"


@patch('combination.get_max_plant_id', return_value=50)
@patch('combination.get_plant_data')
def test_extract_plant_batch_failure_returns_half_items(mock_get_plant_data, mock_max_plant_id):
    """
    Test that extract_plant_batch() returns half items when every even plant call fails.
    """
    def dummy_get_plant_data_failure(_base_url, plant_id):
        if plant_id % 2 == 0:
            raise ValueError("Simulated failure")
        return {"plant_id": plant_id, "name": f"Plant {plant_id}"}
    mock_get_plant_data.side_effect = dummy_get_plant_data_failure

    result = combination.extract_plant_batch()
    total_plants = 50 + (50 // 10)  # 50 plants plus 10%
    expected_successful = (total_plants + 1) // 2
    # Plus 1 because we start counting from 1, which is odd
    assert len(result) == expected_successful


@patch('combination.get_plant_data')
def test_extract_plant_batch_failure_contains_only_odd_plant_ids(mock_get_plant_data):
    """
    Test that extract_plant_batch()'s result contains only odd plant_ids when even calls fail.
    """
    def dummy_get_plant_data_failure(_base_url, plant_id):
        if plant_id % 2 == 0:
            raise ValueError("Simulated failure")
        return {"plant_id": plant_id, "name": f"Plant {plant_id}"}
    mock_get_plant_data.side_effect = dummy_get_plant_data_failure

    result = combination.extract_plant_batch()
    for plant in result:
        assert plant["plant_id"] % 2 == 1


@patch('combination.get')
def test_get_max_plant_id_success(mock_get, base_url):
    """
    Test that get_max_plant_id returns the correct max plant ID when the API call succeeds.
    """
    dummy_response = Mock()
    dummy_response.status_code = 200
    dummy_response.json.return_value = {"plants_on_display": 100}
    mock_get.return_value = dummy_response

    max_plant_id = combination.get_max_plant_id(base_url)
    assert max_plant_id == 100


@patch('combination.get')
def test_get_max_plant_id_http_error(mock_get, base_url):
    """
    Test that get_max_plant_id raises ValueError when the API returns a non-200 status code.
    """
    dummy_response = Mock()
    dummy_response.status_code = 404
    dummy_response.json.return_value = {}
    mock_get.return_value = dummy_response

    with pytest.raises(ValueError):
        combination.get_max_plant_id(base_url)


@patch('combination.get')
def test_get_max_plant_id_missing_key(mock_get, base_url):
    """
    Test that get_max_plant_id raises ValueError when 'plants_on_display' key is missing.
    """
    dummy_response = Mock()
    dummy_response.status_code = 200
    dummy_response.json.return_value = {}
    mock_get.return_value = dummy_response

    with pytest.raises(ValueError):
        combination.get_max_plant_id(base_url)


def test_transform_and_clean_data():
    raw_data = [
        {
            "botanist": {"email": "carl.linnaeus@lnhm.co.uk", "name": "Carl Linnaeus", "phone": "(146)994-1635x35992"},
            "images": {"license": 45, "license_name": "Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)", "license_url": "https://creativecommons.org/licenses/by-sa/3.0/deed.en"},
            "last_watered": "Wed, 05 Feb 2025 14:03:04 GMT",
            "name": "Epipremnum Aureum",
            "origin_location": ["-19.32556", "-41.25528", "Resplendor", "BR", "America/Sao_Paulo"],
            "plant_id": 50,
            "recording_taken": "2025-02-06 12:44:11",
            "scientific_name": ["Epipremnum aureum"],
            "soil_moisture": 20.9415458664085,
            "temperature": 13.2073378873147
        },
        {
            "botanist": {"email": "gertrude.jekyll@lnhm.co.uk", "name": "Gertrude Jekyll", "phone": "001-481-273-3691x127"},
            "last_watered": "Wed, 05 Feb 2025 13:54:32 GMT",
            "name": "Venus flytrap",
            "origin_location": ["33.95015", "-118.03917", "South Whittier", "US", "America/Los_Angeles"],
            "plant_id": 1,
            "recording_taken": "2025-02-06 13:15:07",
            "soil_moisture": 17.2879767785433,
            "temperature": "invalid_temperature"  # Invalid temperature value
        }
    ]

    df = combination.transform_and_clean_data(raw_data)

    assert "temperature" in df.columns
    assert pd.api.types.is_float_dtype(df["temperature"])

    assert df["temperature"][1] != "invalid_temperature"
    assert np.isnan(df["temperature"][1])

    assert "name" in df.columns
    assert "soil_moisture" in df.columns

    assert pd.api.types.is_float_dtype(df["soil_moisture"])
    assert not np.isnan(df["soil_moisture"][0])

    assert "scientific_name" in df.columns
    assert df["scientific_name"][1] is not None

    assert pd.to_datetime(df["last_watered"]).isnull().sum() == 0
    empty_data = []
    empty_df = combination.transform_and_clean_data(empty_data)
    assert empty_df.empty
