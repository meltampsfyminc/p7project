# Property Management System

A complete Django property management application with integrated inventory tracking, Excel file import, and duplicate prevention system.

## 🎯 Features

### Core Functionality
- **Inventory Management**: Track housing units and their inventory items
- **File Import System**: Automatic Excel file import with data extraction
- **Duplicate Prevention**: SHA256-based file hashing prevents re-importing identical files
- **Web Upload Interface**: Drag-and-drop file upload with real-time feedback
- **Admin Dashboard**: Full Django admin interface for data management
- **Import History**: Complete tracking of all imported files

### Technical Features
- PostgreSQL database with environment-based configuration
- Multiple deployment options (local, Docker, Supabase)
- RESTful file upload API
- Secure file handling and validation
- Comprehensive logging and error tracking

## 📋 Quick Start

### 1. Prerequisites
- Python 3.13+
- PostgreSQL 15
- pip package manager

### 2. Installation

```bash
# Clone/navigate to project
cd c:\Projects\p7project\property_management

# Create virtual environment (if not already done)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure database in .env (already configured)
# Check c:\Projects\p7project\property_management\.env

# Run migrations
python manage.py migrate

# Create superuser (if needed)
python manage.py createsuperuser
```

### 3. Start Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

### 4. Access the Application

- **Web Interface**: http://localhost:8000/properties/
- **File Upload**: http://localhost:8000/properties/upload/
- **Admin Dashboard**: http://localhost:8000/admin/
- **Inventory List**: http://localhost:8000/properties/inventory/

## 📁 Project Structure

```
property_management/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── .env                              # Database configuration (secrets)
│
├── property_management/               # Django settings package
│   ├── settings.py                   # Main configuration
│   ├── urls.py                       # URL routing
│   ├── wsgi.py / asgi.py             # Server configurations
│   └── __init__.py
│
├── properties/                        # Main application
│   ├── models.py                     # Database models (4 models)
│   ├── views.py                      # Web views and API
│   ├── urls.py                       # App URL patterns
│   ├── admin.py                      # Admin interface configuration
│   ├── apps.py                       # App configuration
│   ├── management/
│   │   └── commands/
│   │       └── import_inventory.py   # Import command with duplicate detection
│   ├── migrations/                   # Database schema versions
│   └── uploads/                      # Uploaded files directory
│
├── templates/                         # HTML templates
│   └── properties/
│       ├── upload_file.html          # File upload interface
│       └── property_list.html        # Property listing
│
├── static/                           # CSS, JavaScript, images
│
├── docker-compose.yml                # Docker PostgreSQL setup
├── docker-compose.host.yml           # Docker app to host PostgreSQL
├── docker-compose.supabase.yml       # Supabase PostgreSQL option
│
└── Dockerfile                        # Container image definition
```

## 🗄️ Database Models

### 1. **ImportedFile** (Duplicate Prevention)
Tracks all imported files with SHA256 hashing for duplicate detection
- `filename`: Original file name
- `file_hash`: SHA256 hash (unique constraint)
- `file_size`: File size in bytes
- `imported_at`: Import timestamp
- `records_imported`: Number of records extracted
- `status`: success/partial/error
- `error_message`: Error details if any

### 2. **HousingUnit** (Housing Information)
Stores housing unit and occupant details
- `occupant_name`, `department`, `section`, `job_title`
- `date_reported`, `housing_unit_name`, `building`
- `floor`, `unit_number`, `address`

### 3. **PropertyInventory** (Inventory Items)
Tracks individual inventory items per housing unit
- `item_name`, `item_code`, `quantity`
- `date_acquired`, `brand`, `model`, `make`
- `color`, `size`, `serial_number`, `remarks`
- Foreign key to HousingUnit

### 4. **Property** (Original Model)
Basic property information
- `name`, `address`, `city`, `state`, `postal_code`
- `property_type`, `bedrooms`, `bathrooms`, `square_feet`
- `price`, `status`

## 📤 File Upload System

### How It Works

1. **Upload File** → Drag & drop or click to browse
2. **Validation** → Checks file type (.xls, .xlsx, .pdf)
3. **Hash Calculation** → SHA256 of file content
4. **Duplicate Detection** → Checks if file already imported
   - **New File**: Proceeds with import
   - **Duplicate**: Shows warning with previous import details
5. **Auto-Import** → Extracts data and imports to database
6. **Tracking** → Creates/updates ImportedFile record

### Features

- **Drag & Drop**: Intuitive file upload interface
- **Real-time Feedback**: Immediate import results
- **Duplicate Prevention**: Prevents re-importing identical files
- **Import History**: Shows recent imports with timestamps
- **File Validation**: Only accepts supported file types
- **Automatic Processing**: No manual steps required

## 🔧 Management Commands

### Import Excel File
```bash
# Standard import (with duplicate detection)
python manage.py import_inventory "path/to/file.xls"

# Force re-import of duplicate file
python manage.py import_inventory "path/to/file.xls" --force

# Clear existing inventory before import
python manage.py import_inventory "path/to/file.xls" --clear
```

