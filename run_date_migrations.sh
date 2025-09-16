#!/bin/bash
# Script to apply date field migrations (simplified version)

echo "Starting date field conversion migrations"
python manage.py migrate butterflies

echo "Running fresh migrations to ensure all migrations are applied"
python manage.py makemigrations
python manage.py migrate

echo "Migrations completed."
