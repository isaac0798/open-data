"""
Question 8: Are there any competition seasons with no matches recorded?

Run with:
    docker compose run --rm py python "question 8/answer.py"
"""

import sqlite3
from pathlib import Path

# questions/db/statsbomb.db - worked out from this file's location so it runs in Docker or locally
DB_PATH = Path(__file__).resolve().parent.parent / "db" / "statsbomb.db"


def get_connection():
    """Connect to the database and return the connection."""
    # TODO
    pass


def answer(conn):
    """Print any competition seasons with zero matches, via a LEFT JOIN."""
    # TODO
    pass


if __name__ == "__main__":
    conn = get_connection()
    answer(conn)
    conn.close()
