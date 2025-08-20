#!/bin/bash
# Script to completely reset the database and rebuild from scratch

echo "WARNING: This script will completely reset the database!"
echo "All data will be lost and the database will be rebuilt from scratch."

# Drop all tables (using Django's flush command with --no-input)
echo "Dropping all tables..."
python manage.py flush --no-input || echo "Flush failed but continuing"

# Reset migrations
echo "Resetting migrations..."
python manage.py migrate butterflies zero --fake || echo "Migration reset failed but continuing"

# Apply all migrations from scratch
echo "Applying all migrations from scratch..."
python manage.py migrate || echo "Migrations failed but continuing"

# Set up user groups
echo "Setting up user groups and permissions..."
python manage.py setup_groups || echo "Group setup failed but continuing"

echo "Database reset complete!"
