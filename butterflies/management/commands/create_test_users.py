from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Creates test users for Admin and Researcher roles'

    def add_arguments(self, parser):
        parser.add_argument('--admin', type=str, help='Admin username')
        parser.add_argument('--researcher', type=str, help='Researcher username')
        parser.add_argument('--password', type=str, help='Password for both users')

    def handle(self, *args, **options):
        admin_username = options.get('admin') or 'admin'
        researcher_username = options.get('researcher') or 'researcher'
        password = options.get('password') or 'butterflies123'
        
        # Get or create the groups
        admin_group = Group.objects.get(name='Admin')
        researcher_group = Group.objects.get(name='Researcher')
        
        # Create admin user if it doesn't exist
        if not User.objects.filter(username=admin_username).exists():
            admin_user = User.objects.create_user(
                username=admin_username,
                email=f'{admin_username}@example.com',
                password=password,
                is_staff=True  # Allow access to Django admin panel
            )
            admin_user.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS(f'Admin user "{admin_username}" created with admin panel access'))
        else:
            admin_user = User.objects.get(username=admin_username)
            admin_user.is_staff = True  # Make sure existing user has admin access
            admin_user.save()
            admin_user.groups.add(admin_group)
            self.stdout.write(self.style.WARNING(f'Admin user "{admin_username}" already exists, set as staff and added to Admin group'))
        
        # Create researcher user if it doesn't exist
        if not User.objects.filter(username=researcher_username).exists():
            researcher_user = User.objects.create_user(
                username=researcher_username,
                email=f'{researcher_username}@example.com',
                password=password
            )
            researcher_user.groups.add(researcher_group)
            self.stdout.write(self.style.SUCCESS(f'Researcher user "{researcher_username}" created'))
        else:
            researcher_user = User.objects.get(username=researcher_username)
            researcher_user.groups.add(researcher_group)
            self.stdout.write(self.style.WARNING(f'Researcher user "{researcher_username}" already exists, added to Researcher group'))
        
        self.stdout.write(self.style.SUCCESS('Test users setup complete!'))
