"""This script tests for the transform script."""
import pytest
import pandas as pd
import numpy as np
from transform import parse_botanist_data, parse_origin_location, convert_to_dataframe, clean_scientific_name, clean_image_data, format_watered_column


def test_get_botanist_data():
    """Tests for the right transformation of the botanist data."""
    raw_data = convert_to_dataframe([{
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
    }])
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

    transformed_df = parse_botanist_data(raw_data)

    pd.testing.assert_frame_equal(transformed_df, expected_df)


def test_botanist_data_column_missing_for_one_plant():
    """ Tests when the 'botanist' field is missing entirely for one record (botanist key missing)"""
    raw_data = convert_to_dataframe([
        {'botanist': {'email': 'john.doe@example.com', 'name': 'John Doe', 'phone': '123456789'},
         'last_watered': '2025-02-01', 'name': 'Plant 1', 'origin_location': 'Location 1', 'plant_id': 1,
         'recording_taken': '2025-02-01', 'soil_moisture': 0.3, 'temperature': 22},
        {'last_watered': '2025-02-02', 'name': 'Plant 2', 'origin_location': 'Location 2', 'plant_id': 2,
         'recording_taken': '2025-02-02', 'soil_moisture': 0.4, 'temperature': 21},
        {'botanist': {'email': 'jane.doe@example.com', 'name': 'Jane Doe', 'phone': '987654321'},
         'last_watered': '2025-02-03', 'name': 'Plant 3', 'origin_location': 'Location 3', 'plant_id': 3,
         'recording_taken': '2025-02-03', 'soil_moisture': 0.5, 'temperature': 23}
    ])

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

    result = parse_botanist_data(raw_data)
    pd.testing.assert_frame_equal(result, expected_result)


def test_parse_origin_location_valid_data():

    raw_data = convert_to_dataframe([
        {
            "botanist": {
                "email": "gertrude.jekyll@lnhm.co.uk",
                "name": "Gertrude Jekyll",
                "phone": "001-481-273-3691x127"
            },
            "last_watered": "Tue, 04 Feb 2025 13:54:32 GMT",
            "name": "Venus flytrap",
            "origin_location": [
                "33.95015",
                "-118.03917",
                "South Whittier",
                "US",
                "America/Los_Angeles"
            ],
            "plant_id": 1,
            "recording_taken": "2025-02-04 15:33:05",
            "soil_moisture": 94.17996217913385,
            "temperature": 12.041279102130597
        }
    ])

    df = parse_origin_location(raw_data)

    assert "region" in df.columns
    assert "country" in df.columns
    assert "origin_location" not in df.columns


def test_parse_origin_location_values():

    raw_data = convert_to_dataframe([
        {
            "origin_location": [
                "33.95015",
                "-118.03917",
                "South Whittier",
                "US",
                "America/Los_Angeles"
            ]
        }
    ])

    df = parse_origin_location(raw_data)

    assert df.loc[0, "region"] == "South Whittier"
    assert df.loc[0, "country"] == "US"


def test_parse_origin_location_missing_key():

    raw_data_invalid = convert_to_dataframe([{"some_other_key": "value"}])
    with pytest.raises(KeyError, match="Botanist was not found!"):
        parse_origin_location(raw_data_invalid)

def test_convert_to_dataframe_checks_valid_type():
    sample = ""

    with pytest.raises(TypeError):
        convert_to_dataframe(sample)


def test_clean_scientific_with_lists():
    """Test case where scientific_name contains a list of names."""
    data = {'scientific_name': [['Sarracenia catesbaei'], [
        'Wollemia nobilis'], ['Pereskia grandifolia']]}
    df = pd.DataFrame(data)
    result = clean_scientific_name(df)
    expected = {'scientific_name': [
        'Sarracenia catesbaei', 'Wollemia nobilis', 'Pereskia grandifolia']}
    expected_df = pd.DataFrame(expected)
    pd.testing.assert_frame_equal(result, expected_df)


