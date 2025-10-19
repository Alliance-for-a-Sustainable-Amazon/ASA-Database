#!/bin/bash
# Start PostgreSQL service (if available)
if command -v systemctl &> /dev/null; then
    sudo systemctl start postgresql
elif command -v service &> /dev/null; then
    sudo service postgresql start
else
    echo "Please start your PostgreSQL server manually."
fi

# Activate Python virtual environment
source .venv/bin/activate

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Start Django development server in debug mode
python manage.py runserver --insecure
