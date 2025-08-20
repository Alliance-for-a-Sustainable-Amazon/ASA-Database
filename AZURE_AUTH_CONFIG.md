# Authentication Configuration for Azure App Service

This guide explains how to configure authentication and user management for the ASA Database application when deploying to Azure App Service.

## Environment Variables

Set the following environment variables in Azure App Service:

### Required for Basic Functionality

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | A secure secret key for Django | `'a-long-random-string'` |
| `DJANGO_DEBUG` | Set to 'False' for production | `'False'` |
| `DJANGO_SETTINGS_MODULE` | Points to Azure settings | `'research_data_app.settings_azure'` |

### Database Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_DATABASE` | PostgreSQL database name | `'asadb'` |
| `POSTGRES_USER` | PostgreSQL username | `'azureuser@server-name'` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `'YourSecurePassword123!'` |
| `POSTGRES_HOST` | PostgreSQL host | `'server-name.postgres.database.azure.com'` |
| `POSTGRES_PORT` | PostgreSQL port | `'5432'` |

### Authentication Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `DJANGO_ADMIN_USERNAME` | Default admin username | `'admin'` |
| `DJANGO_ADMIN_EMAIL` | Default admin email | `'admin@example.com'` |
| `DJANGO_ADMIN_PASSWORD` | Default admin password | `'SecurePassword123!'` |

## Setting Environment Variables

### Using Azure Portal

1. Navigate to your App Service in Azure Portal
2. Go to **Configuration** > **Application settings**
3. Add each environment variable as a new application setting
4. Click **Save** when done

### Using Azure CLI

```bash
az webapp config appsettings set --resource-group your-resource-group --name your-app-name --settings \
  DJANGO_SECRET_KEY="your-secure-secret-key" \
  DJANGO_DEBUG="False" \
  DJANGO_SETTINGS_MODULE="research_data_app.settings_azure" \
  POSTGRES_DATABASE="your-db-name" \
  POSTGRES_USER="your-db-user@server-name" \
  POSTGRES_PASSWORD="your-secure-password" \
  POSTGRES_HOST="server-name.postgres.database.azure.com" \
  POSTGRES_PORT="5432" \
  DJANGO_ADMIN_USERNAME="admin" \
  DJANGO_ADMIN_EMAIL="admin@example.com" \
  DJANGO_ADMIN_PASSWORD="secure-admin-password"
```

## User Management Process

The deployment process includes these authentication-related steps:

1. **Database Migration**: Creates all necessary tables
2. **Group Setup**: Runs `setup_groups` command to create Admin and Researcher groups
3. **Admin Creation**: Runs `create_default_admin` command to create an admin user

## Managing Users After Deployment

### Creating Additional Users

After deployment, you can manage users through these methods:

1. **Web-Based User Management Interface** (Easiest):
   - Log in as a superuser
   - Navigate to the "Manage Users" link in the navigation bar
   - This provides a user-friendly interface to:
     - View all users and their roles
     - Add new users with specific roles
     - Edit existing users (change roles, activate/deactivate accounts)
     - Delete users when needed

2. **Django Admin Interface** (Alternative):
   - Log in as an admin/superuser at `/admin`
   - Navigate to "Users" under "AUTHENTICATION AND AUTHORIZATION"
   - Click "Add User" to create new accounts
   - After creating a user, edit their profile to:
     - Assign them to either the "Admin" or "Researcher" group
     - Check/uncheck "Staff status" based on whether they need admin panel access

2. **SSH into App Service**:
   ```bash
   az webapp ssh --name your-app-name --resource-group your-resource-group
   cd /home/site/wwwroot
   python manage.py shell
   ```
   Then in the Python shell:
   ```python
   from django.contrib.auth.models import User, Group
   # Create an admin user (with admin panel access)
   admin = User.objects.create_user(username='new_admin', email='admin@example.com', 
                                   password='SecurePass123', is_staff=True)
   admin_group = Group.objects.get(name='Admin')
   admin.groups.add(admin_group)
   admin.save()
   
   # Create a researcher (no admin panel access)
   researcher = User.objects.create_user(username='new_researcher', email='researcher@example.com', 
                                        password='SecurePass123')
   researcher_group = Group.objects.get(name='Researcher')
   researcher.groups.add(researcher_group)
   researcher.save()
   ```

3. **Custom Management Command** (For Remote Management):
   We've created a simplified `manage_users` command that can be used remotely:

   ```bash
   # SSH into Azure App Service
   az webapp ssh --name your-app-name --resource-group your-resource-group
   cd /home/site/wwwroot

   # Creating users
   python manage.py manage_users create username password --email user@example.com --role Admin
   python manage.py manage_users create username password --role Researcher
   python manage.py manage_users create admin_user password --role Admin --superuser

   # Updating users
   python manage.py manage_users update username --password newpass
   python manage.py manage_users update username --email new@example.com --role Admin
   
   # Deleting users
   python manage.py manage_users delete username
   
   # Listing users
   python manage.py manage_users list
   python manage.py manage_users list --role Admin
   ```

### Advanced User Management with Azure AD Integration

For larger organizations or more complex deployments, you may want to integrate with Azure Active Directory:

1. **Azure AD Authentication**:
   - Install the `microsoft-authentication-library-for-python` package
   - Configure your app to use Azure AD for authentication
   - Map Azure AD groups to your Django groups

   This approach allows users to login with their existing organizational credentials.

2. **Azure AD B2C**:
   - For external users or organizations
   - Provides features like multi-factor authentication
   - Customizable sign-up/sign-in flows

Setting up Azure AD integration requires additional configuration beyond the scope of this document but provides benefits like centralized user management and enterprise-grade security features.

## Best Practices

1. **Generate Strong Passwords**: Use a password generator for production deployments
2. **Rotate Credentials**: Periodically update all passwords and secrets
3. **Restrict Access**: Use Azure's network security features to restrict admin access
4. **Monitor Login Activity**: Set up logging for authentication events
5. **Use Azure Key Vault**: For highly sensitive applications, store secrets in Azure Key Vault
6. **Regular Audits**: Periodically review user accounts and remove unnecessary access
7. **Multi-Factor Authentication**: Consider implementing MFA for admin accounts

## Troubleshooting

- **Login Issues**: Check if the user exists and is in the correct group
- **Permission Problems**: Verify group permissions are set correctly
- **Environment Variables**: Make sure all required variables are set

## Security Considerations

- The default admin account should be treated as a bootstrap account
- Consider creating individual accounts for each administrator
- Disable or delete default accounts in a production environment after setting up individual accounts
- Use strong, unique passwords for all accounts
