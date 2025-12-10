from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from properties.models import Property, HousingUnit, PropertyInventory
from datetime import date


class Command(BaseCommand):
    help = 'Seed the database with sample property and housing unit data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))
        
        # Create Abra Building/Property
        abra_property, created = Property.objects.get_or_create(
            name='Abra Building',
            defaults={
                'description': 'Historic church building with multiple housing units',
                'owner': 'The Church',
                'address': '123 Main Street',
                'city': 'Manila',
                'province': 'Metro Manila',
                'postal_code': '1000',
                'property_type': 'Building',
                'status': 'active',
                'total_units': 5,
                'acquisition_cost': Decimal('5000000.00'),
                'current_value': Decimal('5500000.00'),
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created Property: {abra_property.name}'))
        else:
            self.stdout.write(self.style.WARNING(f'✓ Property already exists: {abra_property.name}'))
        
        # Create sample housing units
        units_data = [
            {
                'unit_number': '101',
                'floor': '1',
                'housing_unit_name': 'Unit 101',
                'address': '123 Main Street, Unit 101',
                'occupant_name': 'John Doe',
                'department': 'Operations',
                'section': 'Finance',
                'job_title': 'Manager',
            },
            {
                'unit_number': '102',
                'floor': '1',
                'housing_unit_name': 'Unit 102',
                'address': '123 Main Street, Unit 102',
                'occupant_name': 'Jane Smith',
                'department': 'Administration',
                'section': 'Human Resources',
                'job_title': 'Coordinator',
            },
            {
                'unit_number': '201',
                'floor': '2',
                'housing_unit_name': 'Unit 201',
                'address': '123 Main Street, Unit 201',
                'occupant_name': 'Robert Johnson',
                'department': 'Maintenance',
                'section': 'Building Services',
                'job_title': 'Supervisor',
            },
            {
                'unit_number': '202',
                'floor': '2',
                'housing_unit_name': 'Unit 202',
                'address': '123 Main Street, Unit 202',
                'occupant_name': 'Maria Garcia',
                'department': 'Finance',
                'section': 'Accounting',
                'job_title': 'Accountant',
            },
            {
                'unit_number': '301',
                'floor': '3',
                'housing_unit_name': 'Unit 301',
                'address': '123 Main Street, Unit 301',
                'occupant_name': 'David Lee',
                'department': 'Operations',
                'section': 'Logistics',
                'job_title': 'Officer',
            },
        ]
        
        created_units = 0
        for unit_data in units_data:
            housing_unit, created = HousingUnit.objects.get_or_create(
                property=abra_property,
                unit_number=unit_data['unit_number'],
                defaults={
                    'floor': unit_data['floor'],
                    'housing_unit_name': unit_data['housing_unit_name'],
                    'address': unit_data['address'],
                    'occupant_name': unit_data['occupant_name'],
                    'department': unit_data['department'],
                    'section': unit_data['section'],
                    'job_title': unit_data['job_title'],
                    'date_reported': date.today(),
                }
            )
            
            if created:
                created_units += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created Housing Unit: {housing_unit}'))
            else:
                self.stdout.write(self.style.WARNING(f'  ✓ Housing Unit already exists: {housing_unit}'))
            
            # Add sample inventory items to each unit
            if created:
                inventory_items = [
                    {
                        'item_name': 'Sofa Bed',
                        'quantity': 1,
                        'acquisition_cost': Decimal('15000.00'),
                        'useful_life': 7,
                    },
                    {
                        'item_name': 'Dining Table',
                        'quantity': 1,
                        'acquisition_cost': Decimal('8000.00'),
                        'useful_life': 10,
                    },
                    {
                        'item_name': 'Chairs',
                        'quantity': 4,
                        'acquisition_cost': Decimal('2000.00'),
                        'useful_life': 5,
                    },
                    {
                        'item_name': 'Shelving Unit',
                        'quantity': 2,
                        'acquisition_cost': Decimal('5000.00'),
                        'useful_life': 8,
                    },
                ]
                
                for item in inventory_items:
                    inv_item, inv_created = PropertyInventory.objects.get_or_create(
                        housing_unit=housing_unit,
                        item_name=item['item_name'],
                        defaults={
                            'quantity': item['quantity'],
                            'acquisition_cost': item['acquisition_cost'],
                            'useful_life': item['useful_life'],
                            'date_acquired': date.today(),
                        }
                    )
                    if inv_created:
                        self.stdout.write(self.style.SUCCESS(f'    ✓ Created inventory: {inv_item.item_name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Seeding complete! Created {created_units} housing units'))
        self.stdout.write(self.style.SUCCESS('Database is now populated with sample data'))
