"""
app/planner/service.py — CRUD operations for the weekly planner.

LEARNING NOTE: What is CRUD?
    CRUD stands for the four basic database operations:
        C — Create   (INSERT a new row)
        R — Read     (SELECT existing rows)
        U — Update   (UPDATE an existing row)
        D — Delete   (DELETE a row)

    Almost every data-driven app uses these four operations.
    Once you understand CRUD, you understand the backbone of any app.

LEARNING NOTE: SQL Fundamentals used here
    INSERT INTO table (col1, col2) VALUES (?, ?)
        → Add a new row. The ? are "placeholders" for safe input.

    SELECT * FROM table WHERE id = ?
        → Get rows matching a condition. * means "all columns".

    UPDATE table SET col1 = ? WHERE id = ?
        → Change a specific row's data.

    DELETE FROM table WHERE id = ?
        → Remove a row permanently.

LEARNING NOTE: Why use ? placeholders?
    NEVER use Python string formatting to build SQL queries:
        BAD:  f"INSERT INTO table VALUES ('{user_input}')"
        GOOD: cursor.execute("INSERT INTO table VALUES (?)", (user_input,))

    Using ? prevents "SQL injection" attacks — a common security vulnerability
    where malicious input can destroy or steal your database.
"""

import sqlite3
from typing import List, Optional
from app.database import get_connection
from app.models import PlannerEventCreate, PlannerEventUpdate, PlannerEventResponse


def _row_to_event(row: sqlite3.Row) -> PlannerEventResponse:
    """
    Convert a raw database row into a PlannerEventResponse model.

    LEARNING NOTE:
        Helper functions that are only used internally are often named
        with a leading underscore (_) by convention. It signals to other
        developers: "this is private, not meant to be called from outside."

    LEARNING NOTE:
        sqlite3.Row works like both a tuple and a dict.
        row["id"] accesses the "id" column by name.
        bool(row["weather_dependent"]) converts 0/1 integer to True/False.

    Args:
        row: A sqlite3.Row object from a SELECT query.

    Returns:
        PlannerEventResponse populated with the row's data.
    """
    return PlannerEventResponse(
        id=row["id"],
        date=row["date"],
        title=row["title"],
        description=row["description"],
        activity_type=row["activity_type"],
        weather_dependent=bool(row["weather_dependent"]),
        created_at=row["created_at"],
    )


# ── CREATE ────────────────────────────────────────────────────────────────────

def create_event(event: PlannerEventCreate) -> PlannerEventResponse:
    """
    Insert a new planner event into the database.

    LEARNING NOTE: cursor.lastrowid
        After an INSERT, SQLite gives the new row an auto-generated ID.
        cursor.lastrowid retrieves that ID so we can fetch the full record.

    Args:
        event: Validated PlannerEventCreate data model from the request.

    Returns:
        The newly created PlannerEventResponse (including its new id).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO planner_events (date, title, description, activity_type, weather_dependent)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            event.date,
            event.title,
            event.description,
            event.activity_type,
            1 if event.weather_dependent else 0,  # SQLite stores bool as 0/1
        ),
    )
    conn.commit()

    new_id = cursor.lastrowid  # Get the auto-generated ID
    conn.close()

    # Fetch and return the full record (so we include created_at, etc.)
    return get_event_by_id(new_id)


# ── READ ──────────────────────────────────────────────────────────────────────

def get_event_by_id(event_id: int) -> Optional[PlannerEventResponse]:
    """
    Fetch a single planner event by its ID.

    LEARNING NOTE: Optional[T]
        The return type Optional[PlannerEventResponse] means this function
        can return either a PlannerEventResponse OR None (if not found).
        Always handle the None case in the caller!

    Args:
        event_id: The integer ID of the event.

    Returns:
        PlannerEventResponse if found, None if the ID doesn't exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM planner_events WHERE id = ?",
        (event_id,),  # LEARNING NOTE: comma after event_id makes it a tuple
    )
    row = cursor.fetchone()  # fetchone() returns one row or None
    conn.close()

    if row is None:
        return None

    return _row_to_event(row)


