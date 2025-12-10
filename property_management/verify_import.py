#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_management.settings')
django.setup()

from properties.models import HousingUnit, PropertyInventory

# Show housing unit
hu = HousingUnit.objects.first()
print("="*100)
print("HOUSING UNIT DATA")
print("="*100)
print(f"Name: {hu.housing_unit_name}")
print(f"Occupant: {hu.occupant_name}")
print(f"Department: {hu.department}")
print(f"Section: {hu.section}")
print(f"Job Title: {hu.job_title}")
print(f"Building: {hu.building}")
print(f"Floor: {hu.floor}")
print(f"Unit Number: {hu.unit_number}")
print(f"Address: {hu.address}")
print(f"Date Reported: {hu.date_reported}")

# Show inventory items
print(f"\n{'='*100}")
print("INVENTORY ITEMS")
print(f"{'='*100}")
items = PropertyInventory.objects.filter(housing_unit=hu)
print(f"Total items: {items.count()}\n")

for i, item in enumerate(items, 1):
    print(f"{i}. {item.item_name}")
    print(f"   Quantity: {item.quantity}")
    print(f"   Year Acquired: {item.date_acquired}")
    print(f"   Material (Make): {item.make}")
    print(f"   Color: {item.color}")
    print(f"   Size: {item.size}")
    print(f"   Serial Number: {item.serial_number}")
    print(f"   Remarks: {item.remarks}")
    print()

print(f"{'='*100}")
print(f"TOTAL INVENTORY ITEMS: {items.count()}")
print(f"{'='*100}")
