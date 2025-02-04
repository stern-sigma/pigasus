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
def test_get_plant_data_success(mock_get, base_url):
    """
    Test that get_plant_data returns correct data when the API call succeeds.
    """
    dummy_response = Mock()
    dummy_response.status_code = 200
    dummy_response.json.return_value = {"plant_id": 1, "name": "Test Plant"}
    mock_get.return_value = dummy_response

    result = extract.get_plant_data(base_url, 1)
    assert isinstance(result, dict)
    assert result["plant_id"] == 1
    assert result["name"] == "Test Plant"


@patch('extract.get')
def test_get_plant_data_failure(mock_get, base_url):
    """
    Test that get_plant_data raises a ValueError when the API returns a non-200 status.
    """
    dummy_response = Mock()
    dummy_response.status_code = 404
    dummy_response.json.return_value = {}
    mock_get.return_value = dummy_response

    with pytest.raises(ValueError) as exc_info:
        extract.get_plant_data(base_url, 1)
    assert "Failed to fetch data for plant ID 1" in str(exc_info.value)


@patch('extract.get', side_effect=extract.exceptions.ReadTimeout("Simulated timeout"))
def test_get_plant_data_timeout(base_url):
    """
    Test that get_plant_data raises a ValueError when a timeout occurs.
    """
    with pytest.raises(ValueError) as exc_info:
        extract.get_plant_data(base_url, 1)
    assert "Request timed out for plant ID 1" in str(exc_info.value)


@patch('extract.get_plant_data')
def test_main_returns_list(mock_get_plant_data):
    """
    Test that main() returns a list of 50 dictionaries when all API calls succeed.
    """
    def dummy_get_plant_data(_base_url, plant_id):
        return {"plant_id": plant_id, "name": f"Plant {plant_id}"}
    mock_get_plant_data.side_effect = dummy_get_plant_data

    result = extract.main()
    assert isinstance(result, list)
    assert len(result) == 50
    for plant in result:
        assert "plant_id" in plant
        assert plant["name"] == f"Plant {plant['plant_id']}"


@patch('extract.get_plant_data')
def test_main_handles_failures(mock_get_plant_data):
    """
    Test that main() gracefully handles failures.
    Here, the dummy function raises a ValueError for even plant IDs.
    """
    def dummy_get_plant_data_with_failures(_base_url, plant_id):
        if plant_id % 2 == 0:
            raise ValueError("Simulated failure")
        return {"plant_id": plant_id, "name": f"Plant {plant_id}"}
    mock_get_plant_data.side_effect = dummy_get_plant_data_with_failures

    result = extract.main()
    # Out of 50 plants, even-numbered IDs fail, so we expect 25 successes.
    assert len(result) == 25
    for plant in result:
        assert plant["plant_id"] % 2 == 1
