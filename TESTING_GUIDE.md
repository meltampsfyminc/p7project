# Testing Guide - Property Management System

## Quick Start Testing

### 1. Database Verification
```bash
python manage.py shell
```

Then in Python shell:
```python
from properties.models import HousingUnit, PropertyInventory, ImportedFile

# Check Housing Units
units = HousingUnit.objects.all()
print(f"Total housing units: {units.count()}")
for unit in units:
    print(f"  - {unit}")

# Check Inventory Items
items = PropertyInventory.objects.all()
print(f"Total inventory items: {items.count()}")
for item in items[:5]:
    print(f"  - {item.item_name} (Qty: {item.quantity})")

# Check Import History
imports = ImportedFile.objects.all()
print(f"Total imports tracked: {imports.count()}")
for imp in imports:
    print(f"  - {imp.filename}: {imp.records_imported} records")
```

### 2. Management Command Testing

#### Test 1: First Import (New File)
```bash
python manage.py import_inventory "c:\Projects\p7project\P-7-H - Unit 22.xls"
```

Expected Output:
```
====================================================================================================
IMPORTING INVENTORY DATA FROM: c:\Projects\p7project\P-7-H - Unit 22.xls
====================================================================================================

EXTRACTING HEADER INFORMATION...
Occupant: Michael M. Tama
Department: Finance
Section: P-7 Property
Job Title: Section Chief
Housing Unit: Unit 22
Building: Abra
Address: #12 Unit 22 Abra Street, Brgy. Ramon Magsaysay, Quezon City
Date Reported: None

CREATING/UPDATING HOUSING UNIT...
✓ Using existing Housing Unit: Unit 22 - Michael M. Tama

EXTRACTING INVENTORY ITEMS...
----------------------------------------------------------------------------------------------------
✓ Row 9: Sofa bed (Qty: 1)
✓ Row 10: Sofa (Qty: 1)
... (14 more items)

====================================================================================================
IMPORT COMPLETE
====================================================================================================
Housing Units: 1
Inventory Items Created: 16
Rows Skipped: 0
Total Items: 16

====================================================================================================

Import record saved for duplicate detection
File Hash: a94f8b6d383f9cdbe181fd3b32482b231ae9f069ca5b5d02e3077c1726ea9f47
```

#### Test 2: Duplicate Detection (Same File Again)
```bash
python manage.py import_inventory "c:\Projects\p7project\P-7-H - Unit 22.xls"
```

Expected Output:
```
====================================================================================================
FILE ALREADY IMPORTED
====================================================================================================
Filename: P-7-H - Unit 22.xls
Previously imported on: 2025-12-09 00:55:41.124530+00:00
Records imported: 16
Status: success

Use --force flag to re-import this file
====================================================================================================
```

#### Test 3: Force Re-import
```bash
python manage.py import_inventory "c:\Projects\p7project\P-7-H - Unit 22.xls" --force
```

Expected Output:
```
====================================================================================================
IMPORTING INVENTORY DATA FROM: c:\Projects\p7project\P-7-H - Unit 22.xls
====================================================================================================

[Full import output as in Test 1]

====================================================================================================
Import record saved for duplicate detection
File Hash: a94f8b6d383f9cdbe181fd3b32482b231ae9f069ca5b5d02e3077c1726ea9f47
```

Note: Since the file already exists, no new records are created (all items already exist in database with same housing unit and item names)

### 3. Web Interface Testing

#### Test 4: Start Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

Then in browser:

#### Test 4a: Access Upload Interface
```
http://localhost:8000/properties/upload/
```

What you should see:
- Upload area with drag-and-drop support
- "Select File & Upload" button
- Recent imports table showing at least 1 import
- Navigation links

#### Test 4b: Upload New File
1. Click upload area or button
2. Select `P-7-H - Unit 22.xls` again
3. Should see: "File already imported" message
4. Page should not reload

#### Test 4c: View Inventory List
```
http://localhost:8000/properties/inventory/
```

What you should see:
- All 16 inventory items listed
- Filter by housing unit dropdown
- Item details (quantity, brand, model, etc.)

#### Test 4d: Admin Interface
```
http://localhost:8000/admin/
```

Login with superuser credentials, then:
1. Go to Properties > Imported Files
2. Should see 1 entry with:
   - Filename: P-7-H - Unit 22.xls
   - File Hash: a94f8b6d383f9cdbe181fd3b32482b231ae9f069ca5b5d02e3077c1726ea9f47
   - Records Imported: 16
   - Status: success

3. Go to Properties > Housing Units
4. Should see:
   - Unit 22 - Michael M. Tama
   - Department: Finance
   - Section: P-7 Property

5. Go to Properties > Property Inventories
6. Should see all 16 items with full details

### 4. Error Handling Tests

#### Test 5: Invalid File Type
```bash
# Create a test text file
echo "test" > test.txt

# Try to upload via curl
curl -F "file=@test.txt" http://localhost:8000/properties/upload/
```

Expected Error:
```json
{
  "success": false,
  "message": "File type not allowed. Allowed types: .xls, .xlsx, .pdf"
}
```

