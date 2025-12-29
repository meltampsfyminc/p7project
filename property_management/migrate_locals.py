import os
import sys
import django
import pymysql

# Setup Django environment
sys.path.append('c:/Projects/p7project/property_management')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_management.settings')
django.setup()

from properties.models import District, Local

# Configuration
MARIADB_CONFIG = {
    'user': 'gravityuser',
    'password': 'mbt073233',
    'host': 'localhost',
    'port': 3307,
    'database': 'purchasing',
    'cursorclass': pymysql.cursors.DictCursor
}

def migrate():
    try:
        # 1. Connect to MariaDB
        print("Connecting to MariaDB...")
        m_conn = pymysql.connect(**MARIADB_CONFIG)
        m_cursor = m_conn.cursor()

        # 2. Clear existing records in PostgreSQL
        print("Cleaning up PostgreSQL records...")
        Local.objects.all().delete()
        District.objects.all().delete()

        # 3. Migrate Districts
        print("Migrating Districts...")
        m_cursor.execute("SELECT distname, dcode FROM district")
        districts = m_cursor.fetchall()
        print(f"Fetched {len(districts)} districts from MariaDB.")
        
        district_objs = []
        for d in districts:
            dcode = str(d.get('dcode')).strip()
            name = str(d.get('distname')).strip()
            
            if not dcode:
                continue

            obj = District(
                dcode=dcode,
                name=name or f"District {dcode}",
                description=""
            )
            district_objs.append(obj)
        
        # Unique by dcode
        unique_districts = {}
        for obj in district_objs:
            unique_districts[obj.dcode] = obj
            
        print(f"Attempting to bulk create {len(unique_districts)} unique districts...")
        District.objects.bulk_create(unique_districts.values())
        print(f"✓ Total districts in PostgreSQL: {District.objects.count()}")

        # 4. Migrate Locals
        print("Migrating Locals...")
        m_cursor.execute("SELECT dcode, lcode, lokal FROM lokal2")
        locals_raw = m_cursor.fetchall()
        print(f"Fetched {len(locals_raw)} locals from MariaDB.")

        # Cache existing dcodes for matching
        existing_dcodes = set(District.objects.values_list('dcode', flat=True))
        
        local_objs_map = {} # Keyed by (lcode, dcode)
        skip_count = 0
        
        for l in locals_raw:
            lcode = str(l.get('lcode')).strip()
            name = str(l.get('lokal')).strip()
            dcode = str(l.get('dcode')).strip()
            
            if not lcode or not dcode:
                skip_count += 1
                continue

            if dcode in existing_dcodes:
                key = (lcode, dcode)
                if key not in local_objs_map:
                    local_objs_map[key] = Local(
                        lcode=lcode,
                        name=name or f"Local {lcode}",
                        district_id=dcode,
                        description=""
                    )
                else:
                    # Duplicate (lcode, dcode) pair
                    skip_count += 1
            else:
                # District not found
                skip_count += 1

        print(f"Attempting to bulk create {len(local_objs_map)} unique locals...")
        Local.objects.bulk_create(local_objs_map.values())
        print(f"✓ Total locals in PostgreSQL: {Local.objects.count()}")
        print(f"Skipped {skip_count} locals (missing codes or duplicates).")

        # 5. Search for Balayan Batangas
        print("-" * 40)
        print("Searching for Balayan Batangas...")
        balayan = Local.objects.filter(name__icontains='Balayan').first()
        if not balayan:
             balayan = Local.objects.filter(district__name__icontains='Batangas', name__icontains='Balayan').first()
             
        if balayan:
            print(f"Found: {balayan.name}")
            print(f"LCODE: {balayan.lcode}")
            print(f"DCODE: {balayan.district.dcode}")
            print(f"District: {balayan.district.name}")
        else:
            print("Balayan Batangas not found.")

        m_cursor.close()
        m_conn.close()
        print("Migration complete!")

    except Exception as e:
        print(f"Migration error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate()
