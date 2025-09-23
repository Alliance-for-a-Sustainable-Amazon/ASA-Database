#!/bin/bash

# Check if the table name in the database matches what's expected in the model
echo "Checking database table names for locality..."

# Create a diagnostic Python script
cat > /tmp/check_locality.py << 'EOF'
import os
import sys
import django

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.abspath(os.getcwd()))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_data_app.settings')
django.setup()

from butterflies.models import Locality
from django.db import connection

# Check the Django model count
print(f"Django Locality.objects.count(): {Locality.objects.count()}")

# Print the table name used by Django ORM
print(f"Django table name for Locality: {Locality._meta.db_table}")

# Check the actual tables in the database
with connection.cursor() as cursor:
    cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    print("\nAll tables in database:")
    for table in tables:
        print(f"- {table[0]}")

# Check if both tables exist and count records
with connection.cursor() as cursor:
    # Check if localityTable exists
    cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'localityTable'
    );
    """)
    locality_table_exists = cursor.fetchone()[0]
    
    # Check if butterflies_locality exists
    cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'butterflies_locality'
    );
    """)
    butterflies_locality_exists = cursor.fetchone()[0]
    
    print(f"\nlocalityTable exists: {locality_table_exists}")
    print(f"butterflies_locality exists: {butterflies_locality_exists}")
    
    # Count records in each table if they exist
    if locality_table_exists:
        cursor.execute('SELECT COUNT(*) FROM "localityTable"')
        locality_count = cursor.fetchone()[0]
        print(f"Records in localityTable: {locality_count}")
    
    if butterflies_locality_exists:
        cursor.execute('SELECT COUNT(*) FROM "butterflies_locality"')
        butterflies_locality_count = cursor.fetchone()[0]
        print(f"Records in butterflies_locality: {butterflies_locality_count}")

# Print some sample data from the table Django is using
print("\nSample data from Django Locality model:")
localities = Locality.objects.all()[:5]
for loc in localities:
    print(f"- {loc.localityCode}")

# Raw SQL to check raw data in both tables if they exist
with connection.cursor() as cursor:
    print("\nRaw SQL data check:")
    
    if locality_table_exists:
        print("First 5 records from localityTable:")
        cursor.execute('SELECT "localityCode" FROM "localityTable" LIMIT 5')
        for row in cursor.fetchall():
            print(f"- {row[0]}")
    
    if butterflies_locality_exists:
        print("\nFirst 5 records from butterflies_locality:")
        cursor.execute('SELECT "localityCode" FROM "butterflies_locality" LIMIT 5')
        for row in cursor.fetchall():
            print(f"- {row[0]}")
EOF

# Run the diagnostic script
python3 /tmp/check_locality.py
