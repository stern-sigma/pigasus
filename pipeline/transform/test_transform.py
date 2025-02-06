"""This script tests for the transform script."""
import pytest
import pandas as pd
import numpy as np
from transform import (
    parse_botanist_data,
    parse_origin_location,
    convert_to_dataframe,
    clean_scientific_name,
    clean_image_data,
    format_watered_column,
    format_recording_taken,
    capitalise_plant_name,
    validate_soil_moisture,
    process_temperature_column,
    transform_and_clean_data
)

def test_convert_to_dataframe():
    raw_data = [{"name": "Plant 1", "scientific_name": ["Plantus", "Maximus"]}]
    df = convert_to_dataframe(raw_data)
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 1
    assert df.shape[1] == 2


def test_convert_to_dataframe_invalid_input():
    raw_data = "Invalid data format"
    try:
        convert_to_dataframe(raw_data)
    except TypeError:
        pass
    else:
        assert False


def test_parse_botanist_data_columns():
    raw_data = [{"name": "Plant 1", "botanist": {
        "email": "botanist1@example.com", "name": "Botanist One", "phone": "123456789"}}]
    df = convert_to_dataframe(raw_data)
    df = parse_botanist_data(df)

    assert "botanist_email" in df.columns
    assert "botanist_name" in df.columns
    assert "botanist_phone" in df.columns


def test_parse_botanist_data_values():
    raw_data = [{"name": "Plant 1", "botanist": {
        "email": "botanist1@example.com", "name": "Botanist One", "phone": "123456789"}}]
    df = convert_to_dataframe(raw_data)
    df = parse_botanist_data(df)

    assert df["botanist_email"][0] == "botanist1@example.com"
    assert df["botanist_name"][0] == "Botanist One"
    assert df["botanist_phone"][0] == "123456789"


def test_parse_botanist_data_missing_botanist_columns():
    raw_data = [{"name": "Plant 1"}]
    df = convert_to_dataframe(raw_data)
    df = parse_botanist_data(df)

    assert "botanist_email" in df.columns
    assert "botanist_name" in df.columns
    assert "botanist_phone" in df.columns


def test_parse_botanist_data_missing_botanist_values():
    raw_data = [{"name": "Plant 1"}]
    df = convert_to_dataframe(raw_data)
    df = parse_botanist_data(df)

    assert pd.isna(df["botanist_email"][0])
    assert pd.isna(df["botanist_name"][0])
    assert pd.isna(df["botanist_phone"][0])


def test_clean_scientific_name_valid():
    raw_data = [{"name": "Plant 1", "scientific_name": ["plantus", "maximus"]}]
    df = convert_to_dataframe(raw_data)
    df = clean_scientific_name(df)

    assert "scientific_name" in df.columns
    assert df["scientific_name"][0] == "Plantus, Maximus"


def test_clean_image_data_columns():
    raw_data = [{"name": "Plant 1", "images": {"license": "CC0", "license_name": "Public Domain",
                                               "license_url": "http://example.com", "original_url": "http://example.com/image.jpg"}}]
    df = convert_to_dataframe(raw_data)
    df = clean_image_data(df)

    assert "image_license" in df.columns
    assert "image_license_name" in df.columns
    assert "image_license_url" in df.columns
    assert "image_original_url" in df.columns


def test_clean_image_data_values():
    raw_data = [{"name": "Plant 1", "images": {"license": "CC0", "license_name": "Public Domain",
                                               "license_url": "http://example.com", "original_url": "http://example.com/image.jpg"}}]
    df = convert_to_dataframe(raw_data)
    df = clean_image_data(df)

    assert df["image_license"][0] == "CC0"
    assert df["image_license_name"][0] == "Public Domain"
    assert df["image_license_url"][0] == "http://example.com"
    assert df["image_original_url"][0] == "http://example.com/image.jpg"


def test_format_watered_column():
    raw_data = [{"name": "Plant 1", "last_watered": "2025-02-06T10:30:00"}]
    df = convert_to_dataframe(raw_data)
    df = format_watered_column(df)

    assert "last_watered" in df.columns
    assert isinstance(df["last_watered"][0], pd.Timestamp)


