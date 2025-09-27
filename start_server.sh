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

# Configure for better handling of large imports
export PYTHONWARNINGS="ignore::DeprecationWarning" 
# Increase Python memory limits for large dataframes
export PYTHONMALLOC=malloc
# Enable fault handler for better debugging
export PYTHONFAULTHANDLER=1
# Allow larger file uploads (Django setting will also need to be updated)
export MAX_UPLOAD_SIZE=52428800

# Start Django development server in debug mode
echo "Starting server with enhanced memory settings for large imports..."
python -X faulthandler manage.py runserver --insecure 0.0.0.0:8000
