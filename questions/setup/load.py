"""
Load StatsBomb open-data JSON into a local SQLite database.

Tables to build:
  competitions  - one row per competition/season   (data/competitions.json)
  matches       - one row per match                 (data/matches/<comp>/<season>.json)
  events        - one row per on-ball event         (data/events/<match_id>.json)

Run with:
  docker compose run --rm py python setup/load.py
"""

import argparse
import json
import os
import sqlite3
from pathlib import Path

# Paths are worked out from where this file lives, so it runs locally or in Docker
QUESTIONS_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("DATA_DIR", QUESTIONS_DIR.parent / "data"))  # Docker sets DATA_DIR=/data
DB_PATH = QUESTIONS_DIR / "db" / "statsbomb.db"


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def create_tables(conn):
    # TODO: DROP and CREATE the tables so the script can be rerun safely
    competition_sql = """
        DROP TABLE IF EXISTS COMPETITION
        CREATE TABLE COMPETITION (
            competition_id int PRIMARY KEY,
            season_id int NOT NULL UNIQUE,
            country_name varchar(255),
            competition_name varchar(255),
            competition_gender varchar(255),
            competition_youth int,
            competition_international int,
            season_name varchar(255),
            match_updated varchar(255),
            match_updated_360 varchar(255),
            match_available_360 varchar(255),
            match_avaliable varchar(255)
        )
    """
    conn.executescript(competition_sql)
    pass


def load_competitions(conn):
    rows = []
    for c in read_json(DATA_DIR / "competitions.json"):
        print(c)
        pass

    print(f"competitions: {len(rows)} rows")


def load_matches(conn):
        #todo
    print(f"todo")


def load_events(conn, max_matches):
    #todo
    print(f"todo")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-matches", type=int, default=10,
                        help="how many matches' events to load (0 = none, -1 = all)")
    args = parser.parse_args()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    create_tables(conn)
    load_competitions(conn)
    load_matches(conn)
    conn.commit()
    if args.event_matches != 0:
        load_events(conn, args.event_matches)

    conn.close()
    print(f"Done -> {DB_PATH}")


if __name__ == "__main__":
    main()
