#!/bin/bash
# Azure App Service deployment script

echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

echo "Deployment complete!"
