#!/bin/bash
# =========================================================
# Startup Script for ASA Database
# Handles proper database initialization
# =========================================================

echo "===== ASA DATABASE STARTUP SCRIPT ====="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version 2>&1)"

# Make sure we're in the right directory for Azure
cd /home/site/wwwroot || cd /tmp/8dde048fd0bd802 || true
echo "Working directory: $(pwd)"

# Set environment variables
echo "Setting environment variables..."
export PYTHONPATH="$(pwd):$PYTHONPATH"
export DJANGO_SETTINGS_MODULE=research_data_app.settings_azure
echo "DJANGO_SETTINGS_MODULE set to: $DJANGO_SETTINGS_MODULE"
echo "PYTHONPATH set to: $PYTHONPATH"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Static collection failed but continuing"

# Handle database migrations with ultimate robustness
echo "Starting robust database migration process..."

# First, try to determine if we're working with a completely fresh database
echo "Checking database state..."
FRESH_DB=false
if ! python -c "
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_data_app.settings_azure')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        tables = connection.introspection.table_names()
        if 'auth_user' in tables or 'django_migrations' in tables:
            sys.exit(1)  # Tables exist
        else:
            sys.exit(0)  # Fresh database
except Exception as e:
    print(f'Error checking tables: {e}')
    sys.exit(2)  # Error
" 2>/dev/null; then
    RESULT=$?
    if [ $RESULT -eq 0 ]; then
        echo "Detected completely fresh database with no tables"
        FRESH_DB=true
    elif [ $RESULT -eq 1 ]; then
        echo "Detected existing database with some tables"
    else
        echo "Error checking database state, will try migrations anyway"
    fi
else
    echo "Database check script ran without expected exit code, assuming fresh database"
    FRESH_DB=true
fi

# First attempt - try to fix any broken migration history
echo "Attempting to repair any broken migration history..."
python manage.py migrate --fake zero || echo "Could not fake zero migrations, continuing anyway"

# For a fresh database, we need to be extremely careful with the order
if [ "$FRESH_DB" = true ]; then
    echo "FRESH DATABASE DETECTED: Using specialized migration sequence"
    
    # Apply Django's built-in app migrations first in the correct order
    echo "Step 1: Applying Django's core migrations first..."
    python manage.py migrate auth --fake-initial || echo "Auth migration failed but continuing"
    python manage.py migrate admin --fake-initial || echo "Admin migration failed but continuing"
    python manage.py migrate contenttypes --fake-initial || echo "Contenttypes migration failed but continuing"
    python manage.py migrate sessions --fake-initial || echo "Sessions migration failed but continuing"
    
    # Apply the app's initial migration
    echo "Step 2: Applying butterflies initial migration..."
    python manage.py migrate butterflies 0001_initial --fake-initial || echo "Initial butterflies migration failed but continuing"
    
    # Apply any fix migrations specifically
    echo "Step 3: Applying fix migration for locality foreign key types..."
    python manage.py migrate butterflies 0002_fix_locality_fk_type || echo "Fix migration failed but continuing"
    
    # Apply any remaining migrations
    echo "Step 4: Applying any remaining migrations..."
    python manage.py migrate || echo "Final migration step failed but continuing"
else
    # For existing databases, try a more standard approach
    echo "EXISTING DATABASE DETECTED: Using standard migration approach"
    python manage.py migrate || echo "Standard migration failed but continuing"
fi

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

# Make sure the ALLOWED_HOSTS setting includes Azure's internal IP
echo "Checking and updating ALLOWED_HOSTS for Azure..."
if [ -n "$WEBSITE_HOSTNAME" ]; then
    echo "WEBSITE_HOSTNAME is set to: $WEBSITE_HOSTNAME"
    # Add 169.254.131.2 to ALLOWED_HOSTS if running in Azure
    export ALLOWED_HOSTS="$WEBSITE_HOSTNAME,localhost,127.0.0.1,169.254.131.2"
    echo "ALLOWED_HOSTS set to: $ALLOWED_HOSTS"
fi

# Start Gunicorn server
echo "Starting Gunicorn server..."
gunicorn --bind=0.0.0.0:8000 --timeout 600 --access-logfile - --error-logfile - research_data_app.wsgi:application
