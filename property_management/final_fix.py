import os

files = [
    'templates/gusali/building_list.html',
    'templates/kagamitan/item_list.html',
    'templates/lupa/land_list.html',
    'templates/plants/plant_list.html',
    'templates/vehicles/vehicle_list.html'
]

for rel_path in files:
    path = os.path.join('c:/Projects/p7project/property_management', rel_path)
    if not os.path.exists(path):
        print(f"Skipping {path}")
        continue
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix current_district==
    new_content = content.replace('current_district==district.dcode', 'current_district == district.dcode')
    # Fix current_local==
    new_content = new_content.replace('current_local==local.lcode', 'current_local == local.lcode')
    # Fix some common variants
    new_content = new_content.replace('current_district ==district.dcode', 'current_district == district.dcode')
    new_content = new_content.replace('current_district== district.dcode', 'current_district == district.dcode')
    
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {rel_path}")
    else:
        print(f"Already fixed or not found in {rel_path}")
