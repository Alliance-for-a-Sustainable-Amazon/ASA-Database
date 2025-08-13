# ASA-Database: Butterfly Specimen Management System

## Overview

ASA-Database is a comprehensive Django web application designed for the Alliance for a Sustainable Amazon (ASA) to manage their butterfly specimen collections. This application follows Darwin Core standards for biodiversity data, enabling researchers and field workers to record, track, and manage detailed information about butterfly specimens collected during field research.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation and Setup](#installation-and-setup)
   - [Docker Setup](#docker-setup)
   - [Local Development Setup](#local-development-setup)
3. [Database Structure](#database-structure)
   - [Key Models](#key-models)
   - [Relationships](#relationships)
4. [Core Functionality](#core-functionality)
   - [Specimen Management](#specimen-management)
   - [Locality Management](#locality-management)
   - [People Management (Initials)](#people-management-initials)
   - [Import/Export](#importexport)
5. [User Interface](#user-interface)
   - [Main Dashboard](#main-dashboard)
   - [Form Structure](#form-structure)
   - [Search and Filtering](#search-and-filtering)
   - [Organized Form Layout](#organized-form-layout)
6. [Data Categories](#data-categories)
   - [Record-level Information](#record-level-information)
   - [Location Information](#location-information)
   - [Occurrence Information](#occurrence-information)
   - [Event Information](#event-information)
   - [Taxon Information](#taxon-information)
   - [Identification Information](#identification-information)
7. [Admin Interface](#admin-interface)
8. [Reports and Data Export](#reports-and-data-export)
9. [API Documentation](#api-documentation)
10. [Troubleshooting](#troubleshooting)
11. [Development Notes](#development-notes)
12. [Future Enhancements](#future-enhancements)
13. [Contributing](#contributing)
14. [License](#license)

---

## System Requirements

* Python 3.10+
* Django 4.x
* SQLite3 (development) / PostgreSQL (production)
* Docker and Docker Compose (optional)

---

## Installation and Setup

### Docker Setup

For easy deployment, the application can be run using Docker:

1. Clone the repository:
   ```bash
   git clone https://github.com/Alliance-for-a-Sustainable-Amazon/ASA-Database.git
   cd ASA-Database
   ```

2. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

3. Access the application at `http://localhost:8000`

### Local Development Setup

For local development without Docker:

1. Clone the repository:
   ```bash
   git clone https://github.com/Alliance-for-a-Sustainable-Amazon/ASA-Database.git
   cd ASA-Database
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application at `http://localhost:8000`

For SQLite-based local development, use:
```bash
cd client
bash run_local_sqlite.sh
```

---

## Database Structure

### Key Models

The application is built around these primary models:

1. **Specimen**: The core model that stores all information about butterfly specimens.
2. **Locality**: Geographic locations where specimens were collected.
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

## User Interface

### Main Dashboard

The main interface provides:

- A tabular view of specimens with key information
- Navigation to all major functions
- Quick access to create new entries

### Form Structure

The application uses structured forms that:

- Group related fields together
- Provide clear labeling and help text
- Validate input to ensure data quality
- Support different field types (dropdowns, text areas, date fields)

### Search and Filtering

Users can locate specific records by:

- Filtering by various criteria
- Searching across multiple fields
- Sorting results by different columns

### Organized Form Layout

The forms are organized into logical categories following Darwin Core standards:

- Clean section-based layout
- Collapsible sections for easy navigation
- Consistent formatting and field presentation
- Grayscale color scheme for professional appearance

---

## Data Categories

The application organizes specimen data into six major categories following Darwin Core standards:

### Record-level Information

- Modification history
- Record metadata

### Location Information

- Locality reference
- Geographic coordinates
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

- **CSV exports** of specimen data
- **Filtered reports** based on various criteria
- **Tabular reports** for viewing in the browser

---

## API Documentation

The application includes API endpoints for programmatic access:

- RESTful endpoints for accessing specimen data
- Authentication requirements
- Usage examples

---

## Troubleshooting

Common issues and their solutions:

- **Database connection issues**: Check your database settings in settings.py
- **Missing dependencies**: Run `pip install -r requirements.txt` to ensure all packages are installed
- **Migration errors**: Try resetting migrations with `python manage.py migrate --fake-initial`
- **Form validation errors**: Check the data format against the field requirements

---

## Development Notes

### Project Structure

```
ASA-Database/
├── butterflies/              # Main application
│   ├── admin.py              # Admin interface configuration
│   ├── forms.py              # Form definitions
│   ├── models.py             # Database models
│   ├── views.py              # View functions
│   ├── urls.py               # URL routing
│   ├── templates/            # HTML templates
│   │   └── butterflies/      # App-specific templates
│   └── static/               # Static files (CSS, JS)
│       └── butterflies/      # App-specific static files
├── research_data_app/        # Project settings
├── client/                   # Client-side utilities
├── host/                     # Host deployment utilities
└── manage.py                 # Django management script
```

### Key Files

- **models.py**: Defines the database structure
- **forms.py**: Creates form classes for data entry
- **views.py**: Handles HTTP requests and responses
- **admin.py**: Configures the admin interface
- **forms_organized.py**: Enhanced form layouts
- **views_organized.py**: Enhanced view functionality

## Detailed Feature Documentation

### Specimen Records

#### Creating a New Specimen

1. Navigate to "New Specimen" in the navigation bar
2. Complete the form with the following information:
   - **Record-level**: Modification details
   - **Location**: Locality, coordinates, and elevation
   - **Occurrence**: Specimen number, collector, sex, and disposition
   - **Event**: Collection date, time, and habitat information
   - **Taxon**: Taxonomic classification
   - **Identification**: Identifier and identification details
3. Click "Save" to create the record

#### Editing a Specimen

1. Locate the specimen in the report table
2. Click on the specimen number to open the edit form
3. Make the necessary changes
4. Enter modification details (date, initials, description)
5. Click "Save" to update the record

#### Specimen Disposition Tracking

The system tracks specimen disposition through an append-only history field:

1. Enter the date, initials, and description of the disposition change
2. The history is maintained as a chronological record
3. Each entry follows the format: `DD-MMM-YYYY, initials, description`

### Locality Management

#### Creating a New Locality

1. Navigate to "New Locality" in the navigation bar
2. Enter the locality code and description
3. Provide geographical context information
4. Click "Save" to create the locality

#### Georeferencing

Localities can be georeferenced with:

- Decimal latitude and longitude
- Coordinate uncertainty in meters
- Georeference protocol documentation
- Georeferencer information and date

### Data Import and Export Process

#### Exporting Data

1. Access the data export page
2. Select the desired export format (CSV)
3. Choose filters to limit the exported data (optional)
4. Click "Export" to download the data file

#### Importing Data

1. Prepare a properly formatted CSV file
2. Access the data import page
3. Upload the CSV file
4. Map the CSV columns to database fields
5. Confirm and execute the import

### Field-Specific Features

#### Append-Only Fields

Several fields maintain a history of changes in an append-only format:

- Modified history
- Disposition
- Behavior
- Occurrence remarks
- Habitat notes
- Locality description notes

Each entry follows the format: `DD-MMM-YYYY, initials, description` with entries separated by semicolons.