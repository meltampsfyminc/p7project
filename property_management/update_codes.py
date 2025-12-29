import os
import sys
import django

# Setup Django environment
sys.path.append('c:/Projects/p7project/property_management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_management.settings')
django.setup()

from properties.models import Local
from gusali.models import Building
from kagamitan.models import Item
from lupa.models import Land
from plants.models import Plant

def update_records():
    try:
        # 1. Get Balayan Batangas Local object
        lcode = '003'
        dcode = '01009'
        balayan = Local.objects.filter(lcode=lcode, district__dcode=dcode).first()
        
        if not balayan:
            print("Error: Balayan Batangas local (003/01009) not found in database.")
            return

        print(f"Found Balayan Batangas: {balayan.name} (ID: {balayan.id})")

        # 2. Update Buildings
        buildings = Building.objects.all()
        count = buildings.update(lcode=lcode, dcode=dcode, local=balayan)
        print(f"Updated {count} buildings.")

        # 3. Update Items (Items already have some data? Let's check)
        items = Item.objects.all()
        count = items.update(lcode=lcode, dcode=dcode, local=balayan)
        print(f"Updated {count} items.")

        # 4. Update Lands
        lands = Land.objects.all()
        count = lands.update(lcode=lcode, dcode=dcode, local=balayan)
        print(f"Updated {count} lands.")

        # 5. Update Plants
        plants = Plant.objects.all()
        count = plants.update(lcode=lcode, dcode=dcode, local=balayan)
        print(f"Updated {count} plants.")

        print("Updates complete!")

    except Exception as e:
        print(f"Update error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_records()
