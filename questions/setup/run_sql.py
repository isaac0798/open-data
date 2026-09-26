"""
Run a .sql file against the database and print the result as a table.

    python setup/run_sql.py 01-matches-per-competition/answer.sql
    python setup/run_sql.py 01-matches-per-competition/answer.sql --watch   # rerun on save
"""

import argparse
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "statsbomb.db"


def run(sql_path):
    sql = sql_path.read_text()
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.execute(sql)
        headers = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    finally:
        conn.close()

    # Make each column as wide as its longest value
    widths = [max(len(str(v)) for v in [h, *(r[i] for r in rows)]) for i, h in enumerate(headers)]
    print("  ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print("  ".join(str(v).ljust(w) for v, w in zip(row, widths)))
    print(f"\n({len(rows)} rows)")


def watch(sql_path):
    last_modified = None
    print(f"Watching {sql_path} - save the file to rerun, Ctrl+C to stop\n")
    while True:
        modified = sql_path.stat().st_mtime
        if modified != last_modified:
            last_modified = modified
            print("\033[2J\033[H", end="")  # clear the screen
            print(f"== {sql_path} ({time.strftime('%H:%M:%S')}) ==\n")
            try:
                run(sql_path)
            except sqlite3.Error as e:
                # Keep watching so you can fix the mistake and save again
                print(f"SQL error: {e}")
        time.sleep(0.5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sql_file", type=Path)
    parser.add_argument("--watch", action="store_true", help="rerun every time the file is saved")
    args = parser.parse_args()

    if args.watch:
        try:
            watch(args.sql_file)
        except KeyboardInterrupt:
            pass
    else:
        run(args.sql_file)


if __name__ == "__main__":
    main()