def test_clean_scientific_with_strings():
    """Test case where scientific_name contains strings."""
    data = {'scientific_name': ['Sarracenia catesbaei',
                                'Wollemia nobilis', 'Pereskia grandifolia']}
    df = pd.DataFrame(data)
    result = clean_scientific_name(df)
    expected = {'scientific_name': [
        'Sarracenia catesbaei', 'Wollemia nobilis', 'Pereskia grandifolia']}
    expected_df = pd.DataFrame(expected)
    pd.testing.assert_frame_equal(result, expected_df)


def test_clean_scientific_with_none_values():
    """Test case where scientific_name contains None (null) values."""
    data = {'scientific_name': [None, None, None]}
    df = pd.DataFrame(data)
    result = clean_scientific_name(df)
    expected = {'scientific_name': [None, None, None]}
    expected_df = pd.DataFrame(expected)
    pd.testing.assert_frame_equal(result, expected_df)


def test_clean_scientific_missing_column():
    """Test case where scientific_name column is missing from the DataFrame."""
    df = pd.DataFrame({'some_other_column': [1, 2, 3]})
    with pytest.raises(KeyError):
        clean_scientific_name(df)


def test_parse_botanist_data_missing_column():
    """Test case where scientific_name column is missing from the DataFrame."""
    df = pd.DataFrame({'some_other_column': [1, 2, 3]})
    with pytest.raises(KeyError):
        parse_botanist_data(df)


def test_columns_exist():
    """Test that the new columns are correctly created."""
    data = [{
        "images": {
            "license": 45,
            "license_name": "Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)",
            "license_url": "https://creativecommons.org/licenses/by-sa/3.0/deed.en",
            "original_url": "https://perenual.com/storage/species_image/2773_epipremnum_aureum/og/2560px-Epipremnum_aureum_31082012.jpg"
        },
        "name": "Epipremnum Aureum"
    }]

    df = pd.DataFrame(data)
    cleaned_df = clean_image_data(df)

    assert 'image_license' in cleaned_df.columns
    assert 'image_license_name' in cleaned_df.columns
    assert 'image_license_url' in cleaned_df.columns
    assert 'image_original_url' in cleaned_df.columns

def test_valid_url_format():
    """Test that 'image_original_url' contains a valid URL."""
    data = [{
        "images": {
            "license": 45,
            "license_name": "Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)",
            "license_url": "https://creativecommons.org/licenses/by-sa/3.0/deed.en",
            "original_url": "https://perenual.com/storage/species_image/2773_epipremnum_aureum/og/2560px-Epipremnum_aureum_31082012.jpg"
        },
        "name": "Epipremnum Aureum"
    }]

    df = pd.DataFrame(data)
    cleaned_df = clean_image_data(df)

    assert cleaned_df['image_original_url'].iloc[0].startswith('https://')


def test_clean_images_column_missing():
    """Test case where scientific_name column is missing from the DataFrame."""
    df = pd.DataFrame({'some_other_column': [1, 2, 3]})
    with pytest.raises(KeyError):
        clean_image_data(df)


def test_valid_datetime():
    data_valid = [{
        "last_watered": "Wed, 05 Feb 2025 14:04:23 GMT",
        "name": "Begonia"
    }]
    df_valid = pd.DataFrame(data_valid)
    formatted_df_valid = format_watered_column(df_valid)

    print(formatted_df_valid["last_watered"])

    assert isinstance(formatted_df_valid['last_watered'][0], pd.Timestamp)


def test_clean_water_column_missing():
    """Test case where scientific_name column is missing from the DataFrame."""
    df = pd.DataFrame({'some_other_column': [1, 2, 3]})
    with pytest.raises(KeyError):
        format_watered_column(df)


def test_datetime_with_timezone():
    data_timezone = [{
        "last_watered": "Mon, 02 Feb 2025 08:00:00 GMT",
        "name": "Orchid"
    }]
    df_timezone = pd.DataFrame(data_timezone)
    formatted_df_timezone = format_watered_column(df_timezone)
    assert formatted_df_timezone['last_watered'][0] == pd.to_datetime(
        "Mon, 02 Feb 2025 08:00:00 GMT")
