import os
import subprocess
import re
import sys

def fix_templates():
    files = [
        'templates/gusali/building_list.html',
        'templates/kagamitan/item_list.html',
        'templates/lupa/land_list.html',
        'templates/plants/plant_list.html',
        'templates/vehicles/vehicle_list.html'
    ]
    
    # Regex to find {% if var==var %} or variations
    # We want to ensure at least one space around ==
    re_eq = re.compile(r'\{\%\s*if\s+([a-zA-Z0-9_\.]+)\s*==\s*([a-zA-Z0-9_\.]+)\s*\%\}')
    
    for rel_path in files:
        path = os.path.join('c:/Projects/p7project/property_management', rel_path)
        if not os.path.exists(path):
            print(f"MISSING: {path}")
            continue
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Standardize to {% if var == var %}
        new_content = re_eq.sub(r'{% if \1 == \2 %}', content)
        
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                f.flush()
                os.fsync(f.fileno())
            print(f"Fixed {rel_path}")
        else:
            print(f"No changes needed for {rel_path}")

if __name__ == "__main__":
    fix_templates()
    print("Running tests...")
    # Run tests and save to file to avoid terminal mangling
    with open('test_results.txt', 'w', encoding='utf-8') as f:
        result = subprocess.run([sys.executable, 'manage.py', 'test', 'properties.tests_national', '-v', '2'], 
                                stdout=f, stderr=subprocess.STDOUT, text=True)
    print("Tests finished. Check test_results.txt")
