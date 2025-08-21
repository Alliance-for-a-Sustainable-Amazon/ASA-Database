#!/bin/bash

# Set environment variables
echo "Setting environment variables..."
export DJANGO_SETTINGS_MODULE=research_data_app.settings_azure

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply database migrations with special fix for first run
echo "Applying database migrations..."

# First, apply only the initial migrations (to create basic tables)
echo "Applying initial Django migrations..."
python manage.py migrate auth
python manage.py migrate admin
python manage.py migrate contenttypes
python manage.py migrate sessions

# Then apply the app migrations with --fake-initial to skip dependency checks
echo "Applying butterflies migrations with --fake-initial..."
python manage.py migrate butterflies --fake-initial

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
