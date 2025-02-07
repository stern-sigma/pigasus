"""This script will transform the data into a usable format for the DB."""
import re
import pandas as pd
import numpy as np

def convert_to_dataframe(raw_data:list[dict]):
    """Creates dataframe from data."""
    if not isinstance(raw_data, list):
        raise TypeError("Wrong format!")
    
    return pd.DataFrame(raw_data)


def parse_botanist_data(df: pd.DataFrame) -> pd.DataFrame:
    """Returns botanist data into separate columns, ensuring NaN for missing values without dropping rows."""

    if "botanist" not in df.columns:
        df["botanist"] = np.nan
    df["botanist_email"] = df["botanist"].apply(
        lambda x: x.get("email") if isinstance(x, dict) else np.nan)
    df["botanist_name"] = df["botanist"].apply(
        lambda x: x.get("name") if isinstance(x, dict) else np.nan)
    df["botanist_phone"] = df["botanist"].apply(
        lambda x: x.get("phone") if isinstance(x, dict) else np.nan)

    df = df.drop(columns=["botanist"])
    return df


def parse_origin_location(df: pd.DataFrame) -> pd.DataFrame:
    """Parses the origin_location column into separate latitude, longitude, region, and country columns,
    while excluding the timezone."""

    if "origin_location" not in df.columns:
        df["origin_location"] = np.nan

    df["latitude"] = df["origin_location"].apply(
        lambda x: float(x[0]) if isinstance(x, list) and len(x) > 0 else np.nan
    )
    df["longitude"] = df["origin_location"].apply(
        lambda x: float(x[1]) if isinstance(x, list) and len(x) > 1 else np.nan
    )
    df["region"] = df["origin_location"].apply(
        lambda x: x[2] if isinstance(x, list) and len(x) > 2 else np.nan
    )
    df["country"] = df["origin_location"].apply(
        lambda x: x[3] if isinstance(x, list) and len(x) > 3 else np.nan
    )

    df = df.drop(columns=["origin_location"])
    return df

def clean_scientific_name(df:pd.DataFrame) -> pd.DataFrame:
    """Returns the scientific_name column cleaned - transformed into a string and ensured that it is consistent."""
    if "scientific_name" not in df.columns:
        df['scientific_name'] = np.nan

    df['scientific_name'] = df['scientific_name'].apply(
        lambda x: ', '.join([part.capitalize() for part in x]) if isinstance(x, list) else
        (x.capitalize() if isinstance(x, str) else np.nan)
    )

    df["scientific_name"] = df["scientific_name"].apply(
        lambda x: x.title() if isinstance(x, str) else np.nan)

    return df


def clean_image_data(df:pd.DataFrame) -> pd.DataFrame:
    """Returns the images column into separate columns, creating them even if 'images' does not exist."""

    if "images" not in df.columns:
        df["images"] = None
    df['image_license'] = df['images'].apply(lambda x: x.get(
        'license') if isinstance(x, dict) and x.get('license') is not None else np.nan)
    df['image_license_name'] = df['images'].apply(lambda x: x.get(
        'license_name') if isinstance(x, dict) and x.get('license_name') is not None else np.nan)
    df['image_license_url'] = df['images'].apply(lambda x: x.get(
        'license_url') if isinstance(x, dict) and x.get('license_url') is not None else np.nan)
    df['image_original_url'] = df['images'].apply(lambda x: x.get(
        'original_url') if isinstance(x, dict) and x.get('original_url') is not None else np.nan)
    df = df.drop(columns=['images'])
    df['image_original_url'] = df['image_original_url'].apply(
        lambda x: x if isinstance(x, str) and (x.startswith('http://') or x.startswith('https://')) else np.nan)
    return df




def format_watered_column(df:pd.DataFrame) -> pd.DataFrame:
    """Converts the last_watered column to a datetime object with second precision."""
    if "last_watered" not in df.columns:
        df["last_watered"] = np.nan
    else:
        df["last_watered"] = pd.to_datetime(
            df["last_watered"], errors="coerce")
        df["last_watered"] = df["last_watered"].dt.strftime(
            '%Y-%m-%d %H:%M:%S')
        df["last_watered"] = pd.to_datetime(df["last_watered"])
        df["last_watered"] = df["last_watered"].where(
            df["last_watered"].notna(), np.nan)
    return df

