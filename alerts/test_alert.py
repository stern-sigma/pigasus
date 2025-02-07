import datetime
from unittest.mock import MagicMock, patch


from alert import (
    is_abnormal,
    fetch_readings,
    generate_email,
    lambda_handler,
)


def test_is_abnormal_normal():
    """Test that a reading within the normal range returns False."""
    reading = {"temperature": 20.0, "soil_moisture": 40.0}
    assert not is_abnormal(reading)

def test_is_abnormal_low_temperature():
    """Test that a reading with too low temperature returns True."""
    reading = {"temperature": 10.0, "soil_moisture": 40.0}
    assert is_abnormal(reading)

def test_is_abnormal_high_temperature():
    """Test that a reading with too high temperature returns True."""
    reading = {"temperature": 35.0, "soil_moisture": 40.0}
    assert is_abnormal(reading)

def test_is_abnormal_low_moisture():
    """Test that a reading with too low soil moisture returns True."""
    reading = {"temperature": 20.0, "soil_moisture": 10.0}
    assert is_abnormal(reading)

def test_is_abnormal_high_moisture():
    """Test that a reading with too high soil moisture returns True."""
    reading = {"temperature": 20.0, "soil_moisture": 65.0}
    assert is_abnormal(reading)



def test_generate_email():
    """
    Test that generate_email returns an HTML string containing the plant ID and
    details of the readings.
    """
    plant_id = 42
    reading_time = datetime.datetime(2025, 2, 6, 12, 0)
    readings = [{
        "at": reading_time,
        "temperature": 35.0,
        "soil_moisture": 10.0,
        "email": "test@example.com" 
    }]
    email_html = generate_email(plant_id, readings)
    assert f"Alert for Plant ID: {plant_id}" in email_html
    assert "35.0" in email_html
    assert "10.0" in email_html
    assert "2025-02-06 12:00:00" in email_html


@patch('alert.load_dotenv')
@patch('alert.fetch_readings')
@patch('alert.get_connection')
def test_lambda_handler(mock_get_connection, mock_fetch_readings, mock_load_dotenv):
    """
    Test that lambda_handler processes the readings correctly:
    - Only plants with at least 3 readings are considered.
    - Only plants whose last three readings are abnormal generate an alert.
    """
    dummy_conn = MagicMock()
    dummy_conn.close = MagicMock()
    mock_get_connection.return_value = dummy_conn

    now = datetime.datetime.now()
    # Set up dummy readings:
    readings = [
         # Plant 1 (should trigger alert)
         {'plant_id': 1, 'temperature': 35.0, 'soil_moisture': 10.0, 'at': now, 'email': 'eg1@example.com'},
         {'plant_id': 1, 'temperature': 34.0, 'soil_moisture': 15.0, 'at': now - datetime.timedelta(minutes=5), 'email': 'eg1@example.com'},
         {'plant_id': 1, 'temperature': 36.0, 'soil_moisture': 12.0, 'at': now - datetime.timedelta(minutes=10), 'email': 'eg1@example.com'},
         # Plant 2 (should be skipped: fewer than 3 readings)
         {'plant_id': 2, 'temperature': 35.0, 'soil_moisture': 10.0, 'at': now, 'email': 'eg2@example.com'},
         {'plant_id': 2, 'temperature': 35.0, 'soil_moisture': 10.0, 'at': now - datetime.timedelta(minutes=5), 'email': 'eg2@example.com'},
         # Plant 3 (should be skipped: one reading is normal)
         {'plant_id': 3, 'temperature': 35.0, 'soil_moisture': 10.0, 'at': now, 'email': 'eg3@example.com'},
         {'plant_id': 3, 'temperature': 20.0, 'soil_moisture': 40.0, 'at': now - datetime.timedelta(minutes=5), 'email': 'eg3@example.com'},
         {'plant_id': 3, 'temperature': 36.0, 'soil_moisture': 10.0, 'at': now - datetime.timedelta(minutes=10), 'email': 'eg3@example.com'},
    ]
    mock_fetch_readings.return_value = readings

    result = lambda_handler({}, {})

    # Only plant 1 should generate an alert...
    assert len(result) == 1
    alert = result[0]
    assert "Alert for Plant ID: 1" in alert["email"]
    assert alert["email_address"] == "eg1@example.com"
    dummy_conn.close.assert_called_once()
