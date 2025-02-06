"""Script to present plant data on streamlit dashboard."""
from os import environ
from dotenv import load_dotenv
import streamlit as st
import plotly_express as px

from graphs import watering_pie_chart, temperature_pie_chart, last_watered_bar_chart, soil_moisture_line_graph, plant_temperature_line_graph, moisture_pie_chart, healthy_plant_count, at_risk_plant_count
st.set_page_config(layout="wide")


def get_connection():
    """Establishes streamlit connection to database."""
    return st.connection("sql", host=environ["DB_HOST"], port=environ["DB_PORT"],
                         database=environ["DB_NAME"], username=environ["DB_USER"],
                         password=environ["DB_PASSWORD"], dialect="mssql+pymssql")


def get_plant_id(conn) -> list:
    """Returns list of plant IDs from the database"""
    q = """
    SELECT DISTINCT(plant_id) FROM alpha.reading
    """
    plant_ids_df = conn.query(q)
    plant_ids = plant_ids_df["plant_id"].to_list()
    return plant_ids


def main():
    """Main script to run the streamlit dashboard."""
    load_dotenv()
    conn = get_connection()
    header = st.container()
    top_container = st.container()
    bottom_container = st.container()
    col1, col2, col3, col4 = st.columns([0.1, 0.3, 0.3, 0.3], border=True)
    bottom_col1, bottom_col2, bottom_col3 = st.columns(3, border=True)
    end_col1, end_col2, end_col3 = st.columns([3.25, 3, 3], gap="large")

    with header:
        st.title("**DASHBOARD**")

    with top_container:
        with col1:
            st.metric("Healthy Plants", healthy_plant_count(conn))
            st.metric("At Risk Plants", at_risk_plant_count(conn))
        with col2:
            st.plotly_chart(watering_pie_chart(conn))
        with col3:
            st.plotly_chart(temperature_pie_chart(conn))
        with col4:
            st.plotly_chart(moisture_pie_chart(conn))

    with end_col2:
        plant = st.radio("Plant ID", get_plant_id(
            conn), horizontal=True, index=0, key="1")
    with end_col3:
        plant_2 = st.radio("Plant ID", get_plant_id(
            conn), horizontal=True, index=0, key="2")

    with bottom_container:
        with bottom_col1:
            st.plotly_chart(last_watered_bar_chart(conn))
        with bottom_col2:
            st.plotly_chart(plant_temperature_line_graph(conn, plant))
        with bottom_col3:
            st.plotly_chart(soil_moisture_line_graph(conn, plant_2))


if __name__ == "__main__":
    main()
