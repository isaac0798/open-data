-- Tables for the StatsBomb open data.
-- load.py runs this whole file before loading, so every run starts from empty tables.
--
-- The FOREIGN KEYs document how tables join. SQLite doesn't enforce them by default,
-- which matters here: 274 lineup/event files are for matches that aren't in any
-- data/matches file, so those rows have no matching row in `matches`.

DROP TABLE IF EXISTS competitions;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS lineups;
DROP TABLE IF EXISTS events;


-- One row per competition + season (data/competitions.json)
-- A competition has many seasons and a season id is shared across competitions,
-- so only the pair is unique.
CREATE TABLE competitions (
    competition_id            INTEGER NOT NULL,
    season_id                 INTEGER NOT NULL,
    country_name              TEXT,
    competition_name          TEXT,
    competition_gender        TEXT,
    competition_youth         INTEGER,  -- 0/1 (SQLite has no boolean type)
    competition_international INTEGER,  -- 0/1
    season_name               TEXT,
    match_updated             TEXT,
    match_updated_360         TEXT,
    match_available_360       TEXT,
    match_available           TEXT,
    PRIMARY KEY (competition_id, season_id)
);


-- One row per match (data/matches/<competition_id>/<season_id>.json)
CREATE TABLE matches (
    match_id           INTEGER PRIMARY KEY,
    competition_id     INTEGER NOT NULL,
    season_id          INTEGER NOT NULL,
    match_date         TEXT,
    kick_off           TEXT,
    match_week         INTEGER,
    competition_stage  TEXT,
    home_team_id       INTEGER,
    home_team_name     TEXT,
    away_team_id       INTEGER,
    away_team_name     TEXT,
    home_score         INTEGER,
    away_score         INTEGER,
    stadium_name       TEXT,     -- missing for a few matches
    referee_name       TEXT,     -- missing for some matches
    FOREIGN KEY (competition_id, season_id) REFERENCES competitions (competition_id, season_id)
);


-- One row per player per match (data/lineups/<match_id>.json)
-- Includes subs who never came on (they have no positions).
CREATE TABLE lineups (
    match_id         INTEGER NOT NULL,
    team_id          INTEGER NOT NULL,
    team_name        TEXT,
    player_id        INTEGER NOT NULL,
    player_name      TEXT,
    player_nickname  TEXT,
    jersey_number    INTEGER,
    country_name     TEXT,
    PRIMARY KEY (match_id, player_id),
    FOREIGN KEY (match_id) REFERENCES matches (match_id)
);


-- One row per event: pass, shot, carry, pressure, ... (data/events/<match_id>.json)
-- Most columns are only filled in for some event types, the rest are NULL.
CREATE TABLE events (
    event_id         TEXT PRIMARY KEY,  -- a UUID string
    match_id         INTEGER NOT NULL,
    idx              INTEGER,  -- order within the match ("index" is a reserved word in SQL)
    period           INTEGER,
    timestamp        TEXT,
    minute           INTEGER,
    second           INTEGER,
    type             TEXT,     -- e.g. 'Pass', 'Shot', 'Carry'
    possession       INTEGER,
    possession_team  TEXT,
    play_pattern     TEXT,
    team_id          INTEGER,
    team_name        TEXT,
    player_id        INTEGER,  -- NULL for events with no player
    player_name      TEXT,
    position         TEXT,
    location_x       REAL,     -- pitch is 120 x 80
    location_y       REAL,
    duration         REAL,
    under_pressure   INTEGER,  -- 1 or NULL

    -- Pass events only
    pass_recipient   TEXT,
    pass_length      REAL,
    pass_end_x       REAL,
    pass_end_y       REAL,
    pass_outcome     TEXT,     -- NULL means the pass was completed

    -- Shot events only
    shot_outcome     TEXT,     -- e.g. 'Goal', 'Saved', 'Off T'
    shot_xg          REAL,     -- StatsBomb expected goals

    FOREIGN KEY (match_id) REFERENCES matches (match_id)
);


-- Indexes make the common filters and joins fast
CREATE INDEX idx_matches_competition ON matches (competition_id, season_id);
CREATE INDEX idx_lineups_player      ON lineups (player_id);
CREATE INDEX idx_events_match        ON events (match_id);
CREATE INDEX idx_events_type         ON events (type);
CREATE INDEX idx_events_player       ON events (player_id);
