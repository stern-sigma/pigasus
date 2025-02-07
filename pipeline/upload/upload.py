"""Functions to upload relevant data from plant data batch 
to short term SQL Server Database"""
# pylint: disable=no-member

import os
import pymssql
import pandas as pd
from dotenv import load_dotenv


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


def get_existing_plant_ids(conn: pymssql.Connection, plant_ids: list) -> set:
    """
    Returns a set of plant_ids that already exist in the database.
    """
    if not plant_ids:
        return set()

    placeholders = ", ".join(["%s"] * len(plant_ids))
    query = f"SELECT plant_id FROM alpha.plant WHERE plant_id IN ({placeholders})"

    with conn.cursor() as cursor:
        cursor.execute(query, tuple(plant_ids))
        rows = cursor.fetchall()

    return {row[0] for row in rows}


def upload_new_plants_with_location(conn: pymssql.Connection, data: pd.DataFrame) -> None:
    """
    Uploads new plant data, including location, images, and plant details, into the database.
    Handles relationships and dependencies between tables.
    """
    plant_ids_in_data = data["plant_id"].tolist()
    existing_ids = get_existing_plant_ids(conn, plant_ids_in_data)
    print(f"Existing plant IDs in DB: {existing_ids}")

    new_plants_data = data[~data["plant_id"].isin(existing_ids)]
    if new_plants_data.empty:
        print("No new plants to upload.")
        return

    print(f"New plant IDs to upload: {new_plants_data['plant_id'].tolist()}")

    with conn.cursor() as cursor:
        for _, plant in new_plants_data.iterrows():
            # Insert or update country
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

            # Insert or update region
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

            # Insert or update location
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

            # Insert or update license
            cursor.execute(
                """
                MERGE alpha.license AS target
                USING (SELECT %s AS license_id, %s AS license_name, %s AS license_url) AS source
                ON target.license_id = source.license_id
                WHEN NOT MATCHED THEN
                    INSERT (license_id, license_name, license_url)
                    VALUES (source.license_id, source.license_name, source.license_url);
                """,
                (plant["image_license"], plant["license_name"], plant["image_original_url"])
            )

            # Insert or update image
            cursor.execute(
                """
                MERGE alpha.image AS target
                USING (SELECT %s AS license_id, %s AS original_url) AS source
                ON target.original_url = source.original_url
                WHEN NOT MATCHED THEN
                    INSERT (license_id, original_url)
                    VALUES (source.license_id, source.original_url);
                """,
                (plant["image_license"], plant["image_original_url"])
            )

            # Insert or update plant
            cursor.execute(
                """
                MERGE alpha.plant AS target
                USING (SELECT %s AS plant_id, (
                        SELECT location_id FROM alpha.location
                        WHERE latitude = %s AND longitude = %s
                    ) AS location_id, %s AS scientific_name, (
                        SELECT image_id FROM alpha.image
                        WHERE original_url = %s
                    ) AS image_id, %s AS common_name) AS source
                ON target.plant_id = source.plant_id
                WHEN NOT MATCHED THEN
                    INSERT (plant_id, location_id, scientific_name, image_id, common_name)
                    VALUES (source.plant_id, source.location_id, source.scientific_name, source.image_id, source.common_name);
                """,
                (
                    plant["plant_id"],
                    plant["latitude"], plant["longitude"],
                    plant["scientific_name"],
                    plant["image_original_url"],
                    plant["name"]
                )
            )
        conn.commit()
    print("Upload process completed.")



def update_botanists(conn: pymssql.Connection, batch_data: pd.DataFrame) -> None:
    """
    Updates the botanists table in the database.
    """
    create_temp_table_sql = """
        CREATE TABLE alpha.#transaction_botanists(
            name VARCHAR(30) NOT NULL,
            email VARCHAR(30) NOT NULL,
            phone_number VARCHAR(30) NOT NULL
        )
        ;
    """
    populate_temp_table_sql = """
        INSERT INTO alpha.#transaction_botanists
            (name, email, phone_number)
        VALUES
            (%s, %s, %s)
        ;
    """
    merge_tables_sql = """
        MERGE alpha.botanist as target
        USING alpha.#transaction_botanists as source
        ON target.phone_number = source.phone_number
        WHEN NOT MATCHED THEN
            INSERT (name, email, phone_number)
            VALUES (source.name, source.email, source.phone_number)
        ;
        """
    drop_temp_table_sql = "DROP TABLE alpha.#transaction_botanists;"

    botanist_data = batch_data[[
        "botanist_name",
        "botanist_email",
        "botanist_phone"]]
    upload_data = [tuple(x) for x in botanist_data.itertuples(index=False)]

    with conn.cursor() as cursor:
        cursor.execute(create_temp_table_sql)
        cursor.executemany(populate_temp_table_sql, seq_of_parameters=upload_data)
        cursor.execute(merge_tables_sql)
        cursor.execute(drop_temp_table_sql)

    conn.commit()
