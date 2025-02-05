"""This script will transform the data into a usable format for the DB."""
import pandas as pd

def convert_to_dataframe(raw_data:list[dict]):
    """Creates dataframe from data."""
    if not isinstance(raw_data, list):
        raise TypeError("Wrong format!")
    
    return pd.DataFrame(raw_data)

def parse_botanist_data(data_frame):
    """Returns the botanist data into separated columns in a DataFrame."""
    df = data_frame

    if "botanist" not in df.columns:
        raise KeyError("Botanist was not found!")
    df['botanist_email'] = df['botanist'].apply(
        lambda x: x['email'] if isinstance(
            x, dict) and 'email' in x else None if x is not None else None
    )
    df['botanist_name'] = df['botanist'].apply(
        lambda x: x['name'] if isinstance(
            x, dict) and 'name' in x else None if x is not None else None
    )
    df['botanist_phone'] = df['botanist'].apply(
        lambda x: x['phone'] if isinstance(
            x, dict) and 'phone' in x else None if x is not None else None
    )
    df = df.drop(columns=['botanist'])
    # pylint: disable=unsubscriptable-object
    df = df[[
        'botanist_email',
        'botanist_name',
        'botanist_phone',
        'last_watered',
        'name',
        'origin_location',
        'plant_id',
        'recording_taken',
        'soil_moisture',
        'temperature'
    ]]
    # pylint: disable=unsubscriptable-object
    return df

def parse_origin_location(data_frame):
    """Returns the origin location parsed into three columns"""
    df = data_frame

    if "origin_location" not in df.columns:
        raise KeyError("Botanist was not found!")
    df["region"] = df["origin_location"].apply(
        lambda x: x[2])  # Extract region
    df["country"] = df["origin_location"].apply(lambda x: x[3])

    df.drop(columns=["origin_location"], inplace=True)

    return df


def clean_scientific_name(data_frame):
    """Cleans the scientific_name column."""
    if "scientific_name" not in data_frame.columns:
        raise KeyError("scientific_name was not found!")
    data_frame['scientific_name'] = data_frame['scientific_name'].apply(
        lambda x: ', '.join([str(item) for item in x]) if isinstance(
            x, list) else (x if isinstance(x, str) else None)
    )
    return data_frame