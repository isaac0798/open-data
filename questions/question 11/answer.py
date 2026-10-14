"""
Question 11: Which competition has produced the most goals overall?

Run with:
    docker compose run --rm py python "question 11/answer.py"
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
    """Print the top 5 competitions by total goals scored."""
    # TODO
    pass


if __name__ == "__main__":
    conn = get_connection()
    answer(conn)
    conn.close()