def get_all_events() -> List[PlannerEventResponse]:
    """
    Fetch all planner events, ordered by date then title.

    LEARNING NOTE: ORDER BY
        "ORDER BY date, title" sorts results: first by date (ascending),
        then alphabetically by title within the same date.

    Returns:
        A list of all PlannerEventResponse objects (may be empty).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM planner_events ORDER BY date, title")
    rows = cursor.fetchall()  # fetchall() returns a list of all rows
    conn.close()

    # LEARNING NOTE: List comprehension
    #   [expression for item in iterable]
    #   is a compact way to build a list.
    #   [_row_to_event(row) for row in rows]
    #   means: "for each row in rows, call _row_to_event(row) and collect results"
    return [_row_to_event(row) for row in rows]


def get_events_by_date_range(start_date: str, end_date: str) -> List[PlannerEventResponse]:
    """
    Fetch events within a specific date range (inclusive).

    LEARNING NOTE: BETWEEN in SQL
        "WHERE date BETWEEN ? AND ?" selects rows where date is
        >= start_date AND <= end_date.

    Args:
        start_date: Start of range in YYYY-MM-DD format.
        end_date: End of range in YYYY-MM-DD format.

    Returns:
        List of PlannerEventResponse objects within the date range.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM planner_events
        WHERE date BETWEEN ? AND ?
        ORDER BY date, title
        """,
        (start_date, end_date),
    )
    rows = cursor.fetchall()
    conn.close()

    return [_row_to_event(row) for row in rows]


# ── UPDATE ────────────────────────────────────────────────────────────────────

def update_event(event_id: int, updates: PlannerEventUpdate) -> Optional[PlannerEventResponse]:
    """
    Update specific fields of an existing planner event.

    LEARNING NOTE: Partial updates (PATCH-style)
        We only want to update fields the user actually sent.
        model.model_dump(exclude_none=True) returns a dict of only the
        fields that are NOT None — ignoring ones not sent by the client.

        Then we dynamically build a SQL SET clause from those fields.

    LEARNING NOTE: Dynamic SQL building
        We build the SET clause programmatically:
            fields = {"title": "New title", "activity_type": "outdoor"}
            → SET title = ?, activity_type = ?
            → values = ["New title", "outdoor", event_id]

        We use ', '.join(...) to combine the list into a comma-separated string.

    Args:
        event_id: The ID of the event to update.
        updates: PlannerEventUpdate model with the fields to change.

    Returns:
        Updated PlannerEventResponse, or None if event_id doesn't exist.
    """
    # Get only the fields that were actually provided (not None)
    fields_to_update = updates.model_dump(exclude_none=True)

    if not fields_to_update:
        # Nothing to update — just return the current record
        return get_event_by_id(event_id)

    # Convert bool weather_dependent → int for SQLite
    if "weather_dependent" in fields_to_update:
        fields_to_update["weather_dependent"] = 1 if fields_to_update["weather_dependent"] else 0

    # Build "col1 = ?, col2 = ?" string dynamically
    set_clause = ", ".join(f"{col} = ?" for col in fields_to_update.keys())

    # Values list: the field values + event_id for the WHERE clause
    values = list(fields_to_update.values()) + [event_id]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"UPDATE planner_events SET {set_clause} WHERE id = ?",
        values,
    )
    conn.commit()

    rows_affected = cursor.rowcount  # How many rows were changed
    conn.close()

    if rows_affected == 0:
        return None  # Event ID not found

    return get_event_by_id(event_id)


# ── DELETE ────────────────────────────────────────────────────────────────────

def delete_event(event_id: int) -> bool:
    """
    Delete a planner event by ID.

    LEARNING NOTE: cursor.rowcount
        After DELETE, cursor.rowcount tells you how many rows were deleted.
        If it's 0, the event didn't exist and nothing was deleted.
        If it's 1, the event was found and deleted successfully.

    Args:
        event_id: The ID of the event to delete.

    Returns:
        True if the event was found and deleted, False if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM planner_events WHERE id = ?", (event_id,))
    conn.commit()

    deleted = cursor.rowcount > 0  # True if at least one row was deleted
    conn.close()

    return deleted
