#!/bin/bash

# Set environment variables
echo "Setting environment variables..."
export DJANGO_SETTINGS_MODULE=research_data_app.settings_azure

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Apply database type fix (temporary) - will fix the integer vs varchar issue
echo "Applying database type fix for locality foreign key..."
echo "Setting up fake migration flag for already applied migrations..."
# Mark the natural keys migration as applied
python manage.py migrate butterflies 0012_use_natural_keys --fake || echo "Fake migration failed but continuing"

echo "Applying only the foreign key fix migration..."
python manage.py migrate butterflies 0021_fix_foreign_key_types || echo "Foreign key fix migration failed but continuing"

echo "Fix script completed!"
# The fix only needs to run once - you can remove this block after the first successful run

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
