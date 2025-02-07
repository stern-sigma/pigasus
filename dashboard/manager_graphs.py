"""Module of graphs to be used in the manager's dashboard."""

from dotenv import load_dotenv
from os import environ
import streamlit as st
import plotly_express as px


def botanist_reading_bar_chart(conn):
    """Returns a bar chart displaying number of readings taken per botanist."""
    q = """
    SELECT COUNT(*) as count, b.name
    FROM alpha.reading as r
    JOIN alpha.botanist as b
    ON b.botanist_id = r.botanist_id
    GROUP BY b.name
    """
    bar_chart_df = conn.query(q)
    bar_chart = px.bar(bar_chart_df, x="name", y="count")
    return bar_chart


def botanist_pie_chart(conn, botanist):
    """Returns a pie chart showing proportion of healthy readings taken per botanist."""
    q = """
    WITH healthy_readings AS(
    SELECT CASE 
        WHEN temperature BETWEEN 13 AND 32 
        AND soil_moisture BETWEEN 18 AND 60
        AND temperature BETWEEN 13 AND 32 THEN 'healthy'
        ELSE 'unhealthy'
    END AS 'status', b.name
    FROM alpha.reading AS r
    JOIN alpha.botanist AS b
    ON b.botanist_id = r.botanist_id
    )
    SELECT count(status) as count, status FROM healthy_readings
    WHERE name = :botanist_name
    GROUP BY status
    """
    pie_chart_df = conn.query(q, params={"botanist_name": botanist})
    pie_chart = px.pie(pie_chart_df, values="count", names="status",
                       title=f"Proportion of Healthy Readings Taken By {botanist}")
    return pie_chart


def count_days_since_watered(conn, botanist):
    """Returns bar chart showing count of days since last watered per botanist."""
    q = """
    SELECT COUNT(DATEDIFF(DAY, last_watered, CURRENT_TIMESTAMP)) AS count, 
    CAST(DATEDIFF(DAY, last_watered, CURRENT_TIMESTAMP) AS VARCHAR) AS 'Days Since Last Watered'
    FROM alpha.reading AS r
    JOIN alpha.botanist AS b
    ON b.botanist_id = r.botanist_id
    WHERE name = :botanist_name
    GROUP BY DATEDIFF(DAY, last_watered, CURRENT_TIMESTAMP)
    """
    bar_chart_df = conn.query(q, params={"botanist_name": botanist})
    bar_chart = px.bar(bar_chart_df, y="count",
                       x="Days Since Last Watered", title=f"Count Number of Days Since Last Watered for {botanist}")
    return bar_chart


def botanist_plant_reading_count(conn):
    """Returns a bar chart showing how many readings a botanist has for a certain plant."""

    q = """
    SELECT COUNT(reading_id) AS count, b.name, p.scientific_name FROM alpha.reading AS r
    JOIN alpha.botanist AS b
    ON b.botanist_id = r.botanist_id
    JOIN alpha.plant AS p
    ON p.plant_id = r.plant_id
    GROUP BY b.name, p.scientific_name
    """

    botanist_plant_reading_df = conn.query(q)
    bar_chart = px.bar(botanist_plant_reading_df,
                       x="scientific_name", y="count", color="name", barmode="group")
    return bar_chart
