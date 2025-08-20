# Authentication and Authorization in ASA-Database

This document explains how the authentication and authorization system works in the ASA-Database application.

## User Roles

The application has two main user roles:

1. **Admin** - Has full access to all features, including:
   - Viewing specimens and data
   - Adding new specimens, localities, and initials
   - Editing existing specimens and data
   - Deleting specimens and data
   - Importing data from CSV/Excel files
   - Using the bulk delete functionality

2. **Researcher** - Has limited access to features:
   - Viewing specimens and data
   - Adding new specimens only (not localities or initials)
   - Editing existing specimens and data
   - Cannot delete specimens or data
   - Cannot import data from CSV/Excel files
   - Cannot add new localities or initials

## Setting Up the System

### 1. Create Groups and Permissions

Run the following command to set up the Admin and Researcher groups with appropriate permissions:

```bash
python manage.py setup_groups
```

### 2. Create Test Users

To create test users for both roles, run:

```bash
python manage.py create_test_users
```

This will create:
- Admin user: `admin` with password `butterflies123` (with staff access to Django admin panel)
- Researcher user: `researcher` with password `butterflies123`

You can customize the usernames and password:

```bash
python manage.py create_test_users --admin=adminuser --researcher=researchuser --password=custompassword
```

### 3. Create Users Through the Django Admin Interface

1. Go to the Django admin site at `/admin/`
2. Log in with a superuser account
3. Navigate to "Users" under "AUTHENTICATION AND AUTHORIZATION"
4. Click "Add User" and fill in the required information
5. After creating the user, assign them to either the "Admin" or "Researcher" group

## Using the System

1. **Login**: Users must log in at `/accounts/login/` to access the application
2. **Navigation**: Once logged in, users will see their role indicated in the top navigation bar
3. **Access Control**: The UI will automatically hide delete and import functionality for users without proper permissions
4. **Django Admin Access**: Admin users have access to the Django admin panel at `/admin/` for advanced database management

## Security Notes

- Permissions are enforced both at the UI level (hiding buttons) and at the server level (checking permissions on view functions)
- Attempting to access restricted URLs directly will result in an "Access Denied" message
- All CRUD operations require authentication

## Troubleshooting

If you have issues with permissions:

1. Make sure the user is assigned to the correct group
2. Check that the setup_groups command has been run
3. Verify that the user is logged in
4. If needed, clear browser cookies and try logging in again

## Technical Implementation

The authentication system uses Django's built-in authentication and permission system:

- Login required decorators for basic authentication
- Custom permission decorator (admin_required) for admin-only actions
- Group-based permissions for authorization
- Template logic to conditionally display UI elements

### Django Admin Access

The Django admin panel requires users to have the `is_staff` flag set to True. In this application:

1. **Admin users**: Created with `is_staff=True` to allow Django admin panel access
2. **Superusers**: Have full access to all admin functionality
3. **Researcher users**: No access to Django admin panel

The Django admin panel (at `/admin/`) provides advanced database management capabilities beyond what's available in the regular application interface.
