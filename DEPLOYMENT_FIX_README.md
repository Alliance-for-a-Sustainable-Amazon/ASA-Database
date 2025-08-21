# ASA Database Deployment Fix

## Recent Changes

We've implemented several fixes to address the deployment issues with the ASA Database application on Azure:

1. **Modified migration strategy**: The startup script now handles migrations more robustly, detecting fresh databases and applying migrations in the correct order.

2. **Added ALLOWED_HOSTS**: Updated the settings to include all possible Azure internal IPs, fixing the DisallowedHost errors.

3. **Created migration fix**: Added a new migration (0002_fix_locality_fk_type.py) to ensure proper foreign key types while maintaining compatibility with your current migration state.

4. **Enhanced error handling**: The startup script now continues past errors and provides helpful log messages.

## Deployment Process

When deploying to Azure App Service:

1. Make sure these environment variables are correctly set in Azure App Service Configuration:
   - DJANGO_SETTINGS_MODULE=research_data_app.settings_azure
   - POSTGRES_DATABASE
   - POSTGRES_USER
   - POSTGRES_PASSWORD
   - POSTGRES_HOST
   - POSTGRES_PORT
   - DJANGO_SECRET_KEY
   - DJANGO_ADMIN_PASSWORD (optional, for creating default admin)

2. Deploy the application code with the updated startup.sh script.

3. If the database is completely fresh (no tables), the startup script will:
   - Apply Django's core migrations first (auth, admin, contenttypes, sessions)
   - Apply the butterflies 0001_initial migration with --fake-initial
   - Apply the new fix migration for locality foreign key types
   - Apply any remaining migrations

4. If the database already has tables, it will attempt a standard migration approach.

## Troubleshooting

If you encounter further migration issues:

1. Check the application logs in the Azure portal for specific error messages.

2. Consider resetting the database completely and letting the startup script handle initialization from scratch.

3. You may need to manually connect to the PostgreSQL database and verify the migration state in the django_migrations table.
