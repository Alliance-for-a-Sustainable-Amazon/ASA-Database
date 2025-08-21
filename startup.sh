#!/bin/bash






# Collect static files


echo "Collecting static files..."


python manage.py collectstatic --noinput





# Apply database migrations


echo "Applying database migrations..."


python manage.py migrate





# Start Gunicorn server


echo "Starting Gunicorn server..."


gunicorn --bind=0.0.0.0:8000 --timeout 600 research_data_app.wsgi:application