### Other Commands
```bash
# Database operations
python manage.py migrate              # Apply migrations
python manage.py makemigrations       # Create migrations

# Admin
python manage.py createsuperuser      # Create admin user
python manage.py changepassword       # Change password

# Utilities
python manage.py check               # Check configuration
python manage.py dbshell             # Open database shell
python manage.py shell               # Python shell
```

## 🔐 Security

- **Credentials**: Database credentials stored in `.env` (not in git)
- **File Upload**: Validates file types and sizes
- **CSRF Protection**: Django CSRF tokens required for uploads
- **Safe Handling**: Chunked file streaming prevents memory issues
- **Database**: Uses environment variables instead of hardcoded credentials

## 🚀 Deployment

### Local Development
```bash
python manage.py runserver
```

### Docker with PostgreSQL
```bash
docker-compose up -d
```

### Docker to Host PostgreSQL
```bash
docker-compose -f docker-compose.host.yml up -d
```

### Production (Gunicorn)
```bash
gunicorn property_management.wsgi:application --bind 0.0.0.0:8000
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute getting started guide
- **[COMPLETE_DOCUMENTATION.md](COMPLETE_DOCUMENTATION.md)** - Full project documentation
- **[FILE_UPLOAD_SYSTEM.md](FILE_UPLOAD_SYSTEM.md)** - File upload system details
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Comprehensive testing procedures
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What was implemented
- **[SETUP_GUIDE.md](property_management/SETUP_GUIDE.md)** - Installation steps
- **[DATABASE_OPTIONS.md](property_management/DATABASE_OPTIONS.md)** - Database deployment options
- **[DATA_IMPORT_ANALYSIS.md](DATA_IMPORT_ANALYSIS.md)** - Excel file structure analysis

## 🗂️ Sample Data

The system includes sample data from an actual Excel file:

- **Housing Unit**: Unit 22
- **Occupant**: Michael M. Tama
- **Department**: Finance
- **Section**: P-7 Property
- **Building**: Abra
- **Inventory Items**: 16 items including sofas, chairs, beds, tables, cabinets, etc.

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Django | 4.2.8 LTS |
| Database | PostgreSQL | 15 |
| Python | Python | 3.13 |
| Database Driver | psycopg | 3.2.2 |
| Excel Reader | xlrd | 2.0.2 |
| Environment | python-dotenv | 1.0.0 |
| Containerization | Docker | Latest |

## 📊 API Endpoints

### Web Views
- `GET /properties/` - Property list
- `GET /properties/inventory/` - All inventory items with filtering
- `GET /properties/upload/` - Upload form
- `POST /properties/upload/` - Handle file upload
- `GET /properties/import-history/` - Import history
- `GET /properties/housing-unit/<id>/` - Unit details

### Admin Interface
- `GET/POST /admin/` - Django admin panel

## ⚙️ Configuration

### Environment Variables (.env)
```
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD="your_password"
DB_PORT=5432
DB_NAME=property_management
SECRET_KEY=your_secret_key
DEBUG=True  # Set to False for production
```

### Database Connection
```
PostgreSQL 15
Host: localhost
Port: 5432
Database: property_management
```

## 🐛 Troubleshooting

### Server Won't Start
```bash
python manage.py check
python manage.py migrate
```

### Database Connection Error
```bash
python manage.py dbshell
# Check credentials in .env
```

### File Upload Fails
- Verify file type is .xls, .xlsx, or .pdf
- Check `/uploads/` directory exists
- Ensure adequate disk space

For more troubleshooting, see [TESTING_GUIDE.md](TESTING_GUIDE.md)

## 📈 Features Implemented

✅ Django project structure
✅ PostgreSQL database integration
✅ 4 database models with relationships
✅ Excel file import with automatic data extraction
✅ SHA256 file hashing for duplicate prevention
✅ Web-based file upload interface
✅ Django admin dashboard
✅ Import history tracking
✅ Management command for batch imports
✅ Multiple database deployment options
✅ Comprehensive error handling
✅ Complete documentation

## 🔮 Future Enhancements

- PDF OCR processing with pytesseract
- CSV file support
- Automatic file monitoring
- Advanced search and filtering
- Data export (CSV, PDF reports)
- User authentication and permissions
- Email notifications on import
- Scheduled automatic imports
- API documentation (Swagger)
- Data validation rules

## 📝 License

[See LICENSE file](LICENSE)

## 👥 Support

For issues or questions:
1. Check the [TESTING_GUIDE.md](TESTING_GUIDE.md) for troubleshooting
2. Review the [COMPLETE_DOCUMENTATION.md](COMPLETE_DOCUMENTATION.md)
3. Check [QUICKSTART.md](QUICKSTART.md) for quick reference
4. Run `python manage.py check` for configuration issues

## 📌 Important Notes

- Database credentials are in `.env` (not tracked by git)
- Virtual environment is in `venv/` directory
- Uploaded files are stored in `property_management/uploads/`
- Import history is tracked in the database for audit purposes
- All imports are logged with timestamps and status

## 🎓 Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [xlrd Library](https://xlrd.readthedocs.io/)
- [psycopg Driver](https://www.psycopg.org/)

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: December 9, 2025

For a quick start, see [QUICKSTART.md](QUICKSTART.md)  
For complete details, see [COMPLETE_DOCUMENTATION.md](COMPLETE_DOCUMENTATION.md)
