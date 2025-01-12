from langchain_core.tools import tool
import sqlite3
import json

databaseFilename = "database.db"

@tool
def update_database_metadata() -> str:
    """Updates the metadata tables with information about new tables and
    columns.  Returns a list of tables and columns in the database that
    don't have a description."""

    # Connect to the SQLite database
    conn = sqlite3.connect(databaseFilename)
    cursor = conn.cursor()

    result = []

    try:
        print("Updating table_metadata")
        # Bulk-update table_metadata
        cursor.execute('''
            INSERT OR IGNORE INTO table_metadata (table_name)
            SELECT name
            FROM sqlite_master
            WHERE type='table'
        ''')

        print("Updating column_metadata")
        # Bulk-update column_metadata
        cursor.execute('''
            INSERT OR IGNORE INTO column_metadata (table_name, column_name, data_type, description)
            SELECT
                m.name AS table_name,
                p.name AS column_name,
                p.type AS data_type,
                NULL AS description
            FROM sqlite_master AS m
            JOIN pragma_table_info((m.name)) AS p
            WHERE m.type='table'
        ''')

        # Commit the changes
        conn.commit()

        # Get the tables and columns that don't have a description.
        # Ignore any system tables.
        print("Getting tables and columns without a description")
        cursor.execute('''
            SELECT
                table_name,
                column_name,
                data_type,
                description
            FROM column_metadata
            WHERE
                description IS NULL
                AND table_name NOT IN ('sqlite_sequence', 'sqlite_stat1')
        ''')
        hits = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        results = [dict(zip(column_names, row)) for row in hits]


    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the database connection
        conn.close()

    return json.dumps(results)