def test_format_recording_taken():
    raw_data = [{"name": "Plant 1", "recording_taken": "2025-02-06T10:30:00"}]
    df = convert_to_dataframe(raw_data)
    df = format_recording_taken(df)

    assert "recording_taken" in df.columns
    assert isinstance(df["recording_taken"][0], pd.Timestamp)



def test_capitalise_plant_name():
    raw_data = [{"name": "plant"}]
    df = convert_to_dataframe(raw_data)
    df = capitalise_plant_name(df)

    assert "name" in df.columns
    assert df["name"][0] == "Plant"


def test_parse_origin_location():
    raw_data = [{"name": "Plant 1", "origin_location": [
        "continent", "country", "region", "city"]}]
    df = convert_to_dataframe(raw_data)
    df = parse_origin_location(df)

    assert "region" in df.columns
    assert "country" in df.columns
    assert df["region"][0] == "region"
    assert df["country"][0] == "city"


def test_capitalise_plant_name_missing_column():
    raw_data = [{"botanist_email": "botanist@example.com",
                 "botanist_name": "Botanist One"}]
    df = convert_to_dataframe(raw_data)

    df = capitalise_plant_name(df)

    assert "name" in df.columns, "'name' column is missing"

    assert pd.isna(df["name"][0]), "'name' should be NaN"


def test_format_recording_taken_missing_column():
    raw_data = [{"botanist_email": "botanist@example.com",
                 "botanist_name": "Botanist One"}]
    df = convert_to_dataframe(raw_data)
    df = format_recording_taken(df)


    assert "recording_taken" in df.columns
    assert pd.isna(df["recording_taken"][0])


def test_format_watered_column_missing():
    raw_data = [{"botanist_email": "botanist@example.com",
                 "botanist_name": "Botanist One"}]
    df = convert_to_dataframe(raw_data)

    df = format_watered_column(df)

    assert "last_watered" in df.columns
    assert pd.isna(df["last_watered"][0])


def test_clean_scientific_name_missing_column():
    raw_data = [{"name": "Plant 1"}]
    df = convert_to_dataframe(raw_data)
    df = clean_scientific_name(df)
    assert "scientific_name" in df.columns
    assert pd.isna(df["scientific_name"][0])


def test_soil_moisture_column_creation():
    df = pd.DataFrame([{"name": "Plant 1"}])  # Missing soil_moisture
    result = validate_soil_moisture(df)
    assert "soil_moisture" in result.columns
    assert pd.isna(result["soil_moisture"].iloc[0])


def test_temperature_column_exists_and_valid():
    data = [
        {"temperature": 23.5},
        {"temperature": 15.8},
        {"temperature": 30.1}
    ]
    df = pd.DataFrame(data)
    processed_df = process_temperature_column(df)

    # Assert that temperatures are valid and retained
    assert processed_df['temperature'][0] == 23.5
    assert processed_df['temperature'][1] == 15.8
    assert processed_df['temperature'][2] == 30.1


def test_temperature_column_exists():
    raw_data = [
        {
            "botanist": {"email": "carl.linnaeus@lnhm.co.uk", "name": "Carl Linnaeus", "phone": "(146)994-1635x35992"},
            "last_watered": "Wed, 05 Feb 2025 14:03:04 GMT",
            "name": "Epipremnum Aureum",
            "plant_id": 50,
            "recording_taken": "2025-02-06 12:44:11",
            "soil_moisture": 20.9415458664085,
            "temperature": 13.2073378873147
        }
    ]
    df = transform_and_clean_data(raw_data)
    assert "temperature" in df.columns


def test_temperature_column_type():
    raw_data = [
        {
            "botanist": {"email": "carl.linnaeus@lnhm.co.uk", "name": "Carl Linnaeus", "phone": "(146)994-1635x35992"},
            "last_watered": "Wed, 05 Feb 2025 14:03:04 GMT",
            "name": "Epipremnum Aureum",
            "plant_id": 50,
            "recording_taken": "2025-02-06 12:44:11",
            "soil_moisture": 20.9415458664085,
            "temperature": 13.2073378873147
        }
    ]
    df = transform_and_clean_data(raw_data)
    assert pd.api.types.is_float_dtype(df["temperature"])


