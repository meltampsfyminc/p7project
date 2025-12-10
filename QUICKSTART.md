# Property Management System - Quick Start Guide

## What Has Been Built

A complete Django property management system with:
- ✅ PostgreSQL database integration
- ✅ Inventory tracking system (HousingUnit + PropertyInventory models)
- ✅ Excel file import with automatic data extraction
- ✅ SHA256 file hashing for duplicate prevention
- ✅ Web-based file upload interface
- ✅ Django admin dashboard
- ✅ Import history tracking
- ✅ Multiple database deployment options (Local, Docker, Supabase)

## Quick Start (5 Minutes)

### 1. Start the Development Server
```bash
cd c:\Projects\p7project\property_management
python manage.py runserver 0.0.0.0:8000
```

### 2. Access the Application
- **Web Upload Interface**: http://localhost:8000/properties/upload/
- **Admin Dashboard**: http://localhost:8000/admin/ (login required)
- **Inventory List**: http://localhost:8000/properties/inventory/
- **Properties List**: http://localhost:8000/properties/

### 3. Upload a File
1. Go to: http://localhost:8000/properties/upload/
2. Drag & drop or click to select: `P-7-H - Unit 22.xls`
3. System will auto-import → Shows: "File already imported" (it's already in DB)
4. View results in recent imports table below

### 4. View Imported Data
1. Click "View Inventory" button or go to: http://localhost:8000/properties/inventory/
2. See all 16 inventory items
3. Filter by housing unit "Unit 22"

### 5. Admin Dashboard
1. Go to: http://localhost:8000/admin/
2. Login with superuser account
3. View:
   - Properties > Imported Files (shows import history)
   - Properties > Housing Units (shows Unit 22)
   - Properties > Property Inventories (shows 16 items)

## Key Files

| File | Purpose |
|------|---------|
| `manage.py` | Django management script |
| `properties/models.py` | 4 database models |
| `properties/views.py` | Web views and file upload |
| `properties/urls.py` | URL routing |
| `properties/management/commands/import_inventory.py` | Import command with duplicate detection |
| `templates/properties/upload_file.html` | Upload interface |
| `.env` | Database credentials |
| `requirements.txt` | Python dependencies |

## Common Commands

### Import Excel File
```bash
python manage.py import_inventory "C:\Projects\p7project\P-7-H - Unit 22.xls"
```

### Test Duplicate Detection
```bash
# Second import (will be blocked)
python manage.py import_inventory "C:\Projects\p7project\P-7-H - Unit 22.xls"

# Force re-import
python manage.py import_inventory "C:\Projects\p7project\P-7-H - Unit 22.xls" --force
```

### Check System Status
```bash
python manage.py check
python manage.py dbshell  # Test database connection
```

### Create Admin User
```bash
python manage.py createsuperuser
```

## File Upload System Features

### How It Works
1. **Upload File** → `/properties/upload/`
2. **File Saved** → `/uploads/` directory
3. **Hash Calculated** → SHA256 of file content
4. **Duplicate Check** → Hash checked in database
   - If new: Import proceeds
   - If duplicate: User gets warning
5. **Auto-Import** → Management command runs automatically
6. **Tracking** → ImportedFile record created/updated

### Duplicate Prevention
- Each file's SHA256 hash is stored
- Identical files detected even if renamed
- Previous import details shown (timestamp, record count)
- Override with `--force` flag

### REST API (File Upload)
```
POST /properties/upload/
Content-Type: multipart/form-data
Body: file=<binary>

Response (success):
{
  "success": true,
  "message": "File imported successfully!",
  "details": "<import output>"
}

Response (duplicate):
{
  "success": false,
  "message": "File already imported. Use force flag to re-import.",
  "details": "<previous import info>"
}
```

## Database

### Current Data
- **Housing Unit**: Unit 22
- **Occupant**: Michael M. Tama
- **Department**: Finance
- **Inventory Items**: 16
  - Sofas (2), Chairs (6), Beds (5), Tables (1), Cabinets (2)

### Connection Details
```
Host: localhost
Port: 5432
Database: property_management
User: postgres
Password: Mbt*7tbm#pg723
```

### Tables
- `properties_property` - Properties
- `properties_housingunit` - Housing units (1 record)
- `properties_propertyinventory` - Inventory items (16 records)
- `properties_importedfile` - Import tracking (1+ records)

## Project Structure

```
property_management/
├── manage.py                    # Django management
├── properties/                  # Main app
│   ├── models.py               # 4 models
│   ├── views.py                # Upload + display views
│   ├── urls.py                 # URL patterns
│   ├── admin.py                # Admin config
│   ├── management/commands/
│   │   └── import_inventory.py # Import command
│   ├── migrations/             # Database changes
│   └── uploads/                # Uploaded files
├── property_management/         # Django settings
│   ├── settings.py             # Configuration
│   ├── urls.py                 # Main routing
│   ├── wsgi.py / asgi.py       # Servers
├── templates/                  # HTML templates
│   └── properties/
│       ├── upload_file.html    # Upload UI
│       └── property_list.html
├── static/                     # CSS, JS, images
├── .env                        # Secrets (NOT in git)
└── requirements.txt            # Dependencies
```

## Documentation Files

| Document | Content |
|----------|---------|
| `COMPLETE_DOCUMENTATION.md` | Full project guide (this file) |
| `FILE_UPLOAD_SYSTEM.md` | Upload & duplicate prevention details |
| `TESTING_GUIDE.md` | Comprehensive testing procedures |
| `IMPLEMENTATION_SUMMARY.md` | What was built and why |
| `SETUP_GUIDE.md` | Installation steps |
| `DATABASE_OPTIONS.md` | Multi-database deployment |
| `DATA_IMPORT_ANALYSIS.md` | Excel file structure |

## Troubleshooting

### Server Won't Start
```bash
# Check Django configuration
python manage.py check

# Try different port
python manage.py runserver 8001
```

### Can't Upload Files
1. Verify `/uploads/` directory exists
2. Check database connection: `python manage.py dbshell`
3. Review file extension (.xls, .xlsx, .pdf only)

### Duplicate Files Still Imported
1. Check ImportedFile table: `SELECT COUNT(*) FROM properties_importedfile;`
2. File hash must be unique constraint
3. Force re-import: Add `--force` flag

### Database Errors
1. Check `.env` credentials
2. Verify PostgreSQL is running
3. Run migrations: `python manage.py migrate`

See `TESTING_GUIDE.md` for more troubleshooting.

## Next Steps

### For Local Development
1. ✅ System is ready to use
2. Test with different Excel files
3. Add more housing units/inventory
4. Create custom reports

### For Production
1. Set `DEBUG=False` in settings.py
2. Configure allowed hosts
3. Set up SSL certificates
4. Use Docker for deployment
5. Set up automated backups

### Future Features
- PDF OCR processing
- CSV import support
- Advanced search/filtering
- Data export (PDF reports)
- User authentication
- Scheduled imports
- Email notifications

## Useful Links

- **Admin Interface**: http://localhost:8000/admin/
- **Upload Interface**: http://localhost:8000/properties/upload/
- **Inventory View**: http://localhost:8000/properties/inventory/
- **Django Docs**: https://docs.djangoproject.com/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

## Support

For issues:
1. Check `TESTING_GUIDE.md` for testing procedures
2. Review `COMPLETE_DOCUMENTATION.md` for detailed info
3. Run `python manage.py check` for configuration issues
4. Check database with `python manage.py dbshell`

---

## Command Reference

### Development
```bash
# Start server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Access shell
python manage.py shell
```

### Database
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration plan
python manage.py migrate --plan
```

### Import
```bash
# Standard import
python manage.py import_inventory "file.xls"

# Force re-import
python manage.py import_inventory "file.xls" --force

# Clear before import
python manage.py import_inventory "file.xls" --clear
```

### Utilities
```bash
# Check configuration
python manage.py check

# Database shell
python manage.py dbshell

# Collect static files
python manage.py collectstatic
```

## Credentials

### Admin Account
- **Default User**: admin
- **Default Password**: (Create with `createsuperuser`)

### Database
- **Host**: localhost
- **Port**: 5432
- **User**: postgres
- **Password**: See `.env` file

## Success Indicators

✅ System is working correctly when:
- [ ] Server starts without errors
- [ ] Can access http://localhost:8000/properties/upload/
- [ ] Can login to admin at http://localhost:8000/admin/
- [ ] Can view imported inventory items
- [ ] Duplicate detection prevents re-import
- [ ] Force flag allows re-import
- [ ] Import history shows in database

---

## 🆕 NEW FEATURES: Authentication & 2FA

A complete authentication system with Two-Factor Authentication has been added!

### Authentication Features
- ✅ User login with Django authentication
- ✅ User logout with session management
- ✅ Homepage with responsive design
- ✅ Protected dashboard with statistics
- ✅ Two-Factor Authentication (2FA) with TOTP
- ✅ Backup codes for account recovery
- ✅ IP address tracking
- ✅ Login timestamp tracking

### Quick Authentication Setup

1. **Create a test user**:
```bash
python manage.py createsuperuser
```

2. **Access the application**:
- Homepage: http://localhost:8000/
- Login: http://localhost:8000/login/
- Dashboard: http://localhost:8000/dashboard/

3. **Enable 2FA** (after login):
- Click "Enable 2FA" on dashboard
- Install Google Authenticator, Authy, or Microsoft Authenticator on phone
- Scan QR code
- Enter 6-digit verification code
- Save backup codes in secure location

4. **Login with 2FA**:
- Enter username/password
- Enter 6-digit code from authenticator app
- OR enter a backup code

### New Templates
- `templates/properties/index.html` - Homepage
- `templates/properties/login.html` - Login form
- `templates/properties/dashboard.html` - Dashboard
- `templates/properties/setup_2fa.html` - 2FA setup
- `templates/properties/backup_codes.html` - Backup codes
- `templates/properties/base.html` - Master template

### New Routes
| Route | Purpose |
|-------|---------|
| `/` | Homepage |
| `/login/` | User login |
| `/logout/` | User logout |
| `/dashboard/` | Protected dashboard |
| `/setup-2fa/` | Enable/disable 2FA |
| `/backup-codes/` | View backup codes |

### Security Features
- TOTP (Time-based One-Time Password) encryption
- Backup codes (10 per user, one-time use)
- CSRF token protection
- Session-based authentication
- Password hashing (PBKDF2)
- IP tracking for login audit trail

---

**Status**: ✅ Production Ready
**Version**: 2.0.0 (With Authentication & 2FA)
**Last Updated**: December 2024

For detailed information, see the documentation files:
- `AUTHENTICATION_IMPLEMENTATION.md` - Full implementation details
- `AUTHENTICATION_TESTING_GUIDE.md` - Testing procedures
- `PHASE_COMPLETION_SUMMARY.md` - What was completed
- `IMPLEMENTATION_CHECKLIST.md` - Complete checklist
