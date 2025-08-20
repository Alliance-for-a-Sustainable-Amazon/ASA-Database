from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
import os

class Command(BaseCommand):
    help = 'Creates a default admin user if none exists'

    def handle(self, *args, **options):
        # Get credentials from environment variables
        username = os.environ.get('DJANGO_ADMIN_USERNAME', 'admin')
        email = os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_ADMIN_PASSWORD')
        
        if not password:
            self.stdout.write(self.style.ERROR('Admin password not provided. Set DJANGO_ADMIN_PASSWORD environment variable.'))
            return
            
        # Check if user exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User {username} already exists, skipping creation'))
            return
            
        # Create admin user as superuser (full access to Django admin)
        admin_user = User.objects.create_superuser(username=username, email=email, password=password)
        # Note: create_superuser automatically sets is_staff=True and is_superuser=True
        
        # Add user to Admin group
        try:
            admin_group = Group.objects.get(name='Admin')
            admin_user.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS(f'Created superuser {username} with full Django admin access and added to Admin group'))
        except Group.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin group does not exist. Run setup_groups command first.'))
