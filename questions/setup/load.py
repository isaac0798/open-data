"""
Load StatsBomb open-data JSON into a local SQLite database.

Tables (defined in setup/schema.sql):
  competitions  - one row per competition/season   (data/competitions.json)
  matches       - one row per match                 (data/matches/<comp>/<season>.json)
  lineups       - one row per player per match      (data/lineups/<match_id>.json)
  events        - one row per on-ball event         (data/events/<match_id>.json)

Run with:
  docker compose run --rm py python setup/load.py

Each load_* function turns the JSON into tuples in `rows`, then inserts them.
Each tuple has one value per column, in the same order as the INSERT's column list.
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
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def create_tables(conn):
    # schema.sql drops and recreates every table, so the script can be rerun safely
    conn.executescript(SCHEMA_PATH.read_text())


def load_competitions(conn):
    rows = []
    for c in read_json(DATA_DIR / "competitions.json"):
        rows.append((
            c["competition_id"],
            c["season_id"],
            c["country_name"],
            c["competition_name"],
            c["competition_gender"],
            c["competition_youth"],          # True/False is stored as 1/0
            c["competition_international"],
            c["season_name"],
            c["match_updated"],
            c["match_updated_360"],          # None (NULL) when there's no 360 data
            c["match_available_360"],
            c["match_available"],
        ))

    conn.executemany("""
        INSERT INTO competitions (
            competition_id, season_id, country_name, competition_name,
            competition_gender, competition_youth, competition_international,
            season_name, match_updated, match_updated_360,
            match_available_360, match_available
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    print(f"competitions: {len(rows)} rows")


def load_matches(conn):
    rows = []
    # data/matches/<competition_id>/<season_id>.json
    for path in sorted((DATA_DIR / "matches").glob("*/*.json")):
        for m in read_json(path):
            # .get() returns None instead of crashing when a key is missing.
            # `or {}` turns that None into an empty dict, so the .get("name")
            # after it gives None (stored as NULL) rather than an error.
            stadium = m.get("stadium") or {}
            referee = m.get("referee") or {}
            stage = m.get("competition_stage") or {}

            rows.append((
                m["match_id"],
                m["competition"]["competition_id"],
                m["season"]["season_id"],
                m["match_date"],
                m["kick_off"],
                m.get("match_week"),
                stage.get("name"),
                m["home_team"]["home_team_id"],
                m["home_team"]["home_team_name"],
                m["away_team"]["away_team_id"],
                m["away_team"]["away_team_name"],
                m["home_score"],
                m["away_score"],
                stadium.get("name"),
                referee.get("name"),
            ))

    conn.executemany("""
        INSERT INTO matches (
            match_id, competition_id, season_id, match_date, kick_off,
            match_week, competition_stage,
            home_team_id, home_team_name, away_team_id, away_team_name,
            home_score, away_score, stadium_name, referee_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    print(f"matches: {len(rows)} rows")


def load_lineups(conn):
    rows = []
    # data/lineups/<match_id>.json - one file per match, holding both teams
    for path in sorted((DATA_DIR / "lineups").glob("*.json")):
        match_id = int(path.stem)  # file name is the match id
        for team in read_json(path):
            for p in team["lineup"]:
                country = p.get("country") or {}

                rows.append((
                    match_id,
                    team["team_id"],
                    team["team_name"],
                    p["player_id"],
                    p["player_name"],
                    p.get("player_nickname"),
                    p.get("jersey_number"),
                    country.get("name"),
                ))

    conn.executemany("""
        INSERT INTO lineups (
            match_id, team_id, team_name, player_id, player_name,
            player_nickname, jersey_number, country_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    print(f"lineups: {len(rows)} rows")


def load_events(conn, max_matches):
    paths = sorted((DATA_DIR / "events").glob("*.json"))
    if max_matches >= 0:
        paths = paths[:max_matches]

    total = 0
    for i, path in enumerate(paths, start=1):
        match_id = int(path.stem)  # file name is the match id
        rows = []
        for e in read_json(path):
            # Some events have no player/position/location, and only passes have
            # a "pass" section, only shots a "shot" section. Default each to an
            # empty dict/list so the lookups below give None instead of crashing.
            player = e.get("player") or {}
            position = e.get("position") or {}
            x, y = e.get("location") or [None, None]

            pass_ = e.get("pass") or {}  # trailing _ because `pass` is a Python keyword
            pass_end_x, pass_end_y = pass_.get("end_location") or [None, None]
            pass_recipient = pass_.get("recipient") or {}
            pass_outcome = pass_.get("outcome") or {}  # missing = completed pass

            shot = e.get("shot") or {}
            shot_outcome = shot.get("outcome") or {}

            rows.append((
                e["id"],
                match_id,
                e["index"],
                e["period"],
                e["timestamp"],
                e["minute"],
                e["second"],
                e["type"]["name"],
                e["possession"],
                e["possession_team"]["name"],
                e["play_pattern"]["name"],
                e["team"]["id"],
                e["team"]["name"],
                player.get("id"),
                player.get("name"),
                position.get("name"),
                x,
                y,
                e.get("duration"),
                e.get("under_pressure"),
                pass_recipient.get("name"),
                pass_.get("length"),
                pass_end_x,
                pass_end_y,
                pass_outcome.get("name"),
                shot_outcome.get("name"),
                shot.get("statsbomb_xg"),
            ))

        conn.executemany("""
            INSERT INTO events (
                event_id, match_id, idx, period, timestamp, minute, second,
                type, possession, possession_team, play_pattern,
                team_id, team_name, player_id, player_name, position,
                location_x, location_y, duration, under_pressure,
                pass_recipient, pass_length, pass_end_x, pass_end_y, pass_outcome,
                shot_outcome, shot_xg
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        conn.commit()
        total += len(rows)
        print(f"events: match {i}/{len(paths)} ({total} rows so far)")


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
    load_lineups(conn)
    conn.commit()
    if args.event_matches != 0:
        load_events(conn, args.event_matches)

    conn.close()
    print(f"Done -> {DB_PATH}")


if __name__ == "__main__":
    main()