#### Test 6: Non-existent File
```bash
python manage.py import_inventory "c:\non\existent\file.xls"
```

Expected Error:
```
File not found: c:\non\existent\file.xls
```

### 5. Database Verification Tests

#### Test 7: Check ImportedFile Records
```bash
python manage.py shell -c "from properties.models import ImportedFile; [print(f'{i.filename}: {i.records_imported} records - {i.status}') for i in ImportedFile.objects.all()]"
```

#### Test 8: Verify Inventory Data
```bash
python manage.py shell -c "from properties.models import PropertyInventory, HousingUnit; unit = HousingUnit.objects.first(); print(f'Unit: {unit}'); items = PropertyInventory.objects.filter(housing_unit=unit); print(f'Items: {items.count()}'); [print(f'  - {i.item_name} (Qty: {i.quantity})') for i in items[:5]]"
```

Expected Output:
```
Unit: Unit 22 - Michael M. Tama
Items: 16
  - Sofa bed (Qty: 1)
  - Sofa (Qty: 1)
  - Office chair (Qty: 2)
  - Wardrobe cabinet (Qty: 4)
  - Dining table (Qty: 1)
```

## Test Checklist

### Core Functionality
- [x] Django app loads without errors (`python manage.py check`)
- [x] Database connection works
- [x] Models created (Property, HousingUnit, PropertyInventory, ImportedFile)
- [x] Migrations applied successfully
- [x] Sample data imported (16 items)

### Import System
- [x] Management command executes successfully
- [x] File hashing works (SHA256)
- [x] Duplicate detection works (prevents re-import)
- [x] Force flag overrides duplicate detection
- [x] ImportedFile records created/updated
- [x] Import history tracked

### Web Interface
- [x] Upload page loads
- [x] File upload validation works
- [x] Automatic import on upload
- [x] Duplicate message shows correctly
- [x] Recent imports display
- [ ] Test with actual file drag-drop (manual)
- [ ] Test with different file (if available)

### Admin Interface
- [x] Admin page loads
- [x] All models visible
- [x] Can view ImportedFile records
- [x] Can view housing units
- [x] Can view inventory items
- [ ] Test filtering (manual)
- [ ] Test search (manual)

### Error Handling
- [x] Invalid file types rejected
- [x] Missing files handled
- [x] Database errors handled
- [ ] Corrupted file handling (needs test file)
- [ ] Network errors (if using web upload)

## Running Full Test Suite

To run all tests in one command:

```bash
# Check Django
python manage.py check

# Test database
python manage.py migrate --plan

# Import test
python manage.py import_inventory "c:\Projects\p7project\P-7-H - Unit 22.xls" --force

# Database verification
python manage.py shell < test_queries.py

# Admin creation (if needed)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

## Performance Testing

### Import Speed
```bash
# Time the import command
time python manage.py import_inventory "c:\Projects\p7project\P-7-H - Unit 22.xls" --force
```

Expected: < 5 seconds for 16 items

### Web Upload Speed
- File: P-7-H - Unit 22.xls (~25 KB)
- Expected upload time: < 2 seconds
- Expected import time: < 5 seconds
- Total: < 7 seconds

### Database Query Performance
```bash
python manage.py shell
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as queries:
    # Run your query
    from properties.models import PropertyInventory
    items = PropertyInventory.objects.select_related('housing_unit').all()
    list(items)  # Force evaluation

print(f"Total queries: {len(queries)}")
for q in queries:
    print(f"Time: {q['time']:.3f}s")
```

## Troubleshooting During Testing

### Issue: "ImportedFile table doesn't exist"
**Solution**: Run migrations
```bash
python manage.py migrate
```

### Issue: "File not found" on correct path
**Solution**: Use absolute paths or check working directory
```bash
import os
print(os.getcwd())  # Check current directory
```

### Issue: Duplicate import still creates new record
**Solution**: Ensure unique=True on file_hash field
```bash
python manage.py shell
from properties.models import ImportedFile
print(ImportedFile._meta.get_field('file_hash').unique)  # Should be True
```

### Issue: Web server doesn't start
**Solution**: Check if port 8000 is in use
```bash
# Change port
python manage.py runserver 8001

# Or kill process on port 8000
# Windows: netstat -ano | findstr :8000
# Find PID and: taskkill /PID <pid> /F
```

## Success Criteria

All tests pass when:
1. ✓ Import command executes without errors
2. ✓ File hash is calculated correctly
3. ✓ Duplicate files are detected and blocked
4. ✓ Force flag allows re-import
5. ✓ ImportedFile records are created
6. ✓ Web upload interface works
7. ✓ All data is persisted in database
8. ✓ Admin interface shows all records
9. ✓ No errors in Django checks

## Next Steps After Testing

If all tests pass:
1. Backup database
2. Test with different Excel files
3. Test PDF import (if PDF support is added)
4. Set up production deployment
5. Configure scheduled imports (if needed)
6. Add user authentication
7. Set up logging and monitoring
