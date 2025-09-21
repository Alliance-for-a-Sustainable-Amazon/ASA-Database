"""
Filter utilities for the butterflies app.

This module provides standardized filtering capabilities for all models, with special 
handling for range queries and comma-separated values.

Filter Types Supported:
1. Basic text filters (contains, exact match)
2. Numeric range filters (e.g., "1:100")
3. Comma-separated values (e.g., "A, B, C")
4. Combination of ranges and comma-separated values (e.g., "1:3, 5:10, 15")
"""

from django.db.models import Q, F, Value, CharField, IntegerField, Case, When


class FilterBuilder:
    """
    A utility class for building complex Django ORM filters.
    
    Provides standardized methods for filtering models with support for:
    - Text matching (exact, contains)
    - Numeric ranges with proper integer conversion
    - Comma-separated values
    - Special field handling (catalog numbers, specimen numbers, etc.)
    """
    
    @staticmethod
    def parse_filter(field_name, value, range_support=False):
        """
        Parse a filter value and return a Q object for filtering.
        
        Args:
            field_name (str): The name of the field to filter on
            value (str): The filter value to parse
            range_support (bool): Whether to support range queries with colon separator
            
        Returns:
            Q: A Django Q object representing the filter
        """
        if not value or not value.strip() or not field_name:
            return Q()
        
        # Split by commas to handle multiple values
        parts = [p.strip() for p in value.split(',')]
        combined_q = Q()
        
        for part in parts:
            # Check if it's a range query
            if ':' in part and range_support:
                try:
                    # Handle catalog number ranges (e.g., 2023-KL-0010:0200)
                    if '-' in part and field_name == 'catalogNumber':
                        # Split into base and range part
                        prefix_part, range_part = part.rsplit('-', 1)
                        prefix = prefix_part + '-'  # e.g., "2023-KL-"
                        
                        start_num, end_num = range_part.split(':')
                        
                        # Ensure both have same length by padding with zeros
                        max_len = max(len(start_num), len(end_num))
                        start_padded = start_num.zfill(max_len)
                        end_padded = end_num.zfill(max_len)
                        
                        # Create range query for catalog numbers
                        range_q = Q()
                        range_q &= Q(catalogNumber__regex=f'^{prefix}[0-9]+$')
                        range_q &= Q(catalogNumber__gte=f"{prefix}{start_padded}")
                        range_q &= Q(catalogNumber__lte=f"{prefix}{end_padded}")
                        
                        combined_q |= range_q
                    
                    # For numeric fields (e.g., years 2020:2025 or specimen numbers 1:100)
                    else:
                        start_val, end_val = part.split(':')
                        start_val = start_val.strip()
                        end_val = end_val.strip()
                        
                        # For numeric fields like year and specimenNumber
                        if field_name in ['year', 'specimenNumber']:
                            try:
                                start_int = int(start_val)
                                end_int = int(end_val)
                                # Create explicit list of values in the range
                                for val in range(start_int, end_int + 1):
                                    combined_q |= Q(**{f"{field_name}": str(val)})
                            except ValueError:
                                # Fall back to string comparison if conversion fails
                                range_q = Q()
                                range_q &= Q(**{f"{field_name}__gte": start_val})
                                range_q &= Q(**{f"{field_name}__lte": end_val})
                                combined_q |= range_q
                        else:
                            # String comparison for other fields
                            range_q = Q()
                            range_q &= Q(**{f"{field_name}__gte": start_val})
                            range_q &= Q(**{f"{field_name}__lte": end_val})
                            combined_q |= range_q
                except (ValueError, IndexError):
                    # Fall back to contains search if parsing fails
                    combined_q |= Q(**{f"{field_name}__icontains": part})
            else:
                # Simple exact match for a single value
                combined_q |= Q(**{f"{field_name}__iexact": part})
        
        return combined_q
    
    @staticmethod
    def extract_year_values(year_filter):
        """
        Extract all individual years from a year filter string,
        handling ranges and comma-separated values.
        
        Args:
            year_filter (str): Year filter string (e.g., "2020, 2022:2025")
            
        Returns:
            list: List of individual year strings
        """
        if not year_filter or not year_filter.strip():
            return []
            
        all_years = []
        year_parts = [p.strip() for p in year_filter.split(',')]
        
        for part in year_parts:
            if ':' in part:
                try:
                    start_val, end_val = [p.strip() for p in part.split(':')]
                    start_int = int(start_val)
                    end_int = int(end_val)
                    all_years.extend([str(y) for y in range(start_int, end_int + 1)])
                except (ValueError, TypeError):
                    all_years.append(part)  # If conversion fails, use as-is
            else:
                all_years.append(part)
        
        return all_years
    
    @staticmethod
    def get_catalog_number_by_year_filter(year_filter):
        """
        Create a Q object to filter catalog numbers that start with any
        of the years in the year filter.
        
        Args:
            year_filter (str): Year filter string (e.g., "2020, 2022:2025")
            
        Returns:
            Q: Django Q object for filtering catalog numbers by year
        """
        all_years = FilterBuilder.extract_year_values(year_filter)
        
        year_q = Q()
        for year in all_years:
            year_q |= Q(catalogNumber__startswith=year)
            
        return year_q
    
    @staticmethod
    def create_annotation_for_numeric_sorting(field_name):
        """
        Create a Case/When expression for proper numeric sorting of string fields.
        
        Args:
            field_name (str): The name of the field to convert
            
        Returns:
            dict: Dictionary with the annotation expression
        """
        return {
            f"{field_name}_as_int": Case(
                When(**{f"{field_name}__regex": r'^\d+$'}, then=F(field_name)),
                default=Value('0'),
                output_field=CharField(),
                _connector='AND'
            )
        }


