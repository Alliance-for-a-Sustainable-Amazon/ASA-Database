#!/bin/bash

# Script to remove the empty butterflies_locality table
echo "Running script to remove empty butterflies_locality table..."

# Create a Python script to check and remove the table
cat > /tmp/remove_empty_table.py << 'EOF'
import os
import sys
import django

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.abspath(os.getcwd()))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_data_app.settings')
django.setup()

from django.db import connection

print("Checking if butterflies_locality exists...")
with connection.cursor() as cursor:
    cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'butterflies_locality'
    );
    """)
    butterflies_locality_exists = cursor.fetchone()[0]
    
    if butterflies_locality_exists:
        print("Found butterflies_locality table. Checking if it's empty...")
        cursor.execute('SELECT COUNT(*) FROM "butterflies_locality"')
        count = cursor.fetchone()[0]
        print(f"Records in butterflies_locality: {count}")
        
        if count == 0:
            print("Table is empty. Dropping table...")
            cursor.execute('DROP TABLE IF EXISTS "butterflies_locality"')
            print("Table dropped successfully.")
        else:
            print("Table is not empty. Not dropping table.")
    else:
        print("butterflies_locality table doesn't exist. Nothing to do.")

print("Done!")
EOF

# Run the script
python3 /tmp/remove_empty_table.py
