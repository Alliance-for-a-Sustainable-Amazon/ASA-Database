# Organized Specimen Form

This is an alternative form layout for the Butterfly Specimen database that organizes fields into logical categories.

## Features

- Fields are grouped into categories for easier data entry
- Categories can be collapsed/expanded for a cleaner interface
- Same functionality as the original form with improved organization
- Grid layout for better use of screen space

## Categories

1. **Record-level**
   - modified (Modification History)

2. **Location**
   - locality
   - decimalLatitude
   - decimalLongitude
   - exact_loc
   - coordinateUncertaintyInMeters
   - georeferencedBy
   - georeferencedDate
   - georeferenceProtocol
   - minimumElevationInMeters
   - maximumElevationInMeters

3. **Occurrence**
   - specimenNumber
   - recordedBy
   - sex
   - behavior
   - occurrenceRemarks
   - disposition

4. **Event**
   - year
   - month
   - day
   - eventTime
   - habitatNotes
   - samplingProtocol

5. **Taxon**
   - family
   - subfamily
   - tribe
   - subtribe
   - genus
   - specificEpithet
   - infraspecificEpithet

6. **Identification**
   - identifiedBy
   - dateIdentified
   - identificationReferences
   - identificationRemarks

## How to Access

You can access the organized form in two ways:

1. From the navigation bar: Click on "New Specimen (Organized)"
2. Directly via URL: `/butterflies/specimen/add/organized/`

For editing existing records with the organized form, use:
`/butterflies/edit/organized/specimen/<id>/`

## Implementation Details

The organized form is implemented as an alternative template and view, which means:

1. No changes to the core form functionality or database structure
2. You can switch between the original and organized layouts as needed
3. All form validation and processing remains the same

Files involved:
- `_form_organized.html` - Template with categorized layout
- `views_organized.py` - Alternative views for the organized form
- URLs registered in `urls.py` under the `organized` paths

## Future Improvements

- Add user preference to choose between original and organized layouts
- Add color coding for different categories
- Persist section collapse/expand state between page loads
