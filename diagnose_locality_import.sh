#!/bin/bash

# Script to diagnose why locality import from Excel isn't working
echo "Diagnosing locality import from Excel issue..."

# Create a diagnostic Python script
cat > /tmp/diagnose_locality_import.py << 'EOF'
import os
import sys
import django
import pandas as pd

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.abspath(os.getcwd()))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_data_app.settings')
django.setup()

from butterflies.models import Locality
from django.db import connection

print("\n1. Checking expected column names for Locality model:")
locality_fields = [f.name for f in Locality._meta.fields if f.name != 'id']
print(f"Expected fields: {', '.join(locality_fields)}")

print("\n2. Let's verify what columns our import function expects for localities:")
from butterflies.views import import_model

# Monkey patch the import_model function to print its expectations
import types
import functools
from django.http import HttpRequest

original_import_model = import_model

def patched_import_model(request, model_name):
    print(f"Import function called for model: {model_name}")
    
    if model_name == 'locality':
        print("This is a locality import. Checking expected fields...")
        
    # Call the original function with a fake request to get the context
    fake_request = HttpRequest()
    fake_request.method = 'GET'
    
    try:
        # Try to call the original function but catch any exceptions
        result = original_import_model(fake_request, model_name)
        # Print expected fields for this model
        if hasattr(result, 'context_data'):
            context = result.context_data
            if 'model_fields' in context:
                print(f"Expected fields for {model_name}: {context['model_fields']}")
            if 'unique_field' in context:
                print(f"Unique field for {model_name}: {context['unique_field']}")
    except Exception as e:
        print(f"Error analyzing import function: {str(e)}")
    
    # Return None since this is just for analysis
    return None

# Replace the import_model function with our patched version for testing
import butterflies.views
butterflies.views.import_model = patched_import_model

# Test what the import function expects for localities
print("Calling import_model with 'locality':")
import_result = import_model(None, 'locality')

print("\n3. Let's analyze a sample Excel file for locality imports:")
print("NOTE: You'll need to provide a sample Excel file to continue.")
print("Please place your Excel file at /tmp/locality_sample.xlsx")

excel_path = '/tmp/locality_sample.xlsx'
if os.path.exists(excel_path):
    try:
        # Read the Excel file
        print(f"Reading Excel file: {excel_path}")
        df = pd.read_excel(excel_path)
        
        # Print column names
        print("\nColumns in Excel file:")
        for col in df.columns:
            print(f"- {col}")
        
        # Check if expected columns are present
        missing_columns = []
        for field in locality_fields:
            if field not in df.columns:
                missing_columns.append(field)
        
        if missing_columns:
            print(f"\nMISSING COLUMNS: {', '.join(missing_columns)}")
            print("This could be why your import isn't finding any localities!")
        else:
            print("\nAll required columns are present in the Excel file.")
            
        # Show first few rows
        print("\nFirst 3 rows of data:")
        print(df.head(3))
        
    except Exception as e:
        print(f"Error analyzing Excel file: {str(e)}")
else:
    print(f"No Excel file found at {excel_path}")
    print("Please add a sample file to continue diagnosis")

print("\n4. Testing if Django can read localityTable properly:")
print(f"Current locality count: {Locality.objects.count()}")
print("First 5 localities in database:")
for loc in Locality.objects.all()[:5]:
    print(f"- {loc.localityCode} (Country: {loc.country or 'None'})")

print("\n5. Checking the actual database columns for localityTable:")
with connection.cursor() as cursor:
    cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns
    WHERE table_name = 'localityTable'
    ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    print("localityTable columns:")
    for col in columns:
        print(f"- {col[0]} ({col[1]})")
EOF

# Run the diagnostic script
python3 /tmp/diagnose_locality_import.py
