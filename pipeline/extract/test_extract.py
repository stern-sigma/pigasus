"""
Tests for both functions in the extract module.
Mocking API calls and user functions to keep tests isolated.
"""

from unittest.mock import patch, Mock
import pytest
import extract


@pytest.fixture
def base_url():
    """Fixture providing a dummy API base URL for tests."""
    return "https://dummyapi.com/"


@patch('extract.get')
def test_get_plant_data_success_returns_dict(mock_get, base_url):
    """
    Test that get_plant_data returns a dict when the API call succeeds.
    """
    dummy_response = Mock()
    dummy_response.status_code = 200
    dummy_response.json.return_value = {"plant_id": 1, "name": "Test Plant"}
    mock_get.return_value = dummy_response

    result = extract.get_plant_data(base_url, 1)
    assert isinstance(result, dict)


@patch('extract.get')
def test_get_plant_data_success_returns_correct_plant_id(mock_get, base_url):
    """
    Test that get_plant_data returns the correct plant_id.
    """
    dummy_response = Mock()
    dummy_response.status_code = 200
    dummy_response.json.return_value = {"plant_id": 1, "name": "Test Plant"}
    mock_get.return_value = dummy_response

    result = extract.get_plant_data(base_url, 1)
    assert result["plant_id"] == 1


@patch('extract.get')
def test_get_plant_data_success_returns_correct_name(mock_get, base_url):
    """
    Test that get_plant_data returns the correct name.
    """
    dummy_response = Mock()
    dummy_response.status_code = 200
    dummy_response.json.return_value = {"plant_id": 1, "name": "Test Plant"}
    mock_get.return_value = dummy_response

    result = extract.get_plant_data(base_url, 1)
    assert result["name"] == "Test Plant"


@patch('extract.get')
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
        extract.get_plant_data(base_url, 1)
    assert "Failed to fetch data for plant ID 1" in str(exc_info.value)


@patch('extract.get', side_effect=extract.exceptions.ReadTimeout("Simulated timeout"))
def test_get_plant_data_timeout_message(base_url):
    """
    Test that get_plant_data raises a ValueError with the correct message
    when a timeout occurs.
    """
    with pytest.raises(ValueError) as exc_info:
        extract.get_plant_data(base_url, 1)
    assert "Request timed out for plant ID 1" in str(exc_info.value)


@patch('extract.get_plant_data')
def test_extract_plant_batch_returns_list_type(mock_get_plant_data):
    """
    Test that extract_plant_batch() returns a list.
    """
    def dummy_get_plant_data(_base_url, plant_id):
        return {"plant_id": plant_id, "name": f"Plant {plant_id}"}
    mock_get_plant_data.side_effect = dummy_get_plant_data

    result = extract.extract_plant_batch()
    assert isinstance(result, list)


@patch('extract.get_plant_data')
def test_extract_plant_batch_returns_list_length(mock_get_plant_data):
    """
    Test that extract_plant_batch() returns 50 items when all API calls succeed.
    """
    def dummy_get_plant_data(_base_url, plant_id):
        return {"plant_id": plant_id, "name": f"Plant {plant_id}"}
    mock_get_plant_data.side_effect = dummy_get_plant_data

    result = extract.extract_plant_batch()
    assert len(result) == 50


@patch('extract.get_plant_data')
def test_extract_plant_batch_first_item_plant_id(mock_get_plant_data):
    """
    Test that the first item returned by extract_plant_batch() has plant_id equal to 1.
    """
    def dummy_get_plant_data(_base_url, plant_id):
        return {"plant_id": plant_id, "name": f"Plant {plant_id}"}
    mock_get_plant_data.side_effect = dummy_get_plant_data

    result = extract.extract_plant_batch()
    assert result[0]["plant_id"] == 1


@patch('extract.get_plant_data')
def test_extract_plant_batch_first_item_name(mock_get_plant_data):
    """
    Test that the first item returned by extract_plant_batch() has the correct name.
    """
    def dummy_get_plant_data(_base_url, plant_id):
        return {"plant_id": plant_id, "name": f"Plant {plant_id}"}
    mock_get_plant_data.side_effect = dummy_get_plant_data

    result = extract.extract_plant_batch()
    assert result[0]["name"] == "Plant 1"


@patch('extract.get_plant_data')
def test_extract_plant_batch_failure_returns_25_items(mock_get_plant_data):
    """
    Test that extract_plant_batch() returns 25 items when every even plant call fails.
    """
    def dummy_get_plant_data_failure(_base_url, plant_id):
        if plant_id % 2 == 0:
            raise ValueError("Simulated failure")
        return {"plant_id": plant_id, "name": f"Plant {plant_id}"}
    mock_get_plant_data.side_effect = dummy_get_plant_data_failure

    result = extract.extract_plant_batch()
    assert len(result) == 25


@patch('extract.get_plant_data')
def test_extract_plant_batch_failure_contains_only_odd_plant_ids(mock_get_plant_data):
    """
    Test that extract_plant_batch()'s result contains only odd plant_ids when even calls fail.
    """
    def dummy_get_plant_data_failure(_base_url, plant_id):
        if plant_id % 2 == 0:
            raise ValueError("Simulated failure")
        return {"plant_id": plant_id, "name": f"Plant {plant_id}"}
    mock_get_plant_data.side_effect = dummy_get_plant_data_failure

    result = extract.extract_plant_batch()
    for plant in result:
        assert plant["plant_id"] % 2 == 1
