import os
import django
import sys

# Add project root to path
sys.path.append('c:/Projects/p7project/property_management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_management.settings')
django.setup()

from kagamitan.models import Item

print(f"Total Items: {Item.objects.count()}")
print("-" * 50)
for item in Item.objects.all().order_by('id'):
    print(f"ID: {item.id}")
    print(f"Location (Kaukulan): '{item.location}'")
    print(f"Prop No: {item.property_number}")
    print(f"Name: {item.item_name}")
    print(f"Is New: {item.is_new}")
    print("-" * 20)
