"""Functions to upload relevant data from plant data batch 
to short term SQL Server Database"""
# pylint: disable=no-member

import os
import math
import pymssql
import pandas as pd

def sanitize(val):
    """
    Returns None if val is a float and NaN, otherwise returns val unchanged.
    """
    if isinstance(val, float) and math.isnan(val):
        return None
    return val

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
    # Ensure missing values are converted to None
    data = data.where(pd.notnull(data), None)

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
            # Use sanitize() on each value to ensure NaN becomes None
            plant_id = sanitize(plant.get("plant_id"))

            country = sanitize(plant.get("country"))
            if country is not None:
                country = country.strip().upper()

            region = sanitize(plant.get("region"))
            if region is not None:
                region = region.strip().title()

            latitude = sanitize(plant.get("latitude"))
            longitude = sanitize(plant.get("longitude"))
            image_license = sanitize(plant.get("image_license"))
            image_license_name = sanitize(plant.get("image_license_name"))
            image_original_url = sanitize(plant.get("image_original_url"))
            scientific_name = sanitize(plant.get("scientific_name"))
            plant_name = sanitize(plant.get("name"))

            # Round latitude and longitude to 5 decimal places
            if latitude is not None:
                latitude = round(latitude, 5)
            if longitude is not None:
                longitude = round(longitude, 5)

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
                (country,)
            )

            # Insert or update region
            cursor.execute(
                """
                MERGE alpha.region AS target
                USING (SELECT %s AS region_name, (SELECT country_id 
                FROM alpha.country WHERE country_code = %s) AS country_id) AS source
                ON target.region_name = source.region_name AND target.country_id = source.country_id
                WHEN NOT MATCHED THEN
                    INSERT (region_name, country_id)
                    VALUES (source.region_name, source.country_id);
                """,
                (region, country)
            )

            # Retrieve region_id explicitly
            cursor.execute(
                "SELECT region_id FROM alpha.region WHERE region_name = %s",
                (region,)
            )
            reg_row = cursor.fetchone()
            if not reg_row:
                raise ValueError(f"Failed to retrieve region_id for region '{region}'")
            region_id = reg_row[0]
            print(f"Region '{region}' has region_id: {region_id}")

            # Merge the location row using the retrieved region_id
            # and output the inserted location_id.
            cursor.execute(
                """
                MERGE alpha.location AS target
                USING (SELECT %s AS latitude, %s AS longitude, %s AS region_id) AS source
                ON target.latitude = source.latitude 
                   AND target.longitude = source.longitude 
                   AND target.region_id = source.region_id
                WHEN NOT MATCHED THEN
                    INSERT (latitude, longitude, region_id)
                    VALUES (source.latitude, source.longitude, source.region_id)
                OUTPUT inserted.location_id;
                """,
                (latitude, longitude, region_id)
            )
            loc_row = cursor.fetchone()
            if loc_row is not None:
                location_id = loc_row[0]
                print(f"New location inserted: location_id = {location_id}")
            else:
                # If no row was output, the location row already exists.
                cursor.execute(
                    """
                    SELECT location_id 
                    FROM alpha.location
                    WHERE ROUND(latitude, 5) = %s 
                      AND ROUND(longitude, 5) = %s 
                      AND region_id = %s
                    """,
                    (latitude, longitude, region_id)
                )
                loc_row = cursor.fetchone()
                if not loc_row:
                    raise ValueError(
                        f"Failed to retrieve location_id for plant_id {plant_id} using "
                        f"latitude={latitude}, longitude={longitude}, region_id={region_id}"
                    )
                location_id = loc_row[0]
                print(f"Existing location found: location_id = {location_id}")

            # Only upload license and image if all required values are present
            if image_license is not None and image_license_name is not None \
            and image_original_url is not None:
                cursor.execute(
                    """
                    MERGE alpha.license AS target
                    USING (SELECT %s AS license_id, %s AS license_name, %s AS license_url) AS source
                    ON target.license_id = source.license_id
                    WHEN NOT MATCHED THEN
                        INSERT (license_id, license_name, license_url)
                        VALUES (source.license_id, source.license_name, source.license_url);
                    """,
                    (image_license, image_license_name, image_original_url)
                )
                cursor.execute(
                    """
                    MERGE alpha.image AS target
                    USING (SELECT %s AS license_id, %s AS original_url) AS source
                    ON target.original_url = source.original_url
                    WHEN NOT MATCHED THEN
                        INSERT (license_id, original_url)
                        VALUES (source.license_id, source.original_url);
                    """,
                    (image_license, image_original_url)
                )
            else:
                image_original_url = None

            cursor.execute(
                """
                MERGE alpha.plant AS target
                USING (SELECT %s AS plant_id, %s AS location_id, %s AS scientific_name,
                              (SELECT image_id FROM alpha.image
                              WHERE original_url = %s) AS image_id,
                              %s AS common_name) AS source
                ON target.plant_id = source.plant_id
                WHEN NOT MATCHED THEN
                    INSERT (plant_id, location_id, scientific_name, image_id, common_name)
                    VALUES (source.plant_id, source.location_id,
                    source.scientific_name, source.image_id, source.common_name);
                """,
                (plant_id, location_id, scientific_name, image_original_url, plant_name)
            )
        conn.commit()
    print("Upload process completed.")



