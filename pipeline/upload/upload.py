"""Functions to take transformed data and load relevant information
into the short-term database"""

import os
import pymssql
import pandas as pd
from dotenv import load_dotenv

def get_connection():
    """
    Returns a connection object to connect to the database,
    using all the required environment variables.
    """
    conn = pymssql.connect(  # pylint: disable=no-member
        server=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"]
    )
    return conn

def get_existing_plant_ids(cursor, plant_ids: list) -> set:
    """
    Returns a set of plant_ids that already exist in the database.
    """
    if not plant_ids:
        return set()

    placeholders = ", ".join(["%s"] * len(plant_ids))
    query = f"SELECT plant_id FROM alpha.plant WHERE plant_id IN ({placeholders})"
    cursor.execute(query, tuple(plant_ids))
    rows = cursor.fetchall()
    return {row[0] for row in rows}

def upload_new_plants_with_location(data: pd.DataFrame) -> None:
    """
    Uploads all new plants along with their country, region, location, and plant details
    using SQL Server's MERGE statement.
    """
    conn = get_connection()
    cursor = conn.cursor()

    plant_ids_in_data = data["plant_id"].tolist()

    existing_ids = get_existing_plant_ids(cursor, plant_ids_in_data)
    print(f"Existing plant IDs in DB: {existing_ids}")

    new_plants_data = data[~data["plant_id"].isin(existing_ids)]
    if new_plants_data.empty:
        print("No new plants to upload.")
        conn.close()
        return
    print(f"New plant IDs to upload: {new_plants_data['plant_id'].tolist()}")

    for _, plant in new_plants_data.iterrows():
        cursor.execute(
            """
            MERGE alpha.country AS target
            USING (SELECT %s AS country_code) AS source
            ON target.country_code = source.country_code
            WHEN NOT MATCHED THEN
                INSERT (country_code)
                VALUES (source.country_code);
            """,
            (plant["country"],)
        )

        cursor.execute(
            """
            MERGE alpha.region AS target
            USING (SELECT %s AS region_name, (
                    SELECT country_id FROM alpha.country WHERE country_code = %s
                ) AS country_id) AS source
            ON target.region_name = source.region_name AND target.country_id = source.country_id
            WHEN NOT MATCHED THEN
                INSERT (region_name, country_id)
                VALUES (source.region_name, source.country_id);
            """,
            (plant["region"], plant["country"])
        )

        cursor.execute(
            """
            MERGE alpha.location AS target
            USING (SELECT %s AS latitude, %s AS longitude, (
                    SELECT region_id FROM alpha.region WHERE region_name = %s
                ) AS region_id) AS source
            ON target.latitude = source.latitude AND target.longitude = source.longitude 
            AND target.region_id = source.region_id
            WHEN NOT MATCHED THEN
                INSERT (latitude, longitude, region_id)
                VALUES (source.latitude, source.longitude, source.region_id);
            """,
            (plant["latitude"], plant["longitude"], plant["region"])
        )

        cursor.execute(
            """
            MERGE alpha.plant AS target
            USING (SELECT %s AS plant_id, (
                    SELECT location_id FROM alpha.location
                    WHERE latitude = %s AND longitude = %s
                ) AS location_id, %s AS scientific_name,
                %s AS image_id, %s AS common_name) AS source
            ON target.plant_id = source.plant_id
            WHEN NOT MATCHED THEN
                INSERT (plant_id, location_id, scientific_name, image_id, common_name)
                VALUES (source.plant_id, source.location_id,
                source.scientific_name, source.image_id, source.common_name);
            """,
            (
                plant["plant_id"],
                plant["latitude"], plant["longitude"],
                plant["scientific_name"],
                plant["image_id"],
                plant["name"]
            )
        )
    conn.commit()
    conn.close()
    print("Upload process completed.")

if __name__ == '__main__':
    load_dotenv()

    new_plant_data = pd.DataFrame([{
        "botanist_email": "eliza.andrews@lnhm.co.uk",
        "botanist_name": "Eliza Andrews",
        "botanist_phone": "(846)669-6651x75948",
        "region": "Mars Outpost Alpha",
        "country": "MC",
        "scientific_name": "Extra Terrestrialus",
        "image_license": 451,
        "license_name": "CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "image_original_url": "https://perenual.com/storage/image/alien_flower.jpg",
        "last_watered": pd.to_datetime("2025-02-05 13:23:01"),
        "recording_taken": pd.to_datetime("2025-02-06 11:45:30"),
        "plant_id": 9999,
        "soil_moisture": 99.99,
        "temperature": -42.42,
        "name": "Martian Death Bloom",
        "latitude": 0.0,      
        "longitude": 0.0,     
        "image_id": None      
    }])

    print(new_plant_data)
    upload_new_plants_with_location(new_plant_data)
