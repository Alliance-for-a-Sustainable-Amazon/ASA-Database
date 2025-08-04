# Import/Export System Documentation

## Overview
The ASA-Database implements a generic import/export system that works with any model in the butterflies app. The system supports both CSV and Excel formats for both importing and exporting data.

## Key Features

### Generic Export
- Export any model to CSV or Excel format
- URL pattern: `/<model_name>/export/csv/` or `/<model_name>/export/excel/`
- Functions: `export_model_csv()` and `export_model_excel()`

### Report Table Export
- Export the full report table (specimens with related data) to CSV or Excel
- URL pattern: `/report/export/csv/` or `/report/export/excel/`
- Functions: `export_report_csv()` and `export_report_excel()`

### Generic Import
- Import data from CSV or Excel to any model
- URL pattern: `/<model_name>/import/`
- Function: `import_model()`
- Features:
  - Duplicate detection based on unique fields
  - Auto-numbering for duplicates (e.g., "ABC123-2" for duplicates)
  - Preview before import
  - Validation of required fields

## Templates

- `import_model.html` - Generic file upload form for any model
- `import_model_preview.html` - Preview and confirm imported data before saving

## Deprecated Templates (Retained for Reference)

- `import_locality.html` - Legacy template, no longer used
- `import_locality_preview.html` - Legacy template, no longer used

## Working with the Import/Export System

### Adding Export to a View

```python
from django.urls import reverse

context = {
    # ... other context variables
    'export_csv_url': reverse('export_model_csv', args=['your_model_name']),
    'export_excel_url': reverse('export_model_excel', args=['your_model_name']),
    'import_url': reverse('import_model', args=['your_model_name']),
}
```

### Adding Import/Export Buttons to a Template

```html
<div>
  <a href="{% url 'export_model_csv' model_name_internal %}">Export CSV</a>
  <a href="{% url 'export_model_excel' model_name_internal %}">Export Excel</a>
  <a href="{% url 'import_model' model_name_internal %}">Import Data</a>
</div>
```
