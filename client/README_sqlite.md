# Running ASA-Database as a Local (SQLite) App

This guide is for users who want to run the app locally (single-user, offline mode) using SQLite.

## 1. Requirements
- Python 3.10+
- pip

## 2. Setup Steps
1. Open a terminal in the `client/` folder.
2. Run:
   ```bash
   chmod +x run_local_sqlite.sh
   ./run_local_sqlite.sh
   ```
3. The app will be available at `http://localhost:8000`.

## 3. Notes
- This mode is for single-user/offline use only.
- Data is stored in `db.sqlite3` in your project folder.
- To migrate to the networked (host) version, copy your data or export/import as needed.
