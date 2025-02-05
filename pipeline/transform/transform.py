"""This script will transform the data into a usable format for the DB."""
import pandas as pd
import numpy as np
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

def clean_image_data(data_frame):
    """Returns the images column into separate columns."""
    df = data_frame
    if "images" not in df.columns:
        raise KeyError("images was not found!")
    df['image_license'] = df['images'].apply(lambda x: x.get(
        'license') if isinstance(x, dict) and x.get('license') is not None else np.nan)
    df['image_license_name'] = df['images'].apply(lambda x: x.get(
        'license_name') if isinstance(x, dict) and x.get('license_name') is not None else np.nan)
    df['image_license_url'] = df['images'].apply(lambda x: x.get(
        'license_url') if isinstance(x, dict) and x.get('license_url') is not None else np.nan)
    df['image_original_url'] = df['images'].apply(lambda x: x.get(
        'original_url') if isinstance(x, dict) and x.get('original_url') is not None else np.nan)

    # Drop the original 'images' column
    df = df.drop(columns=['images'])

    # Ensure that image_original_url starts with 'https://' if it's not NaN
    df['image_original_url'] = df['image_original_url'].apply(
        lambda x: x if isinstance(x, str) and x.startswith('https://') else np.nan)

    return df

def format_watered_column(data_frame):
    """Returns the last_watered column into a datetime object."""
    df = data_frame

    if "last_watered" not in df.columns:
        raise KeyError("last_watered column was not found!")
    

    df['last_watered'] = pd.to_datetime(df['last_watered'], errors='coerce')
    return df


    

