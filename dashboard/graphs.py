"""Module of graphs to be used in the dashboard."""

from dotenv import load_dotenv
import streamlit as st
import plotly_express as px


def watering_pie_chart(conn):
    """Returns a pie chart displaying plant watering data."""
    q = """
    WITH watered AS (
    SELECT CASE 
        WHEN DATEDIFF(DAY, last_watered, CURRENT_TIMESTAMP) <= 5 THEN 'Watered Recently'
        WHEN DATEDIFF(DAY, last_watered, CURRENT_TIMESTAMP) >=6 THEN 'Needs Watering'
        END AS status
    FROM alpha.reading)
    SELECT COUNT(*) AS count, status
    FROM watered
    GROUP BY status;
    """

    watering_status_df = conn.query(q)
    return px.pie(watering_status_df, values="count", names="status", title="Proportion of Plants Recently Watered")


def temperature_pie_chart(conn):
    """Returns a pie chart displaying plant temperature data."""
    q = """
    with temperatures AS (
        SELECT CASE
            WHEN temperature < 13 THEN 'Below Ideal Temperature'
            WHEN temperature > 32 THEN 'Above Ideal Temperature'
            WHEN temperature BETWEEN 13 AND 32 THEN 'Ideal Temperature' 
            END AS status
        FROM alpha.reading
    )
    SELECT COUNT(*) AS count, status
    FROM temperatures
    GROUP BY status;
    """

    temperature_status_df = conn.query(q)
    return px.pie(temperature_status_df, values="count", names="status", title="Proportion of Plants Within Ideal Temperature Range")


def moisture_pie_chart(conn):
    """Returns a pie chart displaying plant moisture data."""
    q = """
    with moisture AS (
        SELECT CASE
            WHEN soil_moisture < 18 THEN 'Below Ideal Soil Moisture'
            WHEN soil_moisture > 60 THEN 'Above Ideal Soil Moisture'
            WHEN soil_moisture BETWEEN 18 AND 60 THEN 'Ideal Soil Moisture' 
            END AS status
        FROM alpha.reading
    )
    SELECT COUNT(*) AS count, status
    FROM moisture
    GROUP BY status;
    """
    soil_moisture_df = conn.query(q)
    return px.pie(soil_moisture_df, values="count", names="status", title="Proportion of Plants With Ideal Soil Moisture")


def last_watered_bar_chart(conn):
    """Returns a bar chart displaying number of plants last watered within a timeframe."""
    q = """
        SELECT CASE 
            WHEN DATEDIFF(DAY, last_watered, current_timestamp) >=50 THEN '50+'
            ELSE CAST(DATEDIFF(DAY, last_watered, current_timestamp) AS varchar)
            END AS 'Days Since Watered',
            COUNT(plant_id) AS count
        FROM alpha.reading
        GROUP BY CASE 
            WHEN DATEDIFF(DAY, last_watered, current_timestamp) >=50 THEN '50+'
            ELSE CAST(DATEDIFF(DAY, last_watered, current_timestamp) AS varchar)
            END;

    """
    last_watered_df = conn.query(q)
    chart = px.bar(last_watered_df, x="Days Since Watered", y="count")
    chart.update_layout(xaxis={"type": "category"})
    return chart


def plant_temperature_line_graph(conn, plant):
    """Returns a line graph showing a plant's 24 hour temperature history."""

    q = """
    SELECT ROUND(AVG(r.temperature),2) as 'Average Temperature', DATE_BUCKET(MINUTE, 5, r.AT) as 'Time Recorded'
    FROM alpha.reading AS r
    JOIN alpha.plant AS p
    ON p.plant_id = r.plant_id
    WHERE p.plant_id = :plant_id
    AND r.AT >= DATEADD(DAY, -1, current_timestamp)
    GROUP BY r.AT
    """

    plant_temperature_df = conn.query(q, params={'plant_id': int(plant)})
    graph = px.line(plant_temperature_df, x="Time Recorded",
                    y="Average Temperature")
    graph.add_hline(y=13, line_dash="dash", line_color="red", label={
                    "text": "Min Temperature", "textposition": "end"})
    graph.add_hline(y=32, line_dash="dash", line_color="red")
    return graph


def soil_moisture_line_graph(conn, plant):
    """Returns a line graph showing a plant's 24 hour soil moisture history"""
    q = """
    SELECT ROUND(AVG(r.soil_moisture),2) as 'Average Soil Moisture', DATE_BUCKET(MINUTE, 5, r.AT) as 'Time Recorded'
    FROM alpha.reading AS r
    JOIN alpha.plant AS p
    ON p.plant_id = r.plant_id
    WHERE p.plant_id = :plant_id
    AND r.AT >= DATEADD(DAY, -1, current_timestamp)
    GROUP BY r.AT
    """
    plant_soil_moisture_df = conn.query(q, params={'plant_id': int(plant)})
    graph = px.line(plant_soil_moisture_df, x="Time Recorded",
                    y="Average Soil Moisture")
    graph.add_hline(y=18, line_dash="dash", line_color="red",
                    label={"text": "Min Moisture", "textposition": "end"})
    graph.add_hline(y=60, line_dash="dash", line_color="red")
    return graph


def healthy_plant_count(conn):
    """Returns number of healthy plants counted."""
    q = """
    SELECT COUNT(*) as count FROM alpha.reading
    WHERE temperature BETWEEN 13 AND 32
    AND soil_moisture BETWEEN 18 AND 60
    AND DATEDIFF(DAY, last_watered, CURRENT_TIMESTAMP) BETWEEN 3 AND 5;
    """

    healthy_plants = conn.query(q)
    return healthy_plants["count"]


def at_risk_plant_count(conn):
    """Returns number of plants at risk."""
    q = """
    SELECT COUNT(*) as count FROM alpha.reading
    WHERE temperature NOT BETWEEN 13 AND 32
    AND soil_moisture NOT BETWEEN 18 AND 60
    AND DATEDIFF(DAY, last_watered, CURRENT_TIMESTAMP) NOT BETWEEN 3 AND 5;
    """

    at_risk_plants = conn.query(q)
    return at_risk_plants["count"]


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()
    st.plotly_chart(watering_pie_chart(conn))
    st.plotly_chart(temperature_pie_chart(conn))
    st.plotly_chart(moisture_pie_chart(conn))
    st.plotly_chart(last_watered_bar_chart(conn))
    st.plotly_chart(plant_temperature_line_graph(conn))
    st.plotly_chart(soil_moisture_line_graph(conn))
