"""Functions to upload relevant data from plant data batch 
to short term SQL Server Database"""
# pylint: disable=no-member

import os
import pymssql
import pandas as pd
from dotenv import load_dotenv
from transform import transform_and_clean_data


def get_connection():
    """
    Returns a connection object to connect to the database,
    using all the required environment variables.
    """
    conn = pymssql.connect(
        server=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"]
    )
    return conn


def insert_new_botanists(conn, df):
    """
    Inserts new botanists from a DataFrame into the database, avoiding duplicates.

    Parameters:
        conn: Active pymssql database connection.
        df (pd.DataFrame): DataFrame containing botanist details.

    Returns:
        None
    """
    cursor = conn.cursor()

    for _, row in df.iterrows():
        email = row["botanist_email"]
        name = row["botanist_name"]
        phone = row["botanist_phone"]

        # Check if botanist already exists
        cursor.execute(
            "SELECT botanist_id FROM alpha.botanist WHERE email = %s", (email,))
        existing_botanist = cursor.fetchone()

        if not existing_botanist:
            # Insert new botanist
            cursor.execute(
                "INSERT INTO alpha.botanist (email, name, phone_number) VALUES (%s, %s, %s)",
                (email, name, phone)
            )
            conn.commit()
            print(f"✅ Inserted new botanist: {name}")
        else:
            print(f"⏭️ Botanist {name} already exists, skipping.")

    cursor.close()


def insert_new_countries(conn, df):
    """
    Inserts unique country codes from a DataFrame into the database, avoiding duplicates.

    Parameters:
        conn: Active pymssql database connection.
        df (pd.DataFrame): DataFrame containing country details.

    Returns:
        None
    """
    cursor = conn.cursor()

    # Extract unique country codes from the DataFrame
    unique_countries = df[['country']].drop_duplicates()

    # Fetch existing country codes from the database
    cursor.execute("SELECT country_code FROM alpha.country")
    # Convert result to a set for fast lookup
    existing_countries = {row[0] for row in cursor.fetchall()}

    # Filter only new countries
    new_countries = unique_countries[~unique_countries['country'].isin(
        existing_countries)]

    # Insert only new countries (batch processing)
    if not new_countries.empty:
        values = [tuple(x) for x in new_countries.to_numpy()]
        cursor.executemany(
            "INSERT INTO alpha.country (country_code) VALUES (%s)", values)
        conn.commit()
        print(f"✅ Inserted {len(values)} new countries.")
    else:
        print("⏭️ No new countries to insert.")

    cursor.close()




if __name__ == '__main__':
    load_dotenv()

    connection = get_connection()

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
        "last_watered": "Thu, 06 Feb 2025 14:03:04 GMT",
        "name": "Epipremnum Aureum",
        "origin_location": [
            "-19.32556",
            "-41.25528",
            "Resplendor",
            "BR",
            "America/Sao_Paulo"
        ],
        "plant_id": 50,
        "recording_taken": "2025-02-07 09:56:13",
        "scientific_name": [
            "Epipremnum aureum"
        ],
        "soil_moisture": 30.6977577424976,
        "temperature": 13.231867909622
    }, {
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
        "recording_taken": "2025-02-07 09:57:00",
        "scientific_name": [
            "Begonia 'Art Hodes'"
        ],
        "soil_moisture": 30.795322622824,
        "temperature": 9.08651835249826
    }
    ]
    sample_data = transform_and_clean_data(sample)
    insert_new_botanists(connection, sample_data)
    insert_new_countries(connection, sample_data)
    # upload_new_plants_with_location(connection, sample_data)
    # upload_readings(connection, new_plant_data)

    connection.close()
