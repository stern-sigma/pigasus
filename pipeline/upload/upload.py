import pymssql
import pandas as pd


def update_botanists(conn: pymssql.Connection, batch_data: pd.DataFrame
                     ) -> None:
    """Updates the botanists table in the database"""
    cur = conn.cursor()
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
    print(upload_data)

    with conn.cursor() as cur:
        cur.execute(create_temp_table_sql)
        cur.executemany(populate_temp_table_sql, seq_of_parameters=upload_data)
        cur.execute(merge_tables_sql)
        cur.execute(drop_temp_table_sql)
    conn.commit()
