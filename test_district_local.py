#!/usr/bin/env python
import os
import sys
import django

# Add the project to path
sys.path.insert(0, 'c:\\Projects\\p7project\\property_management')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_management.settings')
django.setup()

from properties.models import District, Local

print("="*80)
print("DISTRICT AND LOCAL MODELS - VERIFICATION")
print("="*80)

# Create test districts
print("\n1. CREATING TEST DISTRICTS...")
district1, created1 = District.objects.get_or_create(
    dcode='NCR',
    defaults={'name': 'National Capital Region'}
)
print(f"   District NCR: {'Created' if created1 else 'Already exists'}")
print(f"   └─ {district1}")

district2, created2 = District.objects.get_or_create(
    dcode='CALABARZON',
    defaults={'name': 'Calabarzon Region'}
)
print(f"   District CALABARZON: {'Created' if created2 else 'Already exists'}")
print(f"   └─ {district2}")

# Create test locals
print("\n2. CREATING TEST LOCALS...")
local1, created3 = Local.objects.get_or_create(
    lcode='QC01',
    district=district1,
    defaults={'name': 'Quezon City Local 1'}
)
print(f"   Local QC01: {'Created' if created3 else 'Already exists'}")
print(f"   └─ {local1}")
print(f"   └─ District Code: {local1.get_district_code()}")

local2, created4 = Local.objects.get_or_create(
    lcode='QC02',
    district=district1,
    defaults={'name': 'Quezon City Local 2'}
)
print(f"   Local QC02: {'Created' if created4 else 'Already exists'}")
print(f"   └─ {local2}")

local3, created5 = Local.objects.get_or_create(
    lcode='BIO01',
    district=district2,
    defaults={'name': 'Binangonan Local 1'}
)
print(f"   Local BIO01: {'Created' if created5 else 'Already exists'}")
print(f"   └─ {local3}")

# Display relationships
print("\n3. DISPLAYING RELATIONSHIPS...")
print("\nAll Districts:")
for d in District.objects.all():
    local_count = d.locals.count()
    print(f"  {d.dcode:15} - {d.name:30} ({local_count} locals)")
    for l in d.locals.all():
        print(f"    └─ {l.lcode:10} - {l.name}")

print("\n" + "="*80)
print(f"SUMMARY: {District.objects.count()} districts, {Local.objects.count()} locals")
print("="*80)
