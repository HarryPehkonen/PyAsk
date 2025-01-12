from langchain_core.tools import tool
import sqlite3
import json

databaseFilename = "database.db"

@tool
def execute_sqlite_query(query: str) -> str:
    """Execute an SQLite query."""
    print(f"Executing query: {query}")
    with sqlite3.connect(databaseFilename) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            results = cursor.fetchall()

            if results:

                # this operation seems to have rows to return
                column_names = [description[0] for description in cursor.description]
                result_obj = [dict(zip(column_names, row)) for row in results]

                print(f"SQL query results: {json.dumps(result_obj)}")
                return json.dumps(result_obj)
            else:

                # nothing to return
                conn.commit()
                return "SQL operation completed without exception or anything to return."
        except sqlite3.Error as e:
            return str(e)
        except Exception as e:
            return str(e)