def apply_model_filters(queryset, model, request, special_filters=None):
    """
    Apply filters to a queryset based on request parameters.
    
    Args:
        queryset: Base queryset to filter
        model: Django model class
        request: HTTP request with filter parameters
        special_filters: Dictionary of special filter configurations
        
    Returns:
        queryset: Filtered queryset
    """
    from django.db.models.functions import Cast
    
    # Initialize special filters if not provided
    if special_filters is None and model.__name__ == 'Specimen':
        special_filters = {
            'catalogNumber': {'field': 'catalogNumber', 'range_support': True},
            'locality': {'field': 'locality__localityCode', 'range_support': False},
            'specimenNumber': {'field': 'specimenNumber', 'range_support': True},
            'year': {'field': 'year', 'range_support': True}
        }
    
    # Apply special filters first if any
    if special_filters:
        for filter_key, config in special_filters.items():
            filter_value = request.GET.get(filter_key)
            if filter_value and filter_value.strip():
                # Apply the main filter
                filter_q = FilterBuilder.parse_filter(
                    config['field'], 
                    filter_value, 
                    range_support=config['range_support']
                )
                queryset = queryset.filter(filter_q)
                
                # Special handling for year filter - match catalog numbers
                if filter_key == 'year':
                    year_q = FilterBuilder.get_catalog_number_by_year_filter(filter_value)
                    queryset = queryset.filter(year_q)
    
    # Apply standard filters for all other fields
    fields = [field for field in model._meta.fields if field.name != 'id']
    
    for field in fields:
        # Skip fields that have already been handled by special filters
        if special_filters and field.name in special_filters:
            continue
            
        value = request.GET.get(field.name)
        if value and value.strip():
            # Handle foreign key fields
            if field.is_relation:
                try:
                    # Try exact match first
                    queryset = queryset.filter(**{field.name: value})
                except (ValueError, model.DoesNotExist):
                    # If exact match fails, try related objects
                    related_model = field.related_model
                    pk_field = related_model._meta.pk.name
                    
                    # Find related objects containing the search term
                    related_objects = related_model.objects.filter(**{f"{pk_field}__icontains": value})
                    if related_objects.exists():
                        queryset = queryset.filter(**{f"{field.name}__in": related_objects})
                    else:
                        # No matches - return empty queryset
                        return queryset.none()
            else:
                # Standard field filtering - use contains for better usability
                queryset = queryset.filter(**{f"{field.name}__icontains": value})
    
    # Apply annotations for numeric sorting (if it's a Specimen model)
    if model.__name__ == 'Specimen':
        numeric_annotations = {}
        
        # Annotate year as integer for sorting
        year_annotation = FilterBuilder.create_annotation_for_numeric_sorting('year')
        numeric_annotations.update(year_annotation)
        
        # Annotate specimenNumber as integer for sorting
        specimen_annotation = FilterBuilder.create_annotation_for_numeric_sorting('specimenNumber')
        numeric_annotations.update(specimen_annotation)
        
        queryset = queryset.annotate(**numeric_annotations)
        
        # Cast annotations to integers
        queryset = queryset.annotate(
            year_as_int=Cast('year_as_int', output_field=IntegerField()),
            specimenNumber_as_int=Cast('specimenNumber_as_int', output_field=IntegerField())
        )
        
        # Apply default ordering
        queryset = queryset.order_by(
            'year_as_int',
            'specimenNumber_as_int',
            F('eventDate').asc(nulls_last=True),
            'month', 'day'
        )
    
    return queryset
