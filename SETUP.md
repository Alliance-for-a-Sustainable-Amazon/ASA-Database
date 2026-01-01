## Initial Setup

### 1. Create Python virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Set up local PostgreSQL server

Install PostgreSQL:
```bash
brew install postgresql@14
brew services start postgresql@14
```

Create the database and user (credentials from settings.py):
```bash
# Access PostgreSQL
psql postgres

# Run these SQL commands:
CREATE USER asa_user WITH PASSWORD 'asa_password';
CREATE DATABASE asa_db;
GRANT ALL PRIVILEGES ON DATABASE asa_db TO asa_user;
ALTER USER asa_user WITH SUPERUSER;
\q
```

Test the connection:
```bash
psql -U asa_user -d asa_db -h localhost
# Enter password: asa_password
```

### 3. Run the server
```bash
./start_server.sh
```

**Note:** The database credentials in `settings.py` are:
- Database: `asa_db`
- User: `asa_user`
- Password: `asa_password`
- Host: `localhost`
- Port: `5432`

These are hardcoded for development. For production, use environment variables.