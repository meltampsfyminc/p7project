#!/usr/bin/env python
import os
import sys
import django

# Add the project to path
sys.path.insert(0, 'c:\\Projects\\p7project\\property_management')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_management.settings')
django.setup()

from properties.models import ImportedFile

print("="*80)
print("IMPORTED FILES IN DATABASE")
print("="*80)

imported_files = ImportedFile.objects.all()
print(f"\nTotal: {imported_files.count()}")

for i in imported_files:
    print(f"\nFile: {i.filename}")
    print(f"  Hash: {i.file_hash}")
    print(f"  Status: {i.status}")
    print(f"  Records: {i.records_imported}")
    print(f"  Imported At: {i.imported_at}")
    print(f"  Error: {i.error_message}")

if imported_files.count() > 0:
    print("\n" + "="*80)
    print("DELETING ALL IMPORTED FILE RECORDS...")
    print("="*80)
    ImportedFile.objects.all().delete()
    print("✓ Deleted all import records")
    print(f"Remaining: {ImportedFile.objects.count()}")
