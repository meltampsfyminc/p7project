#!/usr/bin/env python
import os
import sys
import django

# Add the project to path
sys.path.insert(0, 'c:\\Projects\\p7project\\property_management')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_management.settings')
django.setup()

from properties.models import Property, HousingUnit

# Find the "Abra Building" property
abra_property = Property.objects.filter(name__icontains='Abra').first()

print(f"Abra Property found: {abra_property}")

if abra_property:
    # Find Unit 22 and link it to Abra Building
    unit_22 = HousingUnit.objects.filter(housing_unit_name='Unit 22', property=None).first()
    
    if unit_22:
        print(f"\nFound Unit 22 without property:")
        print(f"  ID: {unit_22.id}")
        print(f"  Unit Name: {unit_22.housing_unit_name}")
        print(f"  Property: {unit_22.property}")
        
        # Update it
        unit_22.property = abra_property
        unit_22.save()
        
        print(f"\n✓ Updated Unit 22 to link to {abra_property.name}")
        print(f"  New Property: {unit_22.property}")
    else:
        print("Unit 22 not found")
else:
    print("Abra property not found")