def update_botanists(conn: pymssql.Connection, batch_data: pd.DataFrame) -> None:
    """
    Updates the botanists table in the database.
    """
    # Ensure missing values are converted to None
    botanist_data = batch_data[[
        "botanist_name",
        "botanist_email",
        "botanist_phone"
    ]].where(pd.notnull(batch_data[[
        "botanist_name",
        "botanist_email",
        "botanist_phone"
    ]]), None)

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

    # Convert values in each row using sanitize
    upload_data = []
    for row in botanist_data.itertuples(index=False):
        upload_data.append((
            sanitize(row[0]),
            sanitize(row[1]),
            sanitize(row[2])
        ))

    with conn.cursor() as cursor:
        cursor.execute(create_temp_table_sql)
        cursor.executemany(populate_temp_table_sql, seq_of_parameters=upload_data)
        cursor.execute(merge_tables_sql)
        cursor.execute(drop_temp_table_sql)

    conn.commit()


def upload_reading_data(conn: pymssql.Connection, batch_data: pd.DataFrame) -> None:
    """
    Uploads readings onto the reading table on the database from the dataframe.
    """
    # Ensure missing values are converted to None
    batch_data = batch_data.where(pd.notnull(batch_data), None)

    cursor = conn.cursor()
    for _, row in batch_data.iterrows():
        # Retrieve plant_id based on the common name
        plant_name = sanitize(row.get('name'))
        cursor.execute("""
            SELECT plant_id
            FROM alpha.plant
            WHERE common_name = %s
        """, (plant_name,))
        plant_result = cursor.fetchone()
        if not plant_result:
            continue  # Skip if no matching plant is found
        plant_id = plant_result[0]

        # Retrieve botanist_id based on email
        botanist_email = sanitize(row.get('botanist_email'))
        cursor.execute("""
            SELECT botanist_id
            FROM alpha.botanist
            WHERE email = %s
        """, (botanist_email,))
        botanist_result = cursor.fetchone()
        if not botanist_result:
            continue
        botanist_id = botanist_result[0]

        cursor.execute("""
            INSERT INTO alpha.reading (plant_id, soil_moisture, temperature, at, botanist_id, last_watered)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            plant_id,
            sanitize(row.get('soil_moisture')),
            sanitize(row.get('temperature')),
            sanitize(row.get('recording_taken')),
            botanist_id,
            sanitize(row.get('last_watered'))
        ))
    conn.commit()
    cursor.close()
