
# ASA Database

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Installation and Setup](#installation-and-setup)
5. [Database Structure](#database-structure)
6. [Authentication & Authorization](#authentication--authorization)
7. [Core Functionality](#core-functionality)
8. [User Interface](#user-interface)
9. [Internationalization (i18n) & Translation](#internationalization-i18n--translation)
10. [Deployment](#deployment)
11. [Troubleshooting & Maintenance](#troubleshooting--maintenance)
12. [Code Structure](#code-structure)
13. [Documentation & Readme Status](#documentation--readme-status)
14. [Future Enhancements](#future-enhancements)
15. [References](#references)

---

## Project Overview

ASA Database is a Django-based web application for the Alliance for a Sustainable Amazon (ASA) to manage butterfly specimen collections. It follows Darwin Core standards for biodiversity data, supporting researchers and field workers in recording, tracking, and managing specimen information.

---

## Key Features

- **Natural Key System:** Human-readable identifiers for specimens, localities, and people.
- **Role-Based Access:** Admin and Researcher roles with distinct permissions.
- **Data Import/Export:** CSV/Excel support for bulk operations.
- **Organized Data Collection:** Forms structured by Darwin Core standards.
- **Azure Cloud Deployment:** Optimized for Microsoft Azure App Services.
- **Internationalization (i18n):** Global English/Spanish language switch.

---

## System Architecture

### Technology Stack
- **Backend:** Django 5.2.4
- **Database:** SQLite (development), PostgreSQL on Azure (production)
- **Frontend:** HTML, CSS, JavaScript, Django templates
- **Deployment:** Azure App Service, Docker support

### Main Components
- **Core Application:** Django project with `butterflies` app
- **Authentication:** Django auth with custom user management
- **Admin Interface:** Custom admin panel and Django admin
- **Import/Export:** Custom CSV/Excel import/export
- **User Management:** Web interface for user administration

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
- **Specimen:** The core model for butterfly specimens with catalogNumber as the primary key (Format: `YEAR-LOCALITYCODE-SPECIMENNUMBER`, e.g., `2025-ACEER-123`)
- **Locality:** Represents collection locations with localityCode as the primary key (e.g., `ACEER`)
- **Initials:** Stores information about collectors, researchers, etc. with initials as the primary key (e.g., `JDK`)

### Natural Keys Implementation
- Natural keys are used for better human readability and data portability:
  - **Specimen:** catalogNumber
  - **Locality:** localityCode
  - **Initials:** initials

### Model Relationships
- **Specimen** → **Locality:** Many specimens can be collected at one locality
- **Specimen** → **Initials:** Multiple relationships for different roles (recordedBy, identifiedBy, georeferencedBy)

---

## Authentication & Authorization

### User Roles
- **Admin:** Full access to all features, user management, import/export, bulk operations, Django admin access
- **Researcher:** Data entry/viewing, limited permissions

### Permissions System
- Enforced via:
  - Function decorators (`@login_required`, `@admin_required`)
  - Class-based view mixins (`AdminOrSuperUserRequiredMixin`)
  - Template conditionals (`{% if user|has_group:'Admin' %}`)

### Managing Users
- Custom web interface at `/users/` for listing, creating, editing, deleting users

### Creating Admin User via Environment Variables
- Automated admin creation for deployments:
  - `DJANGO_ADMIN_PASSWORD` (required)
  - `DJANGO_ADMIN_USERNAME` (optional, defaults to 'admin')
  - `DJANGO_ADMIN_EMAIL` (optional, defaults to 'admin@example.com')
  - Management command: `python manage.py create_default_admin`
  - Azure deployment script auto-creates admin if password is set

---

## Core Functionality

### Specimen Management
- Add/Edit specimens via forms; catalogNumber auto-generated
- Forms organized by Darwin Core categories:
  1. Record-level Information
  2. Location Information
  3. Occurrence Information
  4. Event Information
  5. Taxon Information
  6. Identification Information

### Locality Management
- Admin-only creation/editing of localities
- List, edit, delete via dedicated views

### People Management (Initials)
- Admin-only creation/editing of initials
- List, edit, delete via dedicated views

---

## Data Import/Export

### Importing Data
- Admin-only import via CSV/Excel with duplicate detection and validation
- Preview screen for duplicates and validation issues
- Auto-suffixing duplicates (e.g., "ACEER-2")
- Foreign key resolution for relationships

### Exporting Data
- Export filtered data to CSV/Excel from dashboards and list views

### Bulk Operations
- Bulk delete for specimens (admin only, double confirmation)

---

## User Interface

- **Dashboard:** Table of specimens, search/filter, edit/export links
- **Forms:** Logical grouping, clear labeling, help text, validation feedback
- **Search/Filtering:** Quick search, advanced filters, model-specific search

---

## Deployment

### Azure
- Prerequisites: Azure account, Azure CLI, Git, Python 3.8+
- Environment variables:
  - `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_SETTINGS_MODULE`, `POSTGRES_DATABASE`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `DJANGO_ADMIN_USERNAME`, `DJANGO_ADMIN_EMAIL`, `DJANGO_ADMIN_PASSWORD`
- Steps:
  1. Create resources (resource group, app service plan, PostgreSQL server, database, web app)
  2. Configure environment variables
  3. Deploy code via Git
  4. Authentication setup: migration, group creation, admin creation, permission setup
- Database: Azure PostgreSQL Flexible Server (connection pooling, SSL, env-based config)

---

## Troubleshooting & Maintenance

- Database connection: Check connection string, firewall settings
- Authentication: Verify groups, admin user creation
- Form errors: Check validation, natural key format
- Import/Export: Verify CSV format, encoding (UTF-8)
- Logs: Azure Portal → App Service → Logs; local logs with `DEBUG=True`
- Migration issues, database resets, deployment errors: See troubleshooting guides and scripts

---

## Code Structure

- `butterflies/`: Main app (models, views, forms, admin, templates, static, management commands)
- `research_data_app/`: Project settings (development and Azure)

### Coding Standards
- **PEP 8**: Python style guidelines
- **Django Best Practices**: App organization, view structure
- **Documentation**: Docstrings for all functions and classes

---

## Internationalization (i18n) & Translation

### System
- Uses Django's built-in i18n system
- All user-facing text uses `{% trans %}` or `{% blocktrans %}` in templates
- Language dropdown in header (in `base.html`) posts to `/i18n/setlang/`
- Selected language persists via cookie (`LANGUAGE_CODE` in templates)
- Translations managed via `.po` files in `locale/` directory

### Workflow
1. Mark text for translation in templates and Python code
2. Extract messages: `python manage.py makemessages -l es`
3. Edit `.po` files for Spanish translations
4. Compile: `python manage.py compilemessages`
5. Test switching via dropdown

### Best Practices
- Always use translation tags for user-facing text
- Do not hardcode language in templates/views
- Keep translations up to date after new features
- Add `{% load i18n %}` in every template with translation tags

### Troubleshooting
- Missing translation: Ensure text is marked and `.po` files are updated/compiled
- Dropdown not persisting: Check `LANGUAGE_CODE` context and middleware
- TemplateSyntaxError: Ensure `{% load i18n %}` is present and tags are correct

### Reference
See `TRANSLATION_GUIDE.md` for full details.

---

## References

- [Django i18n documentation](https://docs.djangoproject.com/en/5.2/topics/i18n/translation/)
- [Django makemessages](https://docs.djangoproject.com/en/5.2/ref/django-admin/#makemessages)
- [Django compilemessages](https://docs.djangoproject.com/en/5.2/ref/django-admin/#compilemessages)
- ASA Database maintainers and official Django documentation