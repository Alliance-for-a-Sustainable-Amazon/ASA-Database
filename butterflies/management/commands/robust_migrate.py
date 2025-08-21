"""
Command to perform robust migrations that can recover from common migration issues.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection

class Command(BaseCommand):
    help = 'Performs migrations in a way that can recover from common issues'

    def add_arguments(self, parser):
        parser.add_argument('--fresh', action='store_true', 
                            help='Indicate this is a fresh database with no tables')

    def handle(self, *args, **options):
        fresh_db = options['fresh']
        
        # Check if database has any tables (for auto-detection of fresh DB)
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT COUNT(*) FROM django_migrations")
                count = cursor.fetchone()[0]
                if count == 0 and not fresh_db:
                    self.stdout.write(self.style.WARNING('No migration records found, treating as fresh database'))
                    fresh_db = True
            except Exception:
                # Table doesn't exist, so it's a fresh database
                if not fresh_db:
                    self.stdout.write(self.style.WARNING('django_migrations table not found, treating as fresh database'))
                    fresh_db = True
        
        if fresh_db:
            self.stdout.write(self.style.SUCCESS('Starting fresh database migration sequence'))
            
            # Try to fake migrations to zero (may fail on fresh DB, that's OK)
            try:
                self.stdout.write('Attempting to fake zero migrations...')
                call_command('migrate', '--fake', 'zero')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Fake zero failed (expected on fresh DB): {e}'))
            
            # Apply Django's built-in app migrations first
            self.stdout.write('Applying auth migrations...')
            call_command('migrate', 'auth', '--fake-initial')
            
            self.stdout.write('Applying contenttypes migrations...')
            call_command('migrate', 'contenttypes', '--fake-initial')
            
            self.stdout.write('Applying admin migrations...')
            call_command('migrate', 'admin', '--fake-initial')
            
            self.stdout.write('Applying sessions migrations...')
            call_command('migrate', 'sessions', '--fake-initial')
            
            # Apply the app's initial migration
            self.stdout.write('Applying butterflies initial migration...')
            try:
                call_command('migrate', 'butterflies', '0001_initial', '--fake-initial')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Initial migration failed, will try fix migration: {e}'))
            
            # Apply fix migration specifically
            self.stdout.write('Applying fix migration for locality FK type...')
            try:
                call_command('migrate', 'butterflies', '0002_fix_locality_fk_type')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Fix migration failed: {e}'))
                
            # Apply any remaining migrations
            self.stdout.write('Applying remaining migrations...')
            call_command('migrate')
            
        else:
            # For existing databases
            self.stdout.write(self.style.SUCCESS('Migrating existing database'))
            call_command('migrate')
            
        self.stdout.write(self.style.SUCCESS('Migration complete'))
