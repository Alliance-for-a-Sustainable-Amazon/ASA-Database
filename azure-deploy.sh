#!/bin/bash
# =========================================================
# Azure Deployment Script for ASA Database
# Simple, focused script for Azure App Service
# =========================================================

echo "===== ASA DATABASE STARTUP SCRIPT ====="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version 2>&1)"
echo "PYTHONPATH: $PYTHONPATH"
echo "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

# Make sure we're in the right directory
cd /home/site/wwwroot
echo "Changed directory to: $(pwd)"
echo "Directory contents:"
ls -la

# Set up Python environment
echo "Setting up Python environment"
export PYTHONPATH="/home/site/wwwroot:$PYTHONPATH"
export DJANGO_SETTINGS_MODULE=research_data_app.settings_azure
echo "DJANGO_SETTINGS_MODULE set to: $DJANGO_SETTINGS_MODULE"

# Simple deployment steps
echo "Installing dependencies"
pip install -r requirements.txt

# Try to collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput || echo "Static collection failed but continuing"

# Try to run migrations
echo "Running database migrations"
python manage.py migrate || echo "Migrations failed but continuing"

# Try the specific migration
echo "Running specific migration for uploaded_iNaturalist"
python manage.py migrate butterflies 0019_remove_uploaded_inaturalist || echo "Specific migration failed but continuing"

# Start with very explicit path
echo "===== STARTING APPLICATION ====="
echo "Starting Gunicorn with explicit application import"

# Direct approach with explicit path to wsgi.py file
cd /home/site/wwwroot
exec gunicorn --bind=0.0.0.0:8000 --log-level debug --pythonpath '/home/site/wwwroot' research_data_app.wsgi:application
