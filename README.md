# ASA-Database: Butterfly Specimen Management System

## Overview

ASA-Database is a comprehensive Django web application designed for the Alliance for a Sustainable Amazon (ASA) to manage their butterfly specimen collections. This application follows Darwin Core standards for biodiversity data, enabling researchers and field workers to record, track, and manage detailed information about butterfly specimens collected during field research.

## Documentation

**Comprehensive documentation** is available in [ASA_DATABASE_DOCUMENTATION.md](ASA_DATABASE_DOCUMENTATION.md)

## Quick Start

### Docker Setup

For easy deployment, the application can be run using Docker:

```bash
# Clone the repository
git clone https://github.com/Alliance-for-a-Sustainable-Amazon/ASA-Database.git
cd ASA-Database

# Build and start the containers
docker-compose up -d

# Run migrations and create user groups
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py setup_groups

# Create an admin user
docker-compose exec web python manage.py createsuperuser
```

Access the application at `http://localhost:8000`

### Local Development Setup

For local development without Docker:

```bash
# Clone the repository
git clone https://github.com/Alliance-for-a-Sustainable-Amazon/ASA-Database.git
cd ASA-Database

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and create user groups
python manage.py migrate
python manage.py setup_groups

# Create an admin user
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Access the application at `http://localhost:8000`

### Azure Deployment

For Azure deployment instructions, refer to the [comprehensive documentation](ASA_DATABASE_DOCUMENTATION.md#azure-deployment).

## Key Features

- **Natural Key System**: Uses human-readable natural keys for identification
- **Role-Based Access**: Distinguishes between Admin and Researcher roles
- **Data Import/Export**: Supports CSV and Excel for both import and export
- **Organized Data Collection**: Forms organized by Darwin Core standards
- **Azure Cloud Deployment**: Configured for Microsoft Azure App Services

## License

This project is licensed under the terms of the MIT license.


3. **Initials**: Researchers and collectors who work with the specimens.

### Relationships

- Each **Specimen** is linked to a **Locality** (where it was found)
- Each **Specimen** is linked to various **Initials** records representing different roles (collector, identifier, etc.)
- History tracking fields use a standardized format for maintaining modification records

---

## Core Functionality

### Specimen Management

The application provides comprehensive tools for managing butterfly specimens:

- **Create new specimens** with detailed taxonomic, location, and collection information
- **Edit existing specimens** with full audit trail of changes
- **View specimen details** in various formats
- **Track specimen disposition** as they move through the research process
- **Link specimens** to localities, collectors, and identifiers

### Locality Management

Manage the geographic locations where specimens were collected:

- **Create and edit localities** with detailed information
- **Georeference** locations with latitude, longitude, and precision data
- **Track uncertainty** in geographic coordinates
- **Record elevation** information

### People Management (Initials)

Track and manage people involved in the collection and identification process:

- **Maintain a database of researchers** with their initials as unique identifiers
- **Associate people** with specimens in various roles
- **Track contributions** to the specimen collection process

### Import/Export

The system supports importing and exporting data:

- **Export data** in CSV format for use in other systems
- **Import data** from structured formats
- **Backup and restore** functionality

---


- Coordinate uncertainty
- Elevation data
- Georeferencing information

### Occurrence Information

- Specimen numbering
- Recorder information
- Sex determination
- Behavioral observations
- Specimen disposition tracking

### Event Information

- Collection date (year, month, day)
- Collection time
- Habitat notes
- Sampling protocol information

### Taxon Information

- Taxonomic hierarchy (family, subfamily, tribe, etc.)
- Genus and species information
- Infraspecific taxonomic details

### Identification Information

- Identifier information
- Identification date
- Reference materials used
- Identification remarks

---

## Admin Interface

The Django admin interface provides advanced management capabilities:

- **User management** for controlling access
- **Bulk operations** for efficient data handling
- **Advanced filtering** options
- **Import/export** functionality
- **Data validation** and integrity checks

---

## Reports and Data Export

Generate reports and export data:

