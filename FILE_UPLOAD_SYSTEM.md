# File Upload & Duplicate Prevention System

## Overview

The property management system now includes an automated file upload and duplicate prevention system. Files uploaded to the system are automatically imported and tracked to prevent duplicate imports of the same file.

## Features

### 1. **Duplicate Detection via SHA256 Hashing**
- Each uploaded file is hashed using SHA256
- The hash is stored in the `ImportedFile` model's `file_hash` field (unique)
- If an identical file (same content, different name) is uploaded, it will be detected as a duplicate
- Prevents re-importing of the exact same file content

### 2. **Automatic Import on Upload**
- When a file is uploaded through the web interface, it's automatically stored in `/uploads` folder
- The `import_inventory` management command is triggered automatically
- Records are extracted and stored in the database
- User receives immediate feedback on import success/failure

### 3. **Import History Tracking**
- Every import is tracked in the `ImportedFile` table
- Records include:
  - `filename`: Original filename
  - `file_hash`: SHA256 hash (unique constraint)
  - `file_size`: File size in bytes
  - `imported_at`: Timestamp of import
  - `records_imported`: Number of records extracted
  - `status`: success, partial, or error
  - `error_message`: Any error details (skipped rows, etc.)

### 4. **Override with --force Flag**
- Users can force re-import of an already-imported file using the `--force` flag
- Command: `python manage.py import_inventory <file_path> --force`
- This will update the existing `ImportedFile` record with new counts

## Usage

### Web Interface Upload

1. Navigate to: `http://localhost:8000/properties/upload/`
2. Either:
   - Click the upload area to browse files
   - Drag and drop files onto the upload area
3. Supported formats: `.xls`, `.xlsx`, `.pdf`
4. System will automatically:
   - Detect if file is already imported
   - Import new files automatically
   - Show import results with record counts

### Management Command

```bash
# Standard import (prevents duplicates)
python manage.py import_inventory "path/to/file.xls"

# Force re-import of already-imported file
python manage.py import_inventory "path/to/file.xls" --force

# Clear existing inventory before import
python manage.py import_inventory "path/to/file.xls" --clear
```

## File Structure

### Uploads Directory
```
property_management/
└── uploads/              # Stores uploaded files
    ├── P-7-H - Unit 22.xls
    ├── Another-File.xlsx
    └── ...
```

### Database Tables

**ImportedFile Table** (`properties_importedfile`)
- `id`: Auto-generated primary key
- `filename`: Name of uploaded file
- `file_hash`: SHA256 hash (unique constraint)
- `file_size`: File size in bytes
- `imported_at`: Auto timestamp on creation
- `records_imported`: Count of records extracted
- `status`: success/partial/error
- `error_message`: Error details if any

## Duplicate Detection Logic

```python
# Step 1: Calculate SHA256 hash of uploaded file
file_hash = _calculate_file_hash(file_path)

# Step 2: Check if hash exists in ImportedFile table
existing = ImportedFile.objects.filter(file_hash=file_hash).first()

# Step 3: If exists and no --force flag
if existing:
    # Show warning with previous import details
    print(f"File already imported on {existing.imported_at}")
    print(f"Records imported: {existing.records_imported}")
    return  # Exit without re-importing

# Step 4: If new file or --force flag used
# Proceed with import and create/update ImportedFile record
```

## Example Scenarios

### Scenario 1: First Import
```
Upload: P-7-H - Unit 22.xls
Result: 
  ✓ File imported successfully
  ✓ 16 records imported
  ✓ Status: success
  ✓ File hash saved for future duplicate detection
```

### Scenario 2: Duplicate Detection
```
Upload: P-7-H - Unit 22.xls (same file, second time)
Result:
  ✗ FILE ALREADY IMPORTED
  ✗ Previously imported on: 2025-12-09 00:55:41
  ✗ Records imported: 16
  ✗ Use --force flag to re-import
```

### Scenario 3: Force Re-import
```
Command: python manage.py import_inventory "P-7-H - Unit 22.xls" --force
Result:
  ✓ File imported successfully (re-imported)
  ✓ 16 records imported
  ✓ Status: success
  ✓ Previous ImportedFile record updated with new timestamp
```

## API Endpoints

### Upload File (POST)
- **URL**: `/properties/upload/`
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Request**:
  ```
  file: <binary file content>
  ```
- **Response (Success)**:
  ```json
  {
    "success": true,
    "message": "File imported successfully!",
    "details": "<import command output>"
  }
  ```
- **Response (Duplicate)**:
  ```json
  {
    "success": false,
    "message": "File already imported. Use force flag to re-import.",
    "details": "<import command output>"
  }
  ```
- **Response (Error)**:
  ```json
  {
    "success": false,
    "message": "Error message",
    "details": "<error details>"
  }
  ```

### View Upload Form (GET)
- **URL**: `/properties/upload/`
- **Method**: GET
- **Response**: HTML form with recent import history

## Security Features

1. **File Validation**
   - Only `.xls`, `.xlsx`, `.pdf` files allowed
   - File extension checked before processing

2. **CSRF Protection**
   - Django CSRF token required for file uploads
   - Automatically included in HTML form

3. **Safe File Handling**
   - Files stored in isolated `/uploads` directory
   - Proper file streaming to prevent memory issues
   - Error handling for corrupted files

## Admin Interface

View and manage imports in Django admin:
1. Go to: `http://localhost:8000/admin/`
2. Navigate to: Properties > Imported Files
3. Features:
   - View all imported files
   - Filter by status (success, partial, error)
   - Search by filename
   - View import timestamps and record counts

## Troubleshooting

### File already imported error
- Use `--force` flag: `python manage.py import_inventory "file.xls" --force`
- Or delete the `ImportedFile` record from admin

### Import failed with errors
- Check error message in `ImportedFile.error_message` field
- Review Excel file format matches expected structure
- Check column positions match (columns: 3, 7, 9, 32, 37, 42, 52)

### File not found in /uploads
- Ensure `/uploads` directory exists (created automatically on first upload)
- Check file permissions on directory
- Verify absolute path in management command

## Next Steps

Potential enhancements:
1. Add PDF OCR processing with pytesseract
2. Create automatic file monitoring for `/uploads` folder
3. Add CSV format support
4. Implement batch import progress tracking
5. Add email notifications for import completion
6. Create inventory reports and exports
