#!/bin/bash
# Script to fix the database type mismatch on Azure
# This script should be run directly on the Azure App Service

# Stop the application first
echo "Stopping the application..."
echo "NOTE: Your site will be temporarily unavailable during this fix"

# Export database connection details from environment variables (for manual use if needed)
# The script will use the Django ORM to run the migration
echo "Preparing to fix the database schema..."

# Run the Django migration to fix the type mismatch
echo "Running database migration to fix the type mismatch..."
python manage.py migrate butterflies 0012_fix_locality_fk_type
if [ $? -eq 0 ]; then
    echo "Migration successfully applied!"
    echo "The database schema has been fixed to correct the type mismatch."
else
    echo "Migration failed. Please check the error messages above."
    echo "If the migration fails, you might need to manually fix the schema using PostgreSQL commands."
    echo "You can connect to your Azure Database for PostgreSQL server and run:"
    echo "---------------------------------------------------------------"
    echo "-- Fix the foreign key relationship between specimen and locality tables"
    echo "UPDATE \"specimenTable\""
    echo "SET locality_id = NULL"
    echo "WHERE locality_id IS NOT NULL AND NOT EXISTS ("
    echo "    SELECT 1 FROM \"localityTable\" WHERE \"localityCode\" = CAST(locality_id AS VARCHAR)"
    echo ");"
    echo ""
    echo "-- Create a temporary column with the correct data type"
    echo "ALTER TABLE \"specimenTable\" "
    echo "ADD COLUMN locality_id_new VARCHAR(100) REFERENCES \"localityTable\"(\"localityCode\") ON DELETE SET NULL;"
    echo ""
    echo "-- Copy data, converting from integer to string if needed"
    echo "UPDATE \"specimenTable\""
    echo "SET locality_id_new = CAST(locality_id AS VARCHAR)"
    echo "WHERE locality_id IS NOT NULL;"
    echo ""
    echo "-- Drop the original foreign key constraint"
    echo "ALTER TABLE \"specimenTable\" DROP CONSTRAINT IF EXISTS specimenTable_locality_id_fkey;"
    echo ""
    echo "-- Drop the original column"
    echo "ALTER TABLE \"specimenTable\" DROP COLUMN locality_id;"
    echo ""
    echo "-- Rename the new column to the original name"
    echo "ALTER TABLE \"specimenTable\" RENAME COLUMN locality_id_new TO locality_id;"
    echo "---------------------------------------------------------------"
fi

echo "Done."
