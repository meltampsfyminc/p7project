import os

# Path to the template file
template_path = r'c:\Projects\p7project\property_management\templates\gusali\building_list.html'

# Read the file
with open(template_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all template syntax errors
# Line 71: current_district==district.dcode
content = content.replace(
    '{% if current_district==district.dcode %}selected{%',
    '{% if current_district == district.dcode %}selected{% endif %}'
)

# Line 83: current_local==local.lcode  
content = content.replace(
    '{% if current_local==local.lcode %}selected{% endif',
    '{% if current_local == local.lcode %}selected{% endif %}'
)

# Line 95: current_code==code
content = content.replace(
    '{% if current_code==code %}',
    '{% if current_code == code %}'
)

# Line 108: current_year==year
content = content.replace(
    '{% if current_year==year|stringformat:"s" %}selected{% endif',
    '{% if current_year == year|stringformat:"s" %}selected{% endif %}'
)

# Also fix any remaining broken endif tags
content = content.replace('selected{%\r\n    endif %}', 'selected{% endif %}')
content = content.replace('selected{% endif\r\n    %}', 'selected{% endif %}')

# Write back with fsync to ensure it's written
with open(template_path, 'w', encoding='utf-8') as f:
    f.write(content)
    f.flush()
    os.fsync(f.fileno())

print("Fixed all template syntax errors in building_list.html")
