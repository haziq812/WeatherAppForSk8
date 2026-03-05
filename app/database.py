"""
app/database.py — Database setup using Python's built-in sqlite3 module.

LEARNING NOTE: What is SQLite?
    SQLite is a database that lives in a single file on your computer.
    Unlike big databases (MySQL, PostgreSQL), you don't need to install
    or run any separate server — Python includes it out of the box!

    Perfect for learning and small-to-medium projects.

LEARNING NOTE: What is sqlite3?
    `sqlite3` is a Python "standard library" module.
    Standard library = comes with Python, no need to pip install.
    It lets you create databases, tables, and run SQL queries.

SQL BASICS (quick reference):
    CREATE TABLE  — create a new table
    INSERT INTO   — add a new row
    SELECT        — read/query rows
    UPDATE        — modify existing rows
    DELETE        — remove rows
    WHERE         — filter rows by condition
"""

import sqlite3  # Built-in Python module — no installation needed
import os       # Built-in module for file/folder paths

# ── Database File Path ────────────────────────────────────────────────────────
# __file__ is a special Python variable that holds THIS file's path.
# os.path.dirname gets the folder containing this file.
# os.path.join combines paths in an OS-safe way (handles / vs \ automatically).
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "weather_app.db")  # Creates weather_app.db in /app/


def get_connection() -> sqlite3.Connection:
    """
    Open and return a connection to the SQLite database.

    LEARNING NOTE:
        A "connection" is like opening a door to the database.
        You need to open it before you can read/write data,
        and close it when you're done.

        row_factory = sqlite3.Row makes each database row behave like a
        dictionary, so you can access columns by name:
            row["title"]  instead of  row[0]
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name, not just index
    return conn


def init_db():
    """
    Create the database tables if they don't already exist.

    LEARNING NOTE:
        "IF NOT EXISTS" means: only create the table if it's not there yet.
        This makes it safe to call init_db() every time the server starts
        without wiping your data.

        AUTOINCREMENT means SQLite automatically assigns a unique ID number
        to every new row you insert. You don't need to pick one yourself.
    """
    conn = get_connection()

    # LEARNING NOTE:
    #   conn.cursor() gives you a "cursor" — a tool to execute SQL commands.
    #   Think of it like a pen you use to write queries to the database.
    cursor = conn.cursor()

    # ── Create planner_events table ───────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS planner_events (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            date             TEXT    NOT NULL,   -- Format: YYYY-MM-DD (e.g. 2026-03-04)
            title            TEXT    NOT NULL,   -- Short event name
            description      TEXT,               -- Optional longer description
            activity_type    TEXT    DEFAULT 'general',  -- 'outdoor', 'indoor', 'travel', 'general'
            weather_dependent INTEGER DEFAULT 0, -- 1=yes (depends on weather), 0=no
            created_at       TEXT    DEFAULT (datetime('now'))  -- Auto-timestamp
        )
    """)

    # LEARNING NOTE:
    #   conn.commit() saves ("commits") your changes to the database.
    #   Without this, your changes are lost when the program ends.
    conn.commit()
    conn.close()  # Always close the connection when done
