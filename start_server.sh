#!/bin/bash
export AZURE_BLOB_SAS_TOKEN="sv=2024-11-04&ss=bfqt&srt=sco&sp=rtfx&se=2025-08-22T22:04:17Z&spr=https&sig=x0Y3GoSQx1yv3cnJsn8Z1Xrsc2UBP7k3JwsjKlqu%2FKg%3D"
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

# Start Django development server
python manage.py runserver
