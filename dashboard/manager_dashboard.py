"""Script to present plant data on streamlit dashboard."""
from os import environ
from dotenv import load_dotenv
import streamlit as st
import plotly_express as px

from manager_graphs import botanist_reading_bar_chart, botanist_pie_chart, count_days_since_watered, botanist_plant_reading_count


def get_connection():
    """Establishes streamlit connection to database."""
    return st.connection("sql", host=environ["DB_HOST"], port=environ["DB_PORT"],
                         database=environ["DB_NAME"], username=environ["DB_USER"],
                         password=environ["DB_PASSWORD"], dialect="mssql+pymssql")


def botanist_count(conn):
    """Returns number of botanists."""
    q = """
        SELECT COUNT(DISTINCT(botanist_id)) as count
        FROM alpha.botanist
    """
    botanist_df = conn.query(q)
    return botanist_df["count"]


def botanist_with_most_readings(conn):
    """Returns botanist name with most readings."""
    q = """
        SELECT TOP 1 count(reading_id) as count, b.name as name
        FROM alpha.reading as r
        JOIN alpha.botanist as b
        on b.botanist_id = r.botanist_id
        GROUP BY b.name
        ORDER BY count DESC
    """
    top_botanist_df = conn.query(q)
    return top_botanist_df["name"].iloc[0]


def list_botanist_names(conn):
    """Returns a list of botanist names."""
    q = """
    SELECT name FROM alpha.botanist
    """
    names_df = conn.query(q)
    names = names_df["name"].to_list()
    return names


def main():
    """Runs the streamlit dashboard"""
    st.set_page_config(layout="wide")
    load_dotenv()
    conn = get_connection()
    header = st.container()
    top_container = st.container()
    col1, col2, col3 = st.columns([0.2, 0.4, 0.4], border=True)

    with top_container:
        with col1:
            st.metric("Number of Botanists", botanist_count(conn))
            st.metric("Botanist With Most Readings",
                      botanist_with_most_readings(conn))
        with col2:
            st.plotly_chart(botanist_reading_bar_chart(conn))
            st.plotly_chart(botanist_plant_reading_count(conn))


if __name__ == "__main__":
    main()
