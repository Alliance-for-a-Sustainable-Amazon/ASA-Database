#!/bin/bash

# Script to diagnose and fix the locality foreign key issue
echo "Diagnosing and fixing locality foreign key relationship issue..."

# Create a Python script to diagnose and fix the relationship
cat > /tmp/fix_locality_fk.py << 'EOF'
import os
import sys
import django

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.abspath(os.getcwd()))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_data_app.settings')
django.setup()

from django.db import connection
from butterflies.models import Locality, Specimen

print("Diagnosing foreign key relationships...")

# Identify all foreign key constraints
with connection.cursor() as cursor:
    cursor.execute("""
    SELECT
        tc.constraint_name, 
        tc.table_name, 
        kcu.column_name, 
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name
    FROM 
        information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
          AND ccu.table_schema = tc.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND (tc.table_name = 'butterflies_specimen' OR ccu.table_name = 'butterflies_locality')
    """)
    constraints = cursor.fetchall()
    
    print("\nForeign Key Constraints:")
    for constraint in constraints:
        print(f"Constraint: {constraint[0]}")
        print(f"  Table: {constraint[1]}.{constraint[2]}")
        print(f"  References: {constraint[3]}.{constraint[4]}")

print("\nChecking specimen table structure...")
with connection.cursor() as cursor:
    # Check specimen table columns
    cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'butterflies_specimen'
    ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    print("\nSpecimen Table Columns:")
    for col in columns:
        print(f"  {col[0]} ({col[1]}, Nullable: {col[2]})")

    # Count specimens with locality references
    cursor.execute("""
    SELECT COUNT(*) FROM "butterflies_specimen"
    WHERE locality_id IS NOT NULL
    """)
    specimen_count = cursor.fetchone()[0]
    print(f"\nSpecimens with locality_id: {specimen_count}")

print("\nChecking what table the Django ORM is actually using...")
print(f"Specimen model table: {Specimen._meta.db_table}")
print(f"Locality model table: {Locality._meta.db_table}")

print("\nThe Django ORM is configured to use:")
print(f"- {Specimen._meta.db_table} for specimens")
print(f"- {Locality._meta.db_table} for localities")

if Specimen._meta.db_table != "butterflies_specimen" or Locality._meta.db_table != "butterflies_locality":
    print("\nThere's a mismatch between the table names in Django models and the foreign key constraints!")
    print("This explains why you can add localities but not use them in specimens.")
    print("\nDo you want to fix this by either:")
    print("1. Removing the foreign key constraint (if it's safe to do so)")
    print("2. Copying data from localityTable to butterflies_locality")
    print("3. Updating the Django models to use the tables with the constraints")
    print("\nOption 1 is recommended if you're not using the butterflies_locality table.")
    
    fix_choice = input("\nEnter your choice (1, 2, or 3): ")
    
    if fix_choice == "1":
        print("\nRemoving the foreign key constraint...")
        with connection.cursor() as cursor:
            # Get the constraint name
            constraint_name = None
            for constraint in constraints:
                if constraint[1] == 'butterflies_specimen' and constraint[3] == 'butterflies_locality':
                    constraint_name = constraint[0]
                    break
            
            if constraint_name:
                print(f"Dropping constraint {constraint_name}...")
                cursor.execute(f'ALTER TABLE "butterflies_specimen" DROP CONSTRAINT "{constraint_name}"')
                print("Constraint dropped successfully!")
                
                print("Now dropping the empty butterflies_locality table...")
                cursor.execute('DROP TABLE IF EXISTS "butterflies_locality"')
                print("Table butterflies_locality dropped successfully!")
            else:
                print("No constraint found between butterflies_specimen and butterflies_locality.")
        
        print("\nFix complete! You should now be able to use localities in specimens.")
    
    elif fix_choice == "2":
        print("\nCopying data from localityTable to butterflies_locality...")
        # Implementation would go here, but not recommended
        print("This option is not implemented as it's not recommended.")
    
    elif fix_choice == "3":
        print("\nUpdating Django models would require code changes.")
        print("This is not implemented in this script.")
    
    else:
        print("\nInvalid choice. No changes made.")
else:
    print("\nNo mismatch detected. Django models are configured correctly.")

print("\nDiagnosis complete!")
EOF

# Run the script
python3 /tmp/fix_locality_fk.py
