#!/usr/bin/env python
import os
import sys
import django

# Add the project to path
sys.path.insert(0, 'c:\\Projects\\p7project\\property_management')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'property_management.settings')
django.setup()

from django.core.management import call_command
from io import StringIO

file_path = r'c:\Projects\p7project\property_management\uploads\P-7-H - Unit 22.xls'

print("="*80)
print(f"Testing import of: {file_path}")
print("="*80)

output = StringIO()
error_output = StringIO()

try:
    call_command('import_inventory', file_path, stdout=output, stderr=error_output)
    
    output_text = output.getvalue()
    error_text = error_output.getvalue()
    
    print("\n--- STDOUT ---")
    print(output_text)
    
    if error_text:
        print("\n--- STDERR ---")
        print(error_text)
    
    print("\n" + "="*80)
    print("RESPONSE CHECKS:")
    print("="*80)
    print(f"'FILE ALREADY IMPORTED' in output: {'FILE ALREADY IMPORTED' in output_text}")
    print(f"'IMPORT COMPLETE' in output: {'IMPORT COMPLETE' in output_text}")
    print(f"'Error' in output: {'Error' in output_text}")
    
except Exception as e:
    print(f"\nException occurred: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
