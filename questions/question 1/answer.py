"""
Question 1: How big is the database?

Run with:
    docker compose run --rm py python "question 1/answer.py"
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "statsbomb.db"

def get_connection():
    con = sqlite3.connect(DB_PATH)

    return con


def answer(conn):
    """Print the total matches, number of competitions, and number of La Liga matches."""
    
    cur = conn.cursor()
    total_matches = cur.execute("SELECT COUNT(*) FROM matches")
    print(total_matches.fetchall())
    
    total_competitions = cur.execute("SELECT COUNT(DISTINCT competition_name) FROM competitions")
    print(total_competitions.fetchall())
    la_liga_competition_id = cur.execute("""SELECT competition_id FROM competitions WHERE competition_name = "La Liga" """)
    total_laliga_matches = cur.execute(f'SELECT COUNT(*) FROM matches WHERE competition_id = {la_liga_competition_id.fetchone()[0]}')
    print(total_laliga_matches.fetchall())

    pass


if __name__ == "__main__":
    conn = get_connection()
    answer(conn)
    conn.close()