def format_recording_taken(df:pd.DataFrame) -> pd.DataFrame:
    """Converts recording_taken to a datetime object or NaN if invalid or missing."""
    if "recording_taken" not in df.columns:
        df["recording_taken"] = np.nan
    df['recording_taken'] = pd.to_datetime(
        df['recording_taken'], errors='coerce')
    df['recording_taken'] = df['recording_taken'].apply(
        lambda x: np.nan if pd.isna(x) else x
    )
    return df


def capitalise_plant_name(df:pd.DataFrame) -> pd.DataFrame:
    """Returns each word in the plant name capitalised.
    Removes non-alphabetic characters (except spaces), and handles leading/trailing spaces."""

    if "name" not in df.columns:
        df["name"] = np.nan
    else:
        df["name"] = df["name"].apply(
            lambda x: re.sub(r"[^a-zA-Z\s]", "", x.strip()).title() if isinstance(x, str) else np.nan)

    return df


def validate_soil_moisture(df:pd.DataFrame) -> pd.DataFrame:
    """Returns the soil_moisture column. Checks it exists, makes negative values absolute, and handles invalid or missing values."""
    if "soil_moisture" not in df.columns:
        df["soil_moisture"] = np.nan
    df["soil_moisture"] = df["soil_moisture"].apply(
        lambda x: abs(x) if isinstance(x, (int, float)) and x >= 0 else np.nan
    )
    return df


def process_temperature_column(df:pd.DataFrame) -> pd.DataFrame:
    """Returns the processed temperature column.
        Removes invalid data types.
        If column does not exist, still create it for consistency.
    """
    if 'temperature' not in df.columns:
        df['temperature'] = np.nan
    df['temperature'] = df['temperature'].apply(
        lambda x: x if isinstance(x, (float, int)) and not pd.isna(x) else np.nan)

    return df


def transform_and_clean_data(raw_data: list[dict]):
    """Returns dataframe that has been cleaned correctly."""
    df = convert_to_dataframe(raw_data)
    df = clean_image_data(df)
    df = clean_scientific_name(df)
    df = format_recording_taken(df)
    df = parse_botanist_data(df)
    df = format_watered_column(df)
    df = parse_origin_location(df)
    df = capitalise_plant_name(df)
    df = process_temperature_column(df)
    return df


sample = [{
    "botanist": {
        "email": "carl.linnaeus@lnhm.co.uk",
        "name": "Carl Linnaeus",
        "phone": "(146)994-1635x35992"
    },
    "images": {
        "license": 45,
        "license_name": "Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)",
        "license_url": "https://creativecommons.org/licenses/by-sa/3.0/deed.en",
        "medium_url": "https://perenual.com/storage/species_image/2773_epipremnum_aureum/medium/2560px-Epipremnum_aureum_31082012.jpg",
        "original_url": "https://perenual.com/storage/species_image/2773_epipremnum_aureum/og/2560px-Epipremnum_aureum_31082012.jpg",
        "regular_url": "https://perenual.com/storage/species_image/2773_epipremnum_aureum/regular/2560px-Epipremnum_aureum_31082012.jpg",
        "small_url": "https://perenual.com/storage/species_image/2773_epipremnum_aureum/small/2560px-Epipremnum_aureum_31082012.jpg",
        "thumbnail": "https://perenual.com/storage/species_image/2773_epipremnum_aureum/thumbnail/2560px-Epipremnum_aureum_31082012.jpg"
    },
    "last_watered": "Wed, 05 Feb 2025 14:03:04 GMT",
    "name": "Epipremnum Aureum",
    "origin_location": [
        "-19.32556",
        "-41.25528",
        "Resplendor",
        "BR",
        "America/Sao_Paulo"
    ],
    "plant_id": 50,
    "recording_taken": "2025-02-06 09:16:49",
    "scientific_name": [
        "Epipremnum aureum"
    ],
    "soil_moisture": 32.985887107454,
    "temperature": 13.1473300457849
},
    {
    "botanist": {
        "email": "gertrude.jekyll@lnhm.co.uk",
        "name": "Gertrude Jekyll",
        "phone": "001-481-273-3691x127"
    },
    "images": None,
    "last_watered": "Thu, 06 Feb 2025 14:04:23 GMT",
    "name": "Begonia",
    "origin_location": [
        "33.95015",
        "-118.03917",
        "South Whittier",
        "US",
        "America/Los_Angeles"
    ],
    "plant_id": 45,
    "recording_taken": "2025-02-06 20:44:13",
    "scientific_name": [
        "Begonia 'Art Hodes'"
    ],
    "soil_moisture": 76.7981688336557,
    "temperature": 9.08020763101348
}]

print(transform_and_clean_data(sample).sample().T)
