# ASA-Database: Complete Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Installation and Setup](#installation-and-setup)
   - [Local Development Setup](#local-development-setup)
   - [Docker Setup](#docker-setup)
4. [Database Structure](#database-structure)
   - [Key Models](#key-models)
   - [Natural Keys Implementation](#natural-keys-implementation)
   - [Model Relationships](#model-relationships)
5. [Authentication and Authorization](#authentication-and-authorization)
   - [User Roles](#user-roles)
   - [Permissions System](#permissions-system)
   - [Managing Users](#managing-users)
   - [Creating Admin User via Environment Variables](#creating-admin-user-via-environment-variables)
6. [Core Functionality](#core-functionality)
   - [Specimen Management](#specimen-management)
   - [Locality Management](#locality-management)
   - [People Management (Initials)](#people-management-initials)
7. [Data Import/Export](#data-importexport)
   - [Importing Data](#importing-data)
   - [Exporting Data](#exporting-data)
   - [Bulk Operations](#bulk-operations)
8. [User Interface](#user-interface)
   - [Main Dashboard](#main-dashboard)
   - [Form Structure](#form-structure)
   - [Search and Filtering](#search-and-filtering)
9. [Azure Deployment](#azure-deployment)
   - [Prerequisites](#prerequisites)
   - [Environment Configuration](#environment-configuration)
   - [Deployment Steps](#deployment-steps)
   - [Authentication Setup](#authentication-setup)
   - [Database Configuration](#database-configuration)
10. [Troubleshooting](#troubleshooting)
11. [Development Notes](#development-notes)
12. [Future Enhancements](#future-enhancements)

---

## Introduction

ASA-Database is a comprehensive Django web application designed for the Alliance for a Sustainable Amazon (ASA) to manage their butterfly specimen collections. This application follows Darwin Core standards for biodiversity data, enabling researchers and field workers to record, track, and manage detailed information about butterfly specimens collected during field research.

### Key Features

- **Natural Key System**: Uses human-readable natural keys for identification
- **Role-Based Access**: Distinguishes between Admin and Researcher roles
- **Data Import/Export**: Supports CSV and Excel for both import and export
- **Organized Data Collection**: Forms organized by Darwin Core standards
- **Azure Cloud Deployment**: Configured for Microsoft Azure App Services

---

## System Architecture

### Technology Stack

- **Backend**: Django 5.2.4
- **Database**: 
  - Development: SQLite
  - Production: PostgreSQL on Azure
- **Frontend**: HTML, CSS, JavaScript with Django templates
- **Deployment**: Azure App Service

### System Components

- **Core Application**: Django project with butterflies app
- **Authentication**: Django's built-in authentication with custom user management
- **Admin Interface**: Custom admin panel and Django admin
- **Import/Export**: Custom CSV and Excel import/export functionality
- **User Management**: Web-based interface for user administration

---

## Installation and Setup

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Alliance-for-a-Sustainable-Amazon/ASA-Database.git
   cd ASA-Database
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create user groups**:
   ```bash
   python manage.py setup_groups
   ```

6. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

### Docker Setup

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Run migrations inside the container**:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create user groups**:
   ```bash
   docker-compose exec web python manage.py setup_groups
   ```

4. **Create a superuser**:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

---

## Database Structure

### Key Models

1. **Specimen**: The core model for butterfly specimens with catalogNumber as the primary key
   - Format: `YEAR-LOCALITYCODE-SPECIMENNUMBER`
   - Example: `2025-ACEER-123`

2. **Locality**: Represents collection locations with localityCode as the primary key
   - Example: `ACEER` for a specific research station

3. **Initials**: Stores information about collectors, researchers, etc. with initials as the primary key
   - Example: `JDK` for a specific researcher

### Natural Keys Implementation

The system uses natural keys instead of auto-incrementing IDs for better human readability and data portability:

- **Specimen**: catalogNumber (format: YEAR-LOCALITYCODE-SPECIMENNUMBER)
- **Locality**: localityCode 
- **Initials**: initials

### Model Relationships

- **Specimen** → **Locality**: Many specimens can be collected at one locality
- **Specimen** → **Initials**: Multiple relationships for different roles (recordedBy, identifiedBy, georeferencedBy)

---

## Authentication and Authorization

### User Roles

The application implements two main user roles:

1. **Admin**
   - Full access to all features
   - Can add/edit/delete all data types
   - Can manage users
   - Can import/export data
   - Can perform bulk operations
   - Has superuser privileges for Django admin access

2. **Researcher**
   - Limited permissions focused on data entry and viewing
   - Can add/edit specimen records
   - Cannot delete records
   - Cannot add localities or initials
   - Cannot import data or perform bulk operations
   - Cannot manage users

### Permissions System

Permissions are enforced through:

1. **Function Decorators**:
   - `@login_required`: Requires any authenticated user
   - `@admin_required`: Requires admin role

2. **Class-Based View Mixins**:
   - `AdminOrSuperUserRequiredMixin`: For user management views

3. **Template Conditionals**:
   - `{% if user|has_group:'Admin' %}`: For UI elements

### Managing Users

Users are managed through a custom web interface at `/users/`:

- **Listing Users**: View all users with their roles, email, and status
- **Creating Users**: Add new users with specific roles
- **Editing Users**: Update user information and roles
- **Deleting Users**: Remove users from the system

### Creating Admin User via Environment Variables

For automated deployments, an admin user can be created using environment variables:

1. **Required Environment Variables**:
   - `DJANGO_ADMIN_PASSWORD`: (Required) Password for the admin user
   - `DJANGO_ADMIN_USERNAME`: (Optional, defaults to 'admin') Username
   - `DJANGO_ADMIN_EMAIL`: (Optional, defaults to 'admin@example.com') Email

2. **Implementation**:
   ```bash
   # Set environment variables
   export DJANGO_ADMIN_USERNAME=admin
   export DJANGO_ADMIN_EMAIL=admin@example.com
   export DJANGO_ADMIN_PASSWORD=SecurePassword123!
   
   # Run the management command
   python manage.py create_default_admin
   ```

3. **In Azure Deployment**:
   The `azure-deploy.sh` script automatically creates an admin user if the `DJANGO_ADMIN_PASSWORD` environment variable is set.

---

## Core Functionality

### Specimen Management

**Adding Specimens**:
- Navigate to "Add Specimen" in the menu
- Complete the form with required fields
- catalogNumber is auto-generated from year, locality, and specimen number

**Editing Specimens**:
- Find the specimen in the list view or search
- Click "Edit" on the specimen record
- Update information and save

**Form Organization**:
Specimen data is organized into six categories based on Darwin Core:
1. Record-level Information
2. Location Information 
3. Occurrence Information
4. Event Information
5. Taxon Information
6. Identification Information

### Locality Management

**Adding Localities** (Admin only):
- Navigate to "Add Locality" in the admin menu
- Define a unique localityCode and locality information
- Save the locality for use in specimen records

**Managing Localities**:
- List all localities via "All Localities" menu
- Edit or delete localities (Admin only)

### People Management (Initials)

**Adding Initials** (Admin only):
- Navigate to "Add Initials" in the admin menu
- Define initials, name, relationship/title, year/term
- Save for use in specimen records

**Managing Initials**:
- List all initials via "All Initials" menu
- Edit or delete initials entries (Admin only)

---

## Data Import/Export

### Importing Data

**Importing Specimens** (Admin only):
1. Navigate to "All Specimens" → "Import"
2. Upload a CSV or Excel file with specimen data
3. Review the preview screen for duplicates and validation issues
4. Confirm import to create records

**Importing Other Models** (Admin only):
Similar process for localities and initials via their respective list views

**Import Features**:
- Duplicate detection based on natural keys
- Auto-suffixing duplicates (e.g., "ACEER-2" for duplicates)
- Data validation before import
- Foreign key resolution for relationships

### Exporting Data

**Exporting Specimen Reports**:
- From the main dashboard, click "Export to CSV" or "Export to Excel"
- All visible/filtered specimens will be exported

**Exporting Model Data**:
- From any list view, click "Export to CSV" or "Export to Excel"
- All records of that model will be exported

### Bulk Operations

**Bulk Delete** (Admin only):
- Available for specimens via a special debug route
- Requires typing "DELETE" as confirmation
- Double confirmation to prevent accidental data loss

---

## User Interface

### Main Dashboard

The main dashboard shows a table of specimens with:
- Key specimen information
- Quick access to filter and search
- Edit links for each record
- Export buttons for the entire dataset

### Form Structure

Forms are organized with:
- Logical grouping of related fields
- Clear labeling with field numbers matching documentation
- Help text for data format guidance
- Validation feedback for incorrect entries

### Search and Filtering

- **Quick Search**: Search box on dashboard for simple filtering
- **Advanced Filtering**: Filter specimens by locality, collector, date, etc.
- **Model-Specific Search**: Each model list has its own search capabilities

---

## Azure Deployment

### Prerequisites

- Azure account with active subscription
- Azure CLI installed and logged in
- Git installed
- Python 3.8+

### Environment Configuration

**Required Environment Variables**:

| Category | Variable | Description | Example |
|----------|----------|-------------|---------|
| **Basic Settings** | `DJANGO_SECRET_KEY` | Secure secret key | `"a-long-random-string"` |
| | `DJANGO_DEBUG` | Debug mode | `"False"` |
| | `DJANGO_SETTINGS_MODULE` | Settings module | `"research_data_app.settings_azure"` |
| **Database** | `POSTGRES_DATABASE` | Database name | `"asadb"` |
| | `POSTGRES_USER` | Database username | `"username@server"` |
| | `POSTGRES_PASSWORD` | Database password | `"SecurePassword123"` |
| | `POSTGRES_HOST` | Database host | `"server.postgres.database.azure.com"` |
| | `POSTGRES_PORT` | Database port | `"5432"` |
| **Authentication** | `DJANGO_ADMIN_USERNAME` | Admin username | `"admin"` |
| | `DJANGO_ADMIN_EMAIL` | Admin email | `"admin@example.com"` |
| | `DJANGO_ADMIN_PASSWORD` | Admin password | `"SecurePassword123"` |

### Deployment Steps

1. **Create Azure Resources**:
   ```bash
   # Log in to Azure CLI
   az login
   
   # Create a resource group
   az group create --name asa-database-rg --location eastus
   
   # Create an App Service Plan
   az appservice plan create --name asa-database-plan --resource-group asa-database-rg --sku B1 --is-linux
   
   # Create PostgreSQL database
   az postgres flexible-server create --resource-group asa-database-rg --name asa-database-server
   
   # Create a database
   az postgres flexible-server db create --resource-group asa-database-rg --server-name asa-database-server --database-name asadb
   
   # Create a web app
   az webapp create --resource-group asa-database-rg --plan asa-database-plan --name asa-database-app --runtime "PYTHON|3.10"
   ```

2. **Configure Environment Variables**:
   ```bash
   az webapp config appsettings set --resource-group asa-database-rg --name asa-database-app --settings \
     DJANGO_SECRET_KEY="your-secure-secret-key" \
     DJANGO_DEBUG="False" \
     DJANGO_SETTINGS_MODULE="research_data_app.settings_azure" \
     POSTGRES_DATABASE="asadb" \
     POSTGRES_USER="your-db-user@asa-database-server" \
     POSTGRES_PASSWORD="your-db-password" \
     POSTGRES_HOST="asa-database-server.postgres.database.azure.com" \
     POSTGRES_PORT="5432" \
     DJANGO_ADMIN_USERNAME="admin" \
     DJANGO_ADMIN_EMAIL="admin@example.com" \
     DJANGO_ADMIN_PASSWORD="your-admin-password"
   ```

3. **Deploy Code**:
   ```bash
   # Configure local Git deployment
   az webapp deployment source config-local-git --resource-group asa-database-rg --name asa-database-app
   
   # Get deployment URL
   url=$(az webapp deployment list-publishing-profiles --resource-group asa-database-rg --name asa-database-app --query "[?publishMethod=='MSDeploy'].publishUrl" --output tsv)
   
   # Add Azure remote to Git
   git remote add azure $url
   
   # Push to Azure
   git push azure main
   ```

### Authentication Setup

During deployment, the `azure-deploy.sh` script executes these steps:

1. **Database Migration**: Sets up user tables and model schema
2. **Group Creation**: Creates Admin and Researcher groups
3. **Admin User Creation**: Creates an admin user using environment variables
4. **Permission Setup**: Ensures proper permissions for both roles

If `DJANGO_ADMIN_PASSWORD` is not set, admin creation will be skipped.

### Database Configuration

The application uses Azure PostgreSQL Flexible Server for production with:
- Automatic connection pooling
- SSL connection
- Environment-based configuration

---

## Troubleshooting

### Common Issues

**Database Connection Issues**:
- Check PostgreSQL connection string in Azure environment variables
- Ensure firewall settings allow connections from App Service

**Authentication Problems**:
- Verify Admin group exists with `python manage.py shell -c "from django.contrib.auth.models import Group; print(Group.objects.all())"`
- Check if admin user was created using the script in `/update_admin_users.py`

**Form Submission Errors**:
- Check for validation errors in form feedback
- Ensure natural keys follow the expected format

**Import/Export Issues**:
- Verify CSV format matches expected columns
- Check for encoding issues (use UTF-8)

### Logs and Debugging

- **Azure Logs**: Access via Azure Portal → App Service → Logs
- **Local Logs**: Run with `DEBUG=True` in development

---

## Development Notes

### Code Structure

- `butterflies/` - Main app directory
  - `models.py` - Core data models
  - `views.py` - View functions for UI interaction
  - `views_user_management.py` - User management views
  - `forms.py` - Form definitions
  - `admin.py` - Admin interface customization
  - `urls.py` - URL routing configuration
  - `templates/` - HTML templates
  - `static/` - CSS, JS, images
  - `management/commands/` - Custom management commands

- `research_data_app/` - Project settings
  - `settings.py` - Development settings
  - `settings_azure.py` - Production settings for Azure

### Coding Standards

- **PEP 8**: Python style guidelines
- **Django Best Practices**: App organization, view structure
- **Documentation**: Docstrings for all functions and classes

---

## Future Enhancements

- **Advanced Search**: More powerful search capabilities
- **API Integration**: RESTful API for programmatic access
- **Mobile Support**: Responsive design for field use
- **Offline Mode**: Support for data collection without internet
- **Data Visualization**: Charts and maps of specimen distribution
- **Batch Processing**: Improved bulk operations
- **Multi-language Support**: Internationalization
- **2FA Authentication**: Two-factor authentication option
