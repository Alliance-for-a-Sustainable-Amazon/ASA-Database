#!/bin/bash






# Collect static files


echo "Collecting static files..."


python manage.py collectstatic --noinput





# Apply database migrations


echo "Applying database migrations..."


python manage.py migrate



# Create admin user from environment variables


echo "Checking for admin credentials..."


if [ -n "$DJANGO_ADMIN_USERNAME" ] && [ -n "$DJANGO_ADMIN_PASSWORD" ]; then
    echo "Creating/updating admin user..."
    python -c "
import os
# Ensure DJANGO_SETTINGS_MODULE has a sensible default when running this script
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_azure.py')
import django
django.setup()
from django.contrib.auth.models import User
username = os.environ.get('DJANGO_ADMIN_USERNAME')
password = os.environ.get('DJANGO_ADMIN_PASSWORD')
email = os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@example.com')
if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    user.set_password(password)
    user.email = email
    user.is_superuser = True
    # user.is_staff = True
    user.save()
    print(f'Updated existing admin user: {username} (superuser/staff set)')
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Created new admin user: {username}')
"
fi



# Start Gunicorn server


echo "Starting Gunicorn server..."


# Use 2 workers + 2 threads per worker for better concurrency
# --preload loads app once and shares across workers (saves memory)
# --timeout 600 allows long-running requests
gunicorn --bind=0.0.0.0:8000 --workers 2 --threads 2 --preload --timeout 600 research_data_app.wsgi:application