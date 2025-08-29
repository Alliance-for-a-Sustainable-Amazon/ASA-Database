#!/bin/bash
# Start PostgreSQL service (if available)
if command -v systemctl &> /dev/null; then
    sudo systemctl start postgresql
elif command -v service &> /dev/null; then
    sudo service postgresql start
else
    echo "Please start your PostgreSQL server manually."
fi


# Load environment variables from .env.local if present
if [ -f .env.local ]; then
    echo "Loading environment variables from .env.local..."
    set -a
    source .env.local
    set +a
fi

# Activate Python virtual environment
source .venv/bin/activate

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Start Django development server
python manage.py runserver
