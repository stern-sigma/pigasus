"""Functions used to alert botanist on 3 successive abnormal readings
Will generate a basic email with all of the require info."""

import os
import datetime
import pymssql
from dotenv import load_dotenv


NORMAL_TEMPERATURE_MIN = 13.0
NORMAL_TEMPERATURE_MAX = 32.0
NORMAL_MOISTURE_MIN = 18.0
NORMAL_MOISTURE_MAX = 60.0


def get_connection():
    """
    Returns a connection object to connect to the SQL Server database,
    using environment variables for configuration.
    """
    return pymssql.connect(
        server=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"]
    )


def is_abnormal(reading):
    """
    Returns True if either the temperature or the soil moisture in the given
    reading is outside the normal range.
    """
    temp = reading["temperature"]
    moisture = reading["soil_moisture"]
    abnormal_temp = temp < NORMAL_TEMPERATURE_MIN or temp > NORMAL_TEMPERATURE_MAX
    abnormal_moisture = moisture < NORMAL_MOISTURE_MIN or moisture > NORMAL_MOISTURE_MAX
    return abnormal_temp or abnormal_moisture


def fetch_readings(conn):
    """
    Fetch last 3 readings from the database along with the botanist email.
    The results are ordered by plant_id and descending timestamp so that for each
    plant the most recent readings come first.
    """
    query = """
    WITH LastThree AS (
        SELECT 
            r.plant_id, 
            r.temperature, 
            r.soil_moisture, 
            r.at, 
            b.email,
            ROW_NUMBER() OVER (PARTITION BY r.plant_id ORDER BY r.at DESC) AS rn
        FROM alpha.reading r
        JOIN alpha.botanist b ON r.botanist_id = b.botanist_id
    )
    SELECT plant_id, temperature, soil_moisture, at, email
    FROM LastThree
    WHERE rn <= 3
    ORDER BY plant_id, at DESC;
    """
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return rows

def generate_email(plant_id, readings):
    """
    Generate an HTML email alert for the given plant, including its plant ID and
    details from the last three readings.
    """
    email_html = "<html><body>"
    email_html += f"<h2>Alert for Plant ID: {plant_id}</h2>"
    email_html += "<p>The last three readings are outside of the normal range:</p>"
    email_html += "<ul>"
    for reading in readings:
        if isinstance(reading["at"], datetime.datetime):
            timestamp = reading["at"].strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = str(reading["at"])
        email_html += (
            f"<li>Time: {timestamp} | Temperature: {reading['temperature']}°C | "
            f"Soil Moisture: {reading['soil_moisture']}</li>"
        )
    email_html += "</ul>"
    email_html += "</body></html>"
    return email_html

def lambda_handler(event, context): # pylint: disable=W0613
    """
    AWS Lambda handler.
    This function connects to the database, checks the last three readings
    for each plant, and if all three are abnormal (i.e. outside the normal range
    for temperature or soil moisture), it creates an email alert.
    """
    load_dotenv()
    try:
        conn = get_connection()
    except Exception as e:
        print("Database connection failed:", e)
        raise

    try:
        all_readings = fetch_readings(conn)
        plants = {}
        for row in all_readings:
            plant_id = row["plant_id"]
            if plant_id not in plants:
                plants[plant_id] = []
            plants[plant_id].append(row)

        alerts = []
        for plant_id, readings in plants.items():
            if len(readings) < 3:
                continue

            last_three = readings[:3]

            if all(is_abnormal(reading) for reading in last_three):
                email_address = last_three[0]["email"]
                email_content = generate_email(plant_id, last_three)
                alerts.append({
                    "email": email_content,
                    "email_address": email_address
                })

        return alerts

    finally:
        conn.close()

if __name__ == '__main__':
    result = lambda_handler({}, {})
    import json
    print(json.dumps(result, indent=2))
