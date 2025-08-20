#!/bin/bash
# Script to make all Admin users into superusers

echo "Creating Python script to update user privileges..."

cat > update_admin_users.py << 'EOF'
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_data_app.settings')
django.setup()

# Import models
from django.contrib.auth.models import User, Group

# Find Admin group
try:
    admin_group = Group.objects.get(name='Admin')
    print(f"Found Admin group with {admin_group.user_set.count()} users")
    
    # Update all users in Admin group to be superusers
    updated_count = 0
    for user in admin_group.user_set.all():
        if not user.is_superuser:
            user.is_superuser = True
            user.is_staff = True
            user.save()
            updated_count += 1
            print(f"Updated {user.username} to superuser status")
    
    print(f"\nSummary: Updated {updated_count} users to superuser status")
    
except Group.DoesNotExist:
    print("Admin group does not exist. Please create it first.")
EOF

echo "Running the update script..."
python update_admin_users.py

echo "Done! All Admin users now have superuser privileges."
echo "You can now access the user management page at /users/"
