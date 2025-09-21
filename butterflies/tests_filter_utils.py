"""
Tests for the filter_utils module.
"""

from django.test import TestCase
from django.db.models import Q
from butterflies.filter_utils import FilterBuilder, apply_model_filters
from butterflies.models import Specimen, Locality
from django.http import HttpRequest


class FilterBuilderTests(TestCase):
    """
    Test cases for the FilterBuilder class.
    """
    
    def setUp(self):
        """Set up test data."""
        # Create some localities
        self.locality1 = Locality.objects.create(
            localityCode="LOC1",
            country="Country 1",
            stateProvince="State 1"
        )
        self.locality2 = Locality.objects.create(
            localityCode="LOC2",
            country="Country 2",
            stateProvince="State 2"
        )
        
        # Create some specimens with different numbers
        self.specimen1 = Specimen.objects.create(
            catalogNumber="2023-AA-0001",
            specimenNumber="1",
            year="2023",
            locality=self.locality1
        )
        self.specimen2 = Specimen.objects.create(
            catalogNumber="2023-AA-0002",
            specimenNumber="2",
            year="2023",
            locality=self.locality1
        )
        self.specimen3 = Specimen.objects.create(
            catalogNumber="2023-AA-0003",
            specimenNumber="3",
            year="2023",
            locality=self.locality1
        )
        self.specimen10 = Specimen.objects.create(
            catalogNumber="2023-AA-0010",
            specimenNumber="10",
            year="2023",
            locality=self.locality2
        )
        self.specimen11 = Specimen.objects.create(
            catalogNumber="2023-AA-0011",
            specimenNumber="11",
            year="2023",
            locality=self.locality2
        )
        self.specimen20 = Specimen.objects.create(
            catalogNumber="2022-AA-0020",
            specimenNumber="20",
            year="2022",
            locality=self.locality2
        )
    
    def test_parse_filter_basic(self):
        """Test basic filter parsing."""
        q = FilterBuilder.parse_filter('year', '2023')
        specimens = Specimen.objects.filter(q)
        self.assertEqual(specimens.count(), 5)
        self.assertIn(self.specimen1, specimens)
        self.assertIn(self.specimen10, specimens)
        self.assertNotIn(self.specimen20, specimens)
    
    def test_parse_filter_range(self):
        """Test range filter parsing."""
        q = FilterBuilder.parse_filter('specimenNumber', '1:3', range_support=True)
        specimens = Specimen.objects.filter(q)
        self.assertEqual(specimens.count(), 3)
        self.assertIn(self.specimen1, specimens)
        self.assertIn(self.specimen2, specimens)
        self.assertIn(self.specimen3, specimens)
        self.assertNotIn(self.specimen10, specimens)
        self.assertNotIn(self.specimen11, specimens)
    
    def test_parse_filter_comma_separated(self):
        """Test comma-separated filter parsing."""
        q = FilterBuilder.parse_filter('specimenNumber', '1, 10, 20', range_support=False)
        specimens = Specimen.objects.filter(q)
        self.assertEqual(specimens.count(), 3)
        self.assertIn(self.specimen1, specimens)
        self.assertIn(self.specimen10, specimens)
        self.assertIn(self.specimen20, specimens)
    
    def test_parse_filter_complex(self):
        """Test complex filter parsing with ranges and comma-separated values."""
        q = FilterBuilder.parse_filter('specimenNumber', '1:3, 20', range_support=True)
        specimens = Specimen.objects.filter(q)
        self.assertEqual(specimens.count(), 4)
        self.assertIn(self.specimen1, specimens)
        self.assertIn(self.specimen2, specimens)
        self.assertIn(self.specimen3, specimens)
        self.assertIn(self.specimen20, specimens)
        self.assertNotIn(self.specimen10, specimens)
    
    def test_extract_year_values(self):
        """Test extracting year values."""
        years = FilterBuilder.extract_year_values('2022, 2023:2025')
        self.assertIn('2022', years)
        self.assertIn('2023', years)
        self.assertIn('2024', years)
        self.assertIn('2025', years)
        self.assertEqual(len(years), 4)
    
    def test_get_catalog_number_by_year_filter(self):
        """Test filtering catalog numbers by year."""
        q = FilterBuilder.get_catalog_number_by_year_filter('2022')
        specimens = Specimen.objects.filter(q)
        self.assertEqual(specimens.count(), 1)
        self.assertIn(self.specimen20, specimens)
    
    def test_apply_model_filters(self):
        """Test applying model filters."""
        request = HttpRequest()
        request.GET = {'specimenNumber': '1:3'}
        
        special_filters = {
            'specimenNumber': {'field': 'specimenNumber', 'range_support': True}
        }
        
        queryset = Specimen.objects.all()
        filtered = apply_model_filters(queryset, Specimen, request, special_filters)
        
        self.assertEqual(filtered.count(), 3)
        self.assertIn(self.specimen1, filtered)
        self.assertIn(self.specimen2, filtered)
        self.assertIn(self.specimen3, filtered)
        self.assertNotIn(self.specimen10, filtered)
    
    def test_numeric_ordering(self):
        """Test numeric ordering of specimen numbers."""
        specimens = Specimen.objects.all().order_by('specimenNumber')
        specimens_list = list(specimens)
        
        # Without proper numeric sorting, '10' would come before '2'
        # With our numeric sorting, the order should be 1, 2, 3, 10, 11, 20
        ordered_ids = [s.id for s in specimens_list]
        expected_order = [
            self.specimen1.id,
            self.specimen2.id, 
            self.specimen3.id,
            self.specimen10.id,
            self.specimen11.id,
            self.specimen20.id
        ]
        
        # Apply the annotations from filter_utils
        from django.db.models import F
        from django.db.models.functions import Cast
        from django.db.models import IntegerField
        
        specimens = Specimen.objects.all().annotate(
            specimenNumber_as_int=Cast('specimenNumber', output_field=IntegerField())
        ).order_by('specimenNumber_as_int')
        
        specimens_list = list(specimens)
        ordered_ids_with_annotation = [s.id for s in specimens_list]
        
        # This should match our expected order
        self.assertEqual(ordered_ids_with_annotation, expected_order)
