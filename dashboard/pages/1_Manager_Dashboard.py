"""Script to present plant data on streamlit dashboard."""
# pylint: disable=invalid-name, line-too-long

from os import environ
from dotenv import load_dotenv
import streamlit as st

from manager_graphs import botanist_reading_bar_chart, botanist_pie_chart, count_days_since_watered, botanist_plant_reading_count


def get_connection() -> st.connection:
    """Establishes streamlit connection to database."""
    return st.connection("sql", host=environ["DB_HOST"], port=environ["DB_PORT"],
                         database=environ["DB_NAME"], username=environ["DB_USER"],
                         password=environ["DB_PASSWORD"], dialect="mssql+pymssql")


def botanist_count(conn: st.connection) -> int:
    """Returns number of botanists."""
    q = """
        SELECT COUNT(DISTINCT(botanist_id)) as count
        FROM alpha.botanist
    """
    botanist_df = conn.query(q)
    return botanist_df["count"]


def botanist_with_most_readings(conn: st.connection) -> str:
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


def list_botanist_names(conn: st.connection) -> list[str]:
    """Returns a list of botanist names."""
    q = """
    SELECT name FROM alpha.botanist
    """
    names_df = conn.query(q)
    names = names_df["name"].to_list()
    return names


def list_plant_names(conn: st.connection) -> list[str]:
    """Returns list of plant IDs from the database"""
    q = """
    SELECT DISTINCT(scientific_name) FROM alpha.plant
    """
    plant_name_df = conn.query(q)
    plant_names = plant_name_df["scientific_name"].to_list()
    return plant_names


def main():
    """Runs the streamlit dashboard"""
    st.set_page_config(layout="wide")
    load_dotenv()
    conn = get_connection()
    header = st.container()
    top_container = st.container()
    bottom_container = st.container()
    col1, col2, col3 = st.columns([0.2, 0.4, 0.4], border=True)
    bcol1, bcol2, bcol3 = st.columns([0.2, 0.4, 0.4], border=True)

    with header:
        st.title("**MANAGER DASHBOARD**")
    with top_container:
        with col1:
            st.metric("Number of Botanists", botanist_count(conn))
            st.metric("Botanist With Most Readings",
                      botanist_with_most_readings(conn))
        with col2:
            st.plotly_chart(botanist_reading_bar_chart(conn))
        with col3:
            chart_placeholder = st.empty()
            plant_name = st.multiselect("Plant Names", list_plant_names(
                conn), default=list_plant_names(conn))
            if plant_name == []:
                plant_name = list_plant_names(conn)
            chart_placeholder.plotly_chart(
                botanist_plant_reading_count(conn, plant_name))
        with bottom_container:
            with bcol1:
                botanists = st.radio("Botanists", list_botanist_names(conn))
            with bcol2:
                st.plotly_chart(botanist_pie_chart(conn, botanists))
            with bcol3:
                st.plotly_chart(count_days_since_watered(conn, botanists))


if __name__ == "__main__":
    main()
