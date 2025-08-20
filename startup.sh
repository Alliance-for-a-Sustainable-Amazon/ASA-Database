#!/bin/bash

# Set environment variables
echo "Setting environment variables..."
export DJANGO_SETTINGS_MODULE=research_data_app.settings_azure

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# TEMPORARY: Reset and rebuild the database from scratch
# WARNING: This will delete all data in the database
echo "PERFORMING FULL DATABASE RESET..."
echo "Dropping all tables..."
python manage.py flush --no-input || echo "Flush failed but continuing"

echo "Resetting migrations..."
python manage.py migrate butterflies zero --fake || echo "Migration reset failed but continuing"

echo "Applying all migrations from scratch..."
python manage.py migrate || echo "Migrations failed but continuing"

echo "Database reset completed!"
# REMOVE THIS BLOCK AFTER ONE SUCCESSFUL RUN

# Set up user groups
echo "Setting up user groups and permissions..."
python manage.py setup_groups || echo "Group setup failed but continuing"

# Create default admin user if environment variables are set
if [ -n "$DJANGO_ADMIN_PASSWORD" ]; then
    echo "Creating default admin user..."
    python manage.py create_default_admin || echo "Admin creation failed but continuing"
else
    echo "Skipping admin creation - DJANGO_ADMIN_PASSWORD not set"
fi

# Start Gunicorn server
echo "Starting Gunicorn server..."
gunicorn --bind=0.0.0.0:8000 --timeout 600 research_data_app.wsgi:application
