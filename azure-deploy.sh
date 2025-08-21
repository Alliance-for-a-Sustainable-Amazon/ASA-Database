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

# Don't run migrations here - let startup.sh handle it with proper sequencing
echo "Database migrations will be handled by startup.sh"

# Make startup.sh executable
echo "Making startup.sh executable"
chmod +x startup.sh || echo "Failed to make startup.sh executable, but continuing"

# Create default admin user if environment variables are set
if [ -n "$DJANGO_ADMIN_PASSWORD" ]; then
    echo "Creating default admin user"
    python manage.py create_default_admin || echo "Admin creation failed but continuing"
else
    echo "Skipping admin creation - DJANGO_ADMIN_PASSWORD not set"
fi

# Start with very explicit path
echo "===== STARTING APPLICATION ====="
echo "Starting Gunicorn with explicit application import"

# Direct approach with explicit path to wsgi.py file
cd /home/site/wwwroot
exec gunicorn --bind=0.0.0.0:8000 --log-level debug --pythonpath '/home/site/wwwroot' research_data_app.wsgi:application