def test_invalid_temperature_is_nan():
    raw_data = [
        {
            "botanist": {"email": "gertrude.jekyll@lnhm.co.uk", "name": "Gertrude Jekyll", "phone": "001-481-273-3691x127"},
            "last_watered": "Wed, 05 Feb 2025 13:54:32 GMT",
            "name": "Venus flytrap",
            "plant_id": 1,
            "recording_taken": "2025-02-06 13:15:07",
            "soil_moisture": 17.2879767785433,
            "temperature": "invalid_temperature"
        }
    ]
    df = transform_and_clean_data(raw_data)
    assert df["temperature"][0] != "invalid_temperature"
    assert np.isnan(df["temperature"][0])


def test_name_column_exists():
    raw_data = [
        {
            "botanist": {"email": "carl.linnaeus@lnhm.co.uk", "name": "Carl Linnaeus", "phone": "(146)994-1635x35992"},
            "last_watered": "Wed, 05 Feb 2025 14:03:04 GMT",
            "name": "Epipremnum Aureum",
            "plant_id": 50,
            "recording_taken": "2025-02-06 12:44:11",
            "soil_moisture": 20.9415458664085,
            "temperature": 13.2073378873147
        }
    ]
    df = transform_and_clean_data(raw_data)
    assert "name" in df.columns


def test_soil_moisture_column_type():
    raw_data = [
        {
            "botanist": {"email": "carl.linnaeus@lnhm.co.uk", "name": "Carl Linnaeus", "phone": "(146)994-1635x35992"},
            "last_watered": "Wed, 05 Feb 2025 14:03:04 GMT",
            "name": "Epipremnum Aureum",
            "plant_id": 50,
            "recording_taken": "2025-02-06 12:44:11",
            "soil_moisture": 20.9415458664085,
            "temperature": 13.2073378873147
        }
    ]
    df = transform_and_clean_data(raw_data)
    assert "soil_moisture" in df.columns
    assert pd.api.types.is_float_dtype(df["soil_moisture"])


def test_soil_moisture_valid():
    raw_data = [
        {
            "botanist": {"email": "carl.linnaeus@lnhm.co.uk", "name": "Carl Linnaeus", "phone": "(146)994-1635x35992"},
            "last_watered": "Wed, 05 Feb 2025 14:03:04 GMT",
            "name": "Epipremnum Aureum",
            "plant_id": 50,
            "recording_taken": "2025-02-06 12:44:11",
            "soil_moisture": 20.9415458664085,
            "temperature": 13.2073378873147
        }
    ]
    df = transform_and_clean_data(raw_data)
    assert not np.isnan(df["soil_moisture"][0])


def test_scientific_name_column_exists():
    raw_data = [
        {
            "botanist": {"email": "carl.linnaeus@lnhm.co.uk", "name": "Carl Linnaeus", "phone": "(146)994-1635x35992"},
            "last_watered": "Wed, 05 Feb 2025 14:03:04 GMT",
            "name": "Epipremnum Aureum",
            "plant_id": 50,
            "recording_taken": "2025-02-06 12:44:11",
            "soil_moisture": 20.9415458664085,
            "temperature": 13.2073378873147,
            "scientific_name": ["Epipremnum aureum"]
        }
    ]
    df = transform_and_clean_data(raw_data)
    assert "scientific_name" in df.columns


def test_last_watered_column_datetime():
    raw_data = [
        {
            "botanist": {"email": "carl.linnaeus@lnhm.co.uk", "name": "Carl Linnaeus", "phone": "(146)994-1635x35992"},
            "last_watered": "Wed, 05 Feb 2025 14:03:04 GMT",
            "name": "Epipremnum Aureum",
            "plant_id": 50,
            "recording_taken": "2025-02-06 12:44:11",
            "soil_moisture": 20.9415458664085,
            "temperature": 13.2073378873147
        }
    ]
    df = transform_and_clean_data(raw_data)
    assert pd.to_datetime(df["last_watered"]).isnull().sum() == 0


def test_empty_data_returns_empty_df():
    empty_data = []
    empty_df = transform_and_clean_data(empty_data)
    assert empty_df.empty
