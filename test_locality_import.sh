#!/bin/bash

# Create a script to add a test locality and check if it worked
cat > /tmp/add_test_locality.py << 'EOF'
import os
import sys
import django
import uuid

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.abspath(os.getcwd()))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_data_app.settings')
django.setup()

from butterflies.models import Locality
from django.db import connection

# Generate a unique test code
test_code = f"TEST-{uuid.uuid4().hex[:6]}"

print(f"Adding test locality with code: {test_code}")

# Create a test locality
test_locality = Locality.objects.create(
    localityCode=test_code,
    country="Test Country",
    region="Test Region"
)

print(f"Test locality created with ID: {test_locality.localityCode}")

# Verify it exists in the database
print("Checking if locality exists in database...")
locality = Locality.objects.filter(localityCode=test_code).first()
if locality:
    print(f"✓ Found in Django ORM: {locality.localityCode}, Country: {locality.country}")
else:
    print("✗ Not found in Django ORM!")

# Check raw SQL in both tables
with connection.cursor() as cursor:
    # Check localityTable
    cursor.execute(f'SELECT COUNT(*) FROM "localityTable" WHERE "localityCode" = %s', [test_code])
    count = cursor.fetchone()[0]
    print(f"✓ Found in localityTable: {count} records")
    
    # Check butterflies_locality
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'butterflies_locality');")
    butterflies_locality_exists = cursor.fetchone()[0]
    
    if butterflies_locality_exists:
        cursor.execute('SELECT COUNT(*) FROM "butterflies_locality" WHERE "locality" = %s', [test_code])
        count = cursor.fetchone()[0]
        print(f"✓ Found in butterflies_locality: {count} records")

print("\nAll Localities:")
for loc in Locality.objects.all().order_by('localityCode')[:15]:
    print(f"- {loc.localityCode}")
EOF

# Run the script
echo "Running test script..."
python3 /tmp/add_test_locality.py
