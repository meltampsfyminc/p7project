#!/usr/bin/env python
import os
import sys
import django

# Add the project to path
sys.path.insert(0, 'c:\\Projects\\p7project\\property_management')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_management.settings')
django.setup()

from properties.models import HousingUnit, ImportedFile, PropertyInventory

print("="*80)
print("DELETING TEST DATA")
print("="*80)

# Delete PropertyInventory items for Unit 22
unit_22 = HousingUnit.objects.filter(housing_unit_name='Unit 22').first()
if unit_22:
    inventory_count = PropertyInventory.objects.filter(housing_unit=unit_22).count()
    print(f"\n✓ Found Unit 22 with {inventory_count} inventory items")
    print(f"  Occupant: {unit_22.occupant_name}")
    
    # Delete inventory items
    PropertyInventory.objects.filter(housing_unit=unit_22).delete()
    print(f"  ✓ Deleted {inventory_count} inventory items")
    
    # Delete the housing unit
    unit_22.delete()
    print(f"  ✓ Deleted Housing Unit 22")
else:
    print("Unit 22 not found")

# Delete the imported file record
imported_file = ImportedFile.objects.filter(filename__icontains='Unit 22').first()
if imported_file:
    print(f"\n✓ Found imported file record")
    print(f"  Filename: {imported_file.filename}")
    print(f"  Status: {imported_file.status}")
    print(f"  Records: {imported_file.records_imported}")
    
    imported_file.delete()
    print(f"  ✓ Deleted import record")
else:
    print("\nNo import record found for Unit 22")

print("\n" + "="*80)
print("FINAL DATABASE STATE")
print("="*80)

from properties.models import Property, HousingUnit as HU, ImportedFile as IF

print(f"\nProperties: {Property.objects.count()}")
for p in Property.objects.all():
    print(f"  - {p.name}")

print(f"\nHousing Units: {HU.objects.count()}")
for h in HU.objects.all():
    print(f"  - {h.housing_unit_name} ({h.occupant_name})")

print(f"\nImported Files: {IF.objects.count()}")
for i in IF.objects.all():
    print(f"  - {i.filename}")

print("\n✓ Ready for re-upload test!")
print("="*80)
