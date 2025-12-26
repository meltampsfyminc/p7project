from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date

from .models import Building, BuildingYearlyRecord


class BuildingModelTests(TestCase):
    """Test Building model"""
    
    def test_building_creation(self):
        """Test creating a building"""
        building = Building.objects.create(
            code='A',
            name='KAPILYA',
            classification='A-3',
            is_donated=True,
            original_cost=Decimal('1897535.51'),
            current_total_cost=Decimal('1897535.51'),
            year_covered=2024,
        )
        self.assertEqual(building.code, 'A')
        self.assertEqual(str(building), 'A - KAPILYA')
        self.assertEqual(building.get_donation_status(), 'HANDOG')
    
    def test_building_not_donated(self):
        """Test building donation status for non-donated building"""
        building = Building.objects.create(
            code='D',
            name='GUARD HOUSE',
            is_donated=False,
            current_total_cost=Decimal('12004.80'),
            year_covered=2024,
        )
        self.assertEqual(building.get_donation_status(), 'HINDI HANDOG')


class BuildingYearlyRecordTests(TestCase):
    """Test BuildingYearlyRecord model"""
    
    def setUp(self):
        """Create test building"""
        self.building = Building.objects.create(
            code='A',
            name='Test Building',
            current_total_cost=Decimal('100000'),
            year_covered=2024,
        )
    
    def test_yearly_record_creation(self):
        """Test creating a yearly record"""
        record = BuildingYearlyRecord.objects.create(
            building=self.building,
            year=2024,
            cost_last_year=Decimal('100000'),
        )
        self.assertEqual(record.year, 2024)
        self.assertEqual(str(record), 'Test Building - 2024')
    
    def test_total_added_calculation(self):
        """Test auto-calculation of total added"""
        record = BuildingYearlyRecord.objects.create(
            building=self.building,
            year=2024,
            cost_last_year=Decimal('100000'),
            construction_cost=Decimal('10000'),
            renovation_cost=Decimal('5000'),
            general_repair_cost=Decimal('2000'),
            other_additions_cost=Decimal('1000'),
        )
        # total_added should be auto-calculated on save
        self.assertEqual(record.total_added, Decimal('18000'))
    
    def test_year_end_total_calculation(self):
        """Test auto-calculation of year-end total"""
        record = BuildingYearlyRecord.objects.create(
            building=self.building,
            year=2024,
            cost_last_year=Decimal('100000'),
            construction_cost=Decimal('10000'),
            broken_removed_cost=Decimal('5000'),
        )
        # year_end_total = cost_last_year + total_added - broken_removed_cost
        # = 100000 + 10000 - 5000 = 105000
        self.assertEqual(record.year_end_total, Decimal('105000'))
    
    def test_unique_together_constraint(self):
        """Test that building-year combination is unique"""
        BuildingYearlyRecord.objects.create(
            building=self.building,
            year=2024,
            cost_last_year=Decimal('100000'),
        )
        
        # Attempting to create another record for same building and year should fail
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            BuildingYearlyRecord.objects.create(
                building=self.building,
                year=2024,
                cost_last_year=Decimal('200000'),
            )
