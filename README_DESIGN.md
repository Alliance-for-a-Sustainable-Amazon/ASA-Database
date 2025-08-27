# ASA Database: Comprehensive Design Document

## 1. Project Overview

ASA Database is a Django-based web application for the Alliance for a Sustainable Amazon (ASA) to manage butterfly specimen collections. It follows Darwin Core standards for biodiversity data, supporting researchers and field workers in recording, tracking, and managing specimen information.

### Key Features
- **Natural Key System:** Human-readable identifiers for specimens, localities, and people.
- **Role-Based Access:** Admin and Researcher roles with distinct permissions.
- **Data Import/Export:** CSV/Excel support for bulk operations.
- **Organized Data Collection:** Forms structured by Darwin Core standards.
- **Azure Cloud Deployment:** Optimized for Microsoft Azure App Services.
- **Internationalization (i18n):** Global English/Spanish language switch.

---

## 2. System Architecture

### Technology Stack
- **Backend:** Django 5.2.4
- **Database:** PostgreSQL on Azure (production), PostgreSQL locally (development)
- **Frontend:** HTML, CSS, JavaScript, Django templates
- **Deployment:** Azure App Service

### Main Components
- **Core Application:** Django project with `butterflies` app
- **Authentication:** Django auth with custom user management
- **Admin Interface:** Custom admin panel and Django admin
- **Import/Export:** Custom CSV/Excel import/export
- **User Management:** Web interface for user administration

---

## 3. Database Structure

### Key Models
- **Specimen:** Core model, natural key `catalogNumber` (e.g., `2025-ACEER-123`)
- **Locality:** Collection locations, key `localityCode`
- **Initials:** People (collectors, researchers), key `initials`

### Relationships
- Specimen → Locality: Many-to-one
- Specimen → Initials: Multiple roles (recordedBy, identifiedBy, etc.)

---

## 4. Authentication & Authorization

### Roles
- **Admin:** Full access, user management, import/export, bulk operations
- **Researcher:** Data entry/viewing, limited permissions

### Permissions
- Function decorators (`@login_required`, `@admin_required`)
- Class-based view mixins (`AdminOrSuperUserRequiredMixin`)
- Template conditionals (`{% if user|has_group:'Admin' %}`)

### User Management
- Custom interface at `/users/` for listing, creating, editing, deleting users
- Automated admin creation via environment variables for deployment

---

## 5. Core Functionality

### Specimen Management
- Add/Edit specimens via forms; catalogNumber auto-generated
- Forms organized by Darwin Core categories

### Locality & People Management
- Admin-only creation/editing of localities and initials
- List, edit, delete via dedicated views

### Data Import/Export
- Admin-only import via CSV/Excel with duplicate detection and validation
- Export filtered data to CSV/Excel from dashboards

### Bulk Operations
- Bulk delete for specimens (admin only, double confirmation)

---

## 6. User Interface

- **Dashboard:** Table of specimens, search/filter, edit/export links
- **Forms:** Logical grouping, clear labeling, help text, validation feedback
- **Search/Filtering:** Quick search, advanced filters, model-specific search

---

## 7. Internationalization (i18n) & Translation

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

## 8. Deployment

### Azure
- Scripts and guides for resource creation, environment variable setup, and deployment
- Robust startup and migration scripts for Azure compatibility
- Troubleshooting guides for common Azure issues

### Docker
- Docker Compose setup for local development and testing

---

## 9. Troubleshooting & Maintenance

- Guides for fixing migration issues, database resets, and deployment errors
- Scripts for robust migration and admin setup
- Testing scripts to simulate Azure locally

---

## 10. Code Structure

- `butterflies/`: Main app (models, views, forms, admin, templates, static, management commands)
- `research_data_app/`: Project settings (development and Azure)

## 12. Documentation & Readme Status

### Main Documentation Files
- `ASA_DATABASE_DOCUMENTATION.md`: Up-to-date, main project guide
- `TRANSLATION_GUIDE.md`: Up-to-date, translation/i18n guide
- `AZURE_DEPLOYMENT.md`, `AZURE_TROUBLESHOOTING.md`: Up-to-date, deployment/troubleshooting
- `docs/auth_implementation_summary.md`, `docs/authentication.md`: Current, authentication details
- `butterflies/import_export_info.md`: Current, import/export details

---

## 13. References

- [Django i18n documentation](https://docs.djangoproject.com/en/5.2/topics/i18n/translation/)
- [Django makemessages](https://docs.djangoproject.com/en/5.2/ref/django-admin/#makemessages)
- [Django compilemessages](https://docs.djangoproject.com/en/5.2/ref/django-admin/#compilemessages)
- ASA Database maintainers and official Django documentation

---

**End of Design Document**