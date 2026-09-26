# Questions

Learning Python + SQL by answering questions about the StatsBomb open data in `data/`.

Everything for this lives in the `questions/` folder. **All commands below are run from `questions/`:**

```bash
cd questions
```

The data ends up in a single SQLite file, `db/statsbomb.db`. You can run the
scripts either **locally** with the Python already on your Mac, or inside a
small **Docker** container. Both use the same files and the same database.

```
data/                         # StatsBomb JSON (competitions, matches, events, ...)
questions/
├── docker-compose.yml        # Docker setup
├── db/statsbomb.db           # created by setup/load.py (gitignored)
├── setup/
│   ├── Dockerfile
│   ├── requirements.txt      # extra Python packages
│   ├── load.py               # JSON -> SQLite
│   └── run_sql.py            # run a .sql file and print a table
```

The database has three tables:

| table          | one row per                 |
|----------------|-----------------------------|
| `competitions` | competition + season        |
| `matches`      | match                       |
| `events`       | on-ball event (pass, shot…) |

---

## Running the scripts (Docker)

Python runs inside a small Docker container, so you don't need to manage
Python installs on your Mac.

1. Install Docker Desktop from https://www.docker.com/products/docker-desktop/ and open it.
   Wait until the whale icon in the menu bar says it's running.
2. From `questions/`, build the container (once, and again after changing `setup/requirements.txt`):

   ```bash
   docker compose build
   ```

3. Load the data and run an answer. The results print straight to your terminal:

   ```bash
   docker compose run --rm py python setup/load.py
   docker compose run --rm py python setup/run_sql.py 01-matches-per-competition/answer.sql
   docker compose run --rm py python setup/run_sql.py 01-matches-per-competition/answer.sql --watch
   ```

4. Or open a shell inside the container so you can just type `python ...`:

   ```bash
   docker compose run --rm py bash
   ```

The container shares the `questions/` folder with your Mac, so the database it
creates is a normal file at **`questions/db/statsbomb.db`** on your Mac. It
isn't hidden inside Docker.

---

## Seeing the database

Because `db/statsbomb.db` lives on your Mac, you can open it with any SQLite
tool while you work. After rerunning `load.py`, refresh or reopen it to see the changes.

### VS Code (SQLite extension)

1. `Cmd+Shift+P` → **SQLite: Open Database** → pick `questions/db/statsbomb.db`
2. A **SQLITE EXPLORER** panel appears at the bottom of the Explorer sidebar
3. Expand it to see each table, and click the ▶ next to a table to see its rows
4. To run your own query: right-click a `.sql` file → **Run Query**

### SQLite shell (built into macOS)

```bash
sqlite3 -header -column db/statsbomb.db
```

```
.tables                          -- list tables
.schema competitions             -- show how a table was created
SELECT * FROM competitions LIMIT 5;
.quit
```
## Development: hot reloading

- **Editing `.sql` or `.py` files:** no restart or rebuild needed. Just run
  them again. The Docker container shares this folder, so it sees your edits too.
- **Working on a query:** use `run_sql.py ... --watch`. The screen clears and
  shows the new result every time you save. SQL errors are printed and it
  keeps watching, so fix the query and save again. `Ctrl+C` stops it.
- **Changing tables in `load.py`:** rerun `load.py` to rebuild the database.
- **Adding a package:** add it to `setup/requirements.txt`, then `docker compose build`.

---

## Cheat sheet

Run from `questions/`.

| I want to…                    | Command                                                                    |
|-------------------------------|----------------------------------------------------------------------------|
| Build the container           | `docker compose build`                                                     |
| (Re)load the database         | `docker compose run --rm py python setup/load.py`                          |
| Run an answer once            | `docker compose run --rm py python setup/run_sql.py <folder>/answer.sql`   |
| Rerun an answer on every save | `docker compose run --rm py python setup/run_sql.py <folder>/answer.sql --watch` |
| Shell inside the container    | `docker compose run --rm py bash`                                          |
| Look at the database          | VS Code: **SQLite: Open Database**, or `sqlite3 -header -column db/statsbomb.db` |
