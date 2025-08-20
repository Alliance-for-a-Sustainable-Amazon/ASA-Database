from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from butterflies.models import Specimen, Locality, Initials

class Command(BaseCommand):
    help = 'Creates Admin and Researcher groups with appropriate permissions'

    def handle(self, *args, **options):
        # Create the groups if they don't exist
        admin_group, admin_created = Group.objects.get_or_create(name='Admin')
        researcher_group, researcher_created = Group.objects.get_or_create(name='Researcher')
        
        if admin_created:
            self.stdout.write(self.style.SUCCESS('Admin group created'))
        else:
            self.stdout.write(self.style.WARNING('Admin group already exists'))
            
        if researcher_created:
            self.stdout.write(self.style.SUCCESS('Researcher group created'))
        else:
            self.stdout.write(self.style.WARNING('Researcher group already exists'))
        
        # Get all permissions for our models
        models = [Specimen, Locality, Initials]
        
        # All permissions for Admin group
        all_permissions = []
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            model_perms = Permission.objects.filter(content_type=content_type)
            all_permissions.extend(model_perms)
        
        # Give all permissions to Admin group
        admin_group.permissions.set(all_permissions)
        self.stdout.write(self.style.SUCCESS(f'Added {len(all_permissions)} permissions to Admin group'))
        
        # Permissions for Researcher group (excluding delete permissions and adding localities/initials)
        researcher_permissions = []
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            # Start with all non-delete permissions
            model_perms = Permission.objects.filter(
                content_type=content_type
            ).exclude(codename__startswith='delete_')
            
            # For Locality and Initials models, exclude add permission as well
            if model in [Locality, Initials]:
                model_perms = model_perms.exclude(codename__startswith='add_')
            
            researcher_permissions.extend(model_perms)
        
        # Give restricted permissions to Researcher group
        researcher_group.permissions.set(researcher_permissions)
        self.stdout.write(self.style.SUCCESS(f'Added {len(researcher_permissions)} permissions to Researcher group'))
        
        self.stdout.write(self.style.SUCCESS('Groups and permissions setup complete!'))
