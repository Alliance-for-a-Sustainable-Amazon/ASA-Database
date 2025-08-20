from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Manage users (create, update, delete, list) in the ASA-Database application'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='action', help='Action to perform')
        
        # Create user subcommand
        create_parser = subparsers.add_parser('create', help='Create a new user')
        create_parser.add_argument('username', type=str, help='Username')
        create_parser.add_argument('password', type=str, help='Password')
        create_parser.add_argument('--email', type=str, help='Email address', default='')
        create_parser.add_argument('--role', type=str, choices=['Admin', 'Researcher'], 
                                   default='Researcher', help='User role (Admin or Researcher)')
        create_parser.add_argument('--superuser', action='store_true', 
                                  help='Create as superuser (full permissions)')
        
        # Update user subcommand
        update_parser = subparsers.add_parser('update', help='Update an existing user')
        update_parser.add_argument('username', type=str, help='Username to update')
        update_parser.add_argument('--password', type=str, help='New password')
        update_parser.add_argument('--email', type=str, help='New email address')
        update_parser.add_argument('--role', type=str, choices=['Admin', 'Researcher'], 
                                  help='Change user role (Admin or Researcher)')
        
        # Delete user subcommand
        delete_parser = subparsers.add_parser('delete', help='Delete a user')
        delete_parser.add_argument('username', type=str, help='Username to delete')
        
        # List users subcommand
        list_parser = subparsers.add_parser('list', help='List all users')
        list_parser.add_argument('--role', type=str, choices=['Admin', 'Researcher'], 
                               help='Filter by role')

    def handle(self, *args, **options):
        action = options.get('action')
        
        if action == 'create':
            self._create_user(options)
        elif action == 'update':
            self._update_user(options)
        elif action == 'delete':
            self._delete_user(options)
        elif action == 'list':
            self._list_users(options)
        else:
            self.stdout.write(self.style.WARNING('Please specify an action: create, update, delete, or list'))
            self.stdout.write('Examples:')
            self.stdout.write('  python manage.py manage_users create username password --role Admin')
            self.stdout.write('  python manage.py manage_users update username --password newpassword')
            self.stdout.write('  python manage.py manage_users list')
    
    def _create_user(self, options):
        username = options['username']
        password = options['password']
        email = options.get('email', '')
        role = options.get('role', 'Researcher')
        is_superuser = options.get('superuser', False)
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User {username} already exists'))
            return
        
        # Create the user
        try:
            if is_superuser:
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(self.style.SUCCESS(f'Created superuser: {username}'))
            else:
                # Regular users, automatically set is_staff for Admin role
                is_staff = (role == 'Admin')
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_staff=is_staff
                )
                
                # Add user to the group
                try:
                    group = Group.objects.get(name=role)
                    user.groups.add(group)
                    self.stdout.write(self.style.SUCCESS(
                        f'Created {role} user: {username} (Staff access: {is_staff})'
                    ))
                except Group.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        f'Group {role} does not exist. Run setup_groups command first.'
                    ))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating user: {str(e)}'))
    
    def _update_user(self, options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            
            # Update email if provided
            if 'email' in options and options['email'] is not None:
                user.email = options['email']
                self.stdout.write(f'Updated email to: {options["email"]}')
            
            # Update password if provided
            if 'password' in options and options['password'] is not None:
                user.set_password(options['password'])
                self.stdout.write('Password updated')
            
            # Update role if provided
            if 'role' in options and options['role'] is not None:
                role = options['role']
                # Clear existing groups
                user.groups.clear()
                
                # Add to new group
                try:
                    group = Group.objects.get(name=role)
                    user.groups.add(group)
                    
                    # Set staff status based on role
                    if role == 'Admin':
                        user.is_staff = True
                    
                    self.stdout.write(f'Changed role to: {role}')
                    
                except Group.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Group {role} does not exist'))
            
            # Save all changes
            user.save()
            self.stdout.write(self.style.SUCCESS(f'User {username} updated successfully'))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist'))
    
    def _delete_user(self, options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            user.delete()
            self.stdout.write(self.style.SUCCESS(f'User {username} deleted successfully'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist'))
    
    def _list_users(self, options):
        users = User.objects.all().order_by('username')
        
        # Filter by role/group if specified
        if 'role' in options and options['role'] is not None:
            group_name = options['role']
            try:
                group = Group.objects.get(name=group_name)
                users = users.filter(groups=group)
                self.stdout.write(f'Users with role {group_name}:')
            except Group.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Group {group_name} does not exist'))
                return
        else:
            self.stdout.write('All users:')
        
        # Display users with their information
        if not users.exists():
            self.stdout.write('  No users found')
            return
            
        format_str = f'{"USERNAME":<15} {"EMAIL":<25} {"ROLE":<12} {"STAFF":<6} {"ACTIVE":<6}'
        self.stdout.write(format_str)
        self.stdout.write('-' * 70)
            
        for user in users:
            groups = ', '.join([g.name for g in user.groups.all()]) or 'None'
            staff = "Yes" if user.is_staff else "No"
            active = "Yes" if user.is_active else "No"
            
            if user.is_superuser:
                groups = "Superuser"
                staff = "Yes"
                
            self.stdout.write(f'{user.username:<15} {user.email:<25} {groups:<12} {staff:<6} {active:<6}')
