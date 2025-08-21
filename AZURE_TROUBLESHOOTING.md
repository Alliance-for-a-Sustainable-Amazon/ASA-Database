# Azure Deployment Troubleshooting Guide

## Overview
This document provides information about troubleshooting and fixing common issues with the ASA-Database Azure deployment, particularly when dealing with database resets or fresh deployments.

## Common Issues and Solutions

### 500 Server Errors After Database Reset
If you encounter 500 server errors after resetting the PostgreSQL database, the following issues may be the cause:

1. **Migration Dependency Issues**: When the database is reset, all tables are removed but Django's migration history is lost, causing migration dependency conflicts.

2. **Path and Module Resolution Problems**: Azure App Service may extract files to temporary directories, causing issues with finding the application code.

3. **ALLOWED_HOSTS Configuration**: Internal Azure IP addresses may not be properly configured in the ALLOWED_HOSTS setting.

4. **Foreign Key Type Mismatches**: The `locality_id` field may have incorrect types in different tables.

## Solution Components

### 1. Robust Startup Script
The `startup.sh` script has been enhanced to:
- Find the application directory regardless of where Azure extracts the files
- Set up proper PYTHONPATH to ensure module imports work
- Test if modules can be imported before starting Django
- Handle migrations more robustly with fallback approaches
- Provide detailed logging for troubleshooting

### 2. Fix Migration for Locality Foreign Keys
The `0002_fix_locality_fk_type.py` migration has been created to:
- Ensure the locality table exists with the correct structure
- Fix the `locality_id` foreign key type in the specimen table
- Set up proper foreign key constraints

### 3. Robust Migration Management Command
The `robust_migrate` management command:
- Detects if the database is fresh or existing
- Applies migrations in the correct order for fresh databases
- Handles common migration errors and provides fallback strategies

### 4. User Groups and Default Admin Setup
Commands for:
- Setting up proper user groups and permissions (`setup_groups`)
- Creating a default admin user from environment variables (`create_default_admin`)

### 5. Expanded ALLOWED_HOSTS
The `settings_azure.py` file now includes:
- All common Azure internal IP addresses
- Support for the entire 169.254.0.0/16 subnet used by Azure
- Environment variable support for additional hosts

## Testing the Azure Deployment Locally
A `test_azure_deployment.sh` script has been added to simulate the Azure environment locally before deploying:
- Creates a temporary directory to mimic Azure's file extraction
- Sets up environment variables similar to Azure
- Runs the startup script in the test environment

## Deployment Checklist

When deploying to Azure:
1. Ensure environment variables are properly set in Azure App Service:
   - `POSTGRES_DATABASE`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`
   - `DJANGO_ADMIN_PASSWORD` if you want a default admin user created
   - `DJANGO_SETTINGS_MODULE=research_data_app.settings_azure`

2. If you reset the database, be aware that you may need to:
   - Monitor startup logs for any migration issues
   - Check if all required tables were created successfully
   - Verify that user groups and permissions are set up correctly

3. Always test locally with `test_azure_deployment.sh` before deploying to Azure

## Troubleshooting

If issues persist:
1. Check the Azure App Service logs for detailed error messages
2. Verify that the PostgreSQL connection is working correctly
3. Try running migrations manually through the Azure console
4. Consider deploying with `DEBUG=True` temporarily to see detailed error pages
