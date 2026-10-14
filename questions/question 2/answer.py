"""
Question 2: What was the biggest win?

Run with:
    docker compose run --rm py python "question 2/answer.py"
"""

import sqlite3
from pathlib import Path

# questions/db/statsbomb.db - worked out from this file's location so it runs in Docker or locally
DB_PATH = Path(__file__).resolve().parent.parent / "db" / "statsbomb.db"


def get_connection():
    """Connect to the database and return the connection."""
    con = sqlite3.connect(DB_PATH)
    
    return con


def answer(conn):
    """Print the 5 matches with the largest goal difference."""
    cur = conn.cursor()
    
    top_5_matches = cur.execute("""SELECT
        match_date, home_team_name, away_team_name, abs(home_score - away_score), home_score, away_score
        FROM matches ORDER BY abs(home_score - away_score) DESC LIMIT 5
    """)
    for match in top_5_matches:
        print(f'{match[0]} {match[1]} {match[4]} - {match[5]} {match[2]}')
    pass


if __name__ == "__main__":
    conn = get_connection()
    answer(conn)
    conn.close()
