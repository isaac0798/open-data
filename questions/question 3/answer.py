"""
Question 3: Which competition seasons have the most matches?

Run with:
    docker compose run --rm py python "question 3/answer.py"
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
    """Print the 5 competition seasons with the most matches."""
    cur = conn.cursor()
    
    res = cur.execute("""
        SELECT competition_name, season_name, competition_name + season_name AS comp_season 
        from competitions
        INNER JOIN matches
            ON competitions.competition_id = matches.competition_id
            AND competitions.season_id = matches.season_id
            ORDER BY comp_season DESC
            LIMIT 5
    """)
    
    for result in res.fetchall():
        print(result)
    pass


if __name__ == "__main__":
    conn = get_connection()
    answer(conn)
    conn.close()
