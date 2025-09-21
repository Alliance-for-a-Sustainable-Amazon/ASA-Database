# Standardized Filtering System

This document describes the standardized filtering system implemented in the ASA-Database project.

## Overview

The filtering system provides a consistent way to filter records in the database across all models. It includes the following features:

- Text filtering with exact matches and case-insensitive contains
- Numeric range filtering (e.g., "1:100")
- Comma-separated values (e.g., "A, B, C")
- Combined ranges and comma-separated values (e.g., "1:3, 5:10, 15")
- Special handling for certain fields like catalog numbers and specimen numbers

## Key Components

### 1. Filter Utilities (`filter_utils.py`)

- `FilterBuilder` class: Constructs complex filter queries for the ORM
- `apply_model_filters()`: Core function that applies filters to a queryset

### 2. Template Tags

- `filter_tags.py`: Tags for rendering filter fields with proper UI
- `form_utils.py`: Form-related utilities for filter forms
- `query_utils.py`: Query string manipulation utilities

### 3. Templates

- `includes/_filter_form.html`: Reusable filter form template with major filters visible and other filters in a dropdown
- `_table.html`: Clean table display without integrated search functionality
- `_pagination.html`: Pagination with query string preservation

## Using the Filter System

### Special Filters

Special filters like specimen number, catalog number, and year have extended support:

1. **Range Filtering**:
   - Format: `start:end`
   - Example: `1:3` for specimen numbers 1, 2, and 3
   - Example: `2020:2023` for years 2020, 2021, 2022, and 2023
   
2. **Comma-separated Values**:
   - Format: `value1, value2, value3`
   - Example: `2020, 2022, 2023` for specific years
   
3. **Combined Format**:
   - Format: `range1, range2, value`
   - Example: `1:3, 5:10, 15` for specimen numbers 1-3, 5-10, and 15

### Standard Filters

All other model fields support standard filtering with case-insensitive contains matching.

## Extending the System

To add a new special filter:

1. Update the `special_filters` dictionary in `apply_model_filters()` function
2. Add appropriate UI elements in the templates
3. Update the documentation

## Query String Manipulation

The system includes template tags for manipulating query strings:

- `update_query_params`: Update a parameter in the query string
- `remove_query_param`: Remove a parameter from the query string
- `preserve_query_params`: Generate hidden inputs for query parameters

## Numeric Sorting

The system includes proper numeric sorting for fields stored as strings:
- Year values are converted to integers for sorting
- Specimen numbers are converted to integers for sorting

## UI Considerations

The filter UI is designed to be user-friendly with:
- Clear labels and placeholders
- Help text explaining filter syntax
- Major filters (specimen number, catalog number, locality, year) displayed prominently
- Advanced filters hidden in a collapsible panel with clear toggle button
- Visual indicators for expanded/collapsed state of advanced filters
- Visual indicators for active filters
- One-click removal of individual filters
