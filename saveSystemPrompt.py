#!/usr/bin/env python

import sqlite3
import sys
from datetime import datetime
import re

def table_exists(db_path, table_name):
    """
    Check if a table exists in the SQLite database.
    
    Args:
        database_path (str): Path to the SQLite database file
        table_name (str): Name of the table to check
    
    Returns:
        bool: True if table exists, False otherwise
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        print(f"table_exists???  {e}", file=sys.stderr)
        return False

def create_database(db_path):
    """Create the SQLite database and table structure."""

    cmds = [
        "CREATE TABLE ask_config (id INTEGER PRIMARY KEY "
        "AUTOINCREMENT, key TEXT, value TEXT, description TEXT, "
        "date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",

        "INSERT INTO ask_config (key, value, description) VALUES"
        "('system_prompts', 'system_prompts', 'System prompts for "
        "different AI personalities');",

        "INSERT INTO ask_config (key, value, description) VALUES "
        "('table_metadata', 'table_metadata', 'Describes the purpose of "
        "each table');",

        "INSERT INTO ask_config (key, value, description) VALUES "
        "('column_metadata', 'column_metadata', 'Describes the purpose of "
        "each column in each table');",

        "CREATE TABLE IF NOT EXISTS system_prompts (id INTEGER PRIMARY "
        "KEY AUTOINCREMENT, ai_code_name TEXT, prompt TEXT, date_created "
        "TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",

        "CREATE TABLE IF NOT EXISTS table_metadata (table_name TEXT "
        "PRIMARY KEY, description TEXT, date_created TIMESTAMP DEFAULT "
        "CURRENT_TIMESTAMP);",

        "INSERT INTO table_metadata (table_name, description) "
        "VALUES('system_prompts','Stores system prompts for various AI "
        "personalities.  Only the newest one is used.');",

        "INSERT INTO table_metadata (table_name, description) "
        "VALUES('table_metadata','Describes the purpose of each "
        "table');",

        "INSERT INTO table_metadata (table_name, description) "
        "VALUES('column_metadata','Lists all columns, their names, the "
        "table where they exist, the data type, as well as their purpose "
        "or description');",

        "INSERT INTO table_metadata (table_name, description) "
        "VALUES('sqlite_sequence','System generated');",

        "INSERT INTO table_metadata (table_name, description) "
        "VALUES('sqlite_stat1','System generated');",

        "CREATE TABLE IF NOT EXISTS column_metadata (id INTEGER PRIMARY "
        "KEY AUTOINCREMENT, table_name TEXT, column_name TEXT, data_type "
        "TEXT, description TEXT, UNIQUE (table_name, column_name));",

        "INSERT INTO column_metadata (table_name, column_name, "
        "data_type, description) "
        "VALUES('ask_config','id','INTEGER','Unique identifier for the configuration record');",

        "INSERT INTO column_metadata (table_name, column_name, "
        "data_type, description) "
        "VALUES('table_metadata','table_name','TEXT','Table name');",

        "INSERT INTO column_metadata (table_name, column_name, "
        "data_type, description) "
        "VALUES('table_metadata','description','TEXT','Description of the "
        "table');",

        "INSERT INTO column_metadata (table_name, column_name, "
        "data_type, description) "
        "VALUES('table_metadata','date_created','TIMESTAMP','Self-explanatory');",

        "INSERT INTO column_metadata (table_name, column_name, "
        "data_type, description) "
        "VALUES('system_prompts','ai_code_name','TEXT','The code name of "
        "the AI');",

        "INSERT INTO column_metadata (table_name, column_name, "
        "data_type, description) "
        "VALUES('system_prompts','prompt','TEXT','The prompt text for the "
        "AI');",

        "INSERT INTO column_metadata (table_name, column_name, "
        "data_type, description) "
        "VALUES('system_prompts','date_created','TIMESTAMP','Timestamp "
        "when the prompt was created');",

        "INSERT INTO column_metadata (table_name, column_name, "
        "data_type, description) "
        "VALUES('column_metadata','id','INTEGER','Self-explanatory');",

        "INSERT INTO column_metadata (table_name, column_name, "
        "data_type, description) "
        "VALUES('column_metadata','table_name','TEXT','Name of the "
        "table');",

        "INSERT INTO column_metadata (table_name, column_name, "
        "data_type, description) "
        "VALUES('column_metadata','column_name','TEXT','Name of the "
        "column');",

        "INSERT INTO column_metadata (table_name, column_name, "
        "data_type, description) "
        "VALUES('column_metadata','data_type','TEXT','Data type of the "
        "column');",

        "INSERT INTO column_metadata (table_name, column_name, "
        "data_type, description) "
        "VALUES('column_metadata','description','TEXT','Description of "
        "the column');",

    ]

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            for sql in cmds:
                cursor.execute(sql)
            conn.commit()
    except sqlite3.Error as e:
        print(f"create_database???  {e}", file=sys.stderr)
        return False
    return True

def load_system_prompt(filename):
    try:
        # Read the markdown file
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def save_system_prompt(db_path, ai_code_name, system_prompt):

    sql = """
        INSERT INTO system_prompts (
            ai_code_name,
            prompt
        ) VALUES (
            ?, ?
        )
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                sql,
                (ai_code_name, system_prompt)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"save_system_prompt:  {e}", file=sys.stderr)
        return False
    return True

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <ai_code_name> <db_path> <input_file>")
        sys.exit(1)
    
    ai_code_name = sys.argv[1]
    db_path = sys.argv[2]
    input_file = sys.argv[3]

    if not table_exists(db_path, "ask_config"):
        create_database(db_path)

    system_prompt = load_system_prompt(input_file)    
    if not save_system_prompt(db_path, ai_code_name, system_prompt):
        print("It didn't work", file=sys.stderr)
        sys.exit(1)
