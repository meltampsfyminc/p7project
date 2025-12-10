#!/usr/bin/env python
import os
import sys
import django

# Add the project to path
sys.path.insert(0, 'c:\\Projects\\p7project\\property_management')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_management.settings')
django.setup()

from properties.models import Property, HousingUnit, ImportedFile

print("="*80)
print("DATABASE RECORDS CHECK")
print("="*80)

print("\nPROPERTIES:")
properties = Property.objects.all()
print(f"Total: {properties.count()}")
for p in properties:
    print(f"  ID: {p.id}")
    print(f"  Name: {p.name}")
    print(f"  Address: {p.address}")
    print(f"  Owner: {p.owner}")
    print()

print("\nHOUSING UNITS:")
housing_units = HousingUnit.objects.all()
print(f"Total: {housing_units.count()}")
for h in housing_units:
    print(f"  ID: {h.id}")
    print(f"  Unit Name: {h.housing_unit_name}")
    print(f"  Unit Number: {h.unit_number}")
    print(f"  Property: {h.property.name if h.property else 'None'}")
    print(f"  Occupant: {h.occupant_name}")
    print(f"  Floor: {h.floor}")
    print()

print("\nIMPORTED FILES:")
imported_files = ImportedFile.objects.all()
print(f"Total: {imported_files.count()}")
for i in imported_files:
    print(f"  Filename: {i.filename}")
    print(f"  Status: {i.status}")
    print(f"  Records Imported: {i.records_imported}")
    print(f"  Imported At: {i.imported_at}")
    print()
