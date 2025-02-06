from unittest.mock import MagicMock
from upload import update_botanists
import pandas as pd


def test_create_temp_table_sql():
    "Tests that create_temp_table_sql is called"
    mock_dataframe = pd.DataFrame(
        {
            "botanist_name": ["bar", "ipsum"],
            "botanist_email": ["foo", "lorem"],
            "botanist_phone": ["baz", "dei"]
        }
    )

    mock_conn = MagicMock()
    mock_curr = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_curr

    update_botanists(mock_conn, mock_dataframe)
    mock_curr.execute.assert_any_call("""
        CREATE TABLE alpha.#transaction_botanists(
            name VARCHAR(30) NOT NULL,
            email VARCHAR(30) NOT NULL,
            phone_number VARCHAR(30) NOT NULL
        )
        ;
    """)


def test_merge_tables():
    "Tests that merge_tables is called"
    mock_dataframe = pd.DataFrame(
        {
            "botanist_name": ["bar", "ipsum"],
            "botanist_email": ["foo", "lorem"],
            "botanist_phone": ["baz", "dei"]
        }
    )

    mock_conn = MagicMock()
    mock_curr = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_curr

    update_botanists(mock_conn, mock_dataframe)
    mock_curr.execute.assert_any_call("""
        MERGE alpha.botanist as target
        USING alpha.#transaction_botanists as source
        ON target.phone_number = source.phone_number
        WHEN NOT MATCHED THEN
            INSERT (name, email, phone_number)
            VALUES (source.name, source.email, source.phone_number)
        ;
        """)


def test_drop_temp_table():
    "Tests that drop_temp_table_sql is called"
    mock_dataframe = pd.DataFrame(
        {
            "botanist_name": ["bar", "ipsum"],
            "botanist_email": ["foo", "lorem"],
            "botanist_phone": ["baz", "dei"]
        }
    )

    mock_conn = MagicMock()
    mock_curr = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_curr

    update_botanists(mock_conn, mock_dataframe)
    mock_curr.execute.assert_any_call(
        "DROP TABLE alpha.#transaction_botanists;")


def test_populate_temp_table():
    "Tests that populate_temp_table_sql is called"
    mock_dataframe = pd.DataFrame(
        {
            "botanist_name": ["bar", "ipsum"],
            "botanist_email": ["foo", "lorem"],
            "botanist_phone": ["baz", "dei"]
        }
    )

    mock_conn = MagicMock()
    mock_curr = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_curr

    update_botanists(mock_conn, mock_dataframe)
    mock_curr.executemany.assert_called_with("""
        INSERT INTO alpha.#transaction_botanists
            (name, email, phone_number)
        VALUES
            (%s, %s, %s)
        ;
    """, seq_of_parameters=[('bar', 'foo', 'baz'), ('ipsum', 'lorem', 'dei')])
