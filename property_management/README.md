# Property Management System - Django + PostgreSQL

A comprehensive Django-based property management application with PostgreSQL database.

## Project Structure

```
property_management/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── .env                              # Environment variables (configure here)
├── Dockerfile                        # Docker container configuration
├── docker-compose.yml                # Docker Compose setup
├── property_management/              # Main Django project
│   ├── __init__.py
│   ├── settings.py                   # Django settings with PostgreSQL config
│   ├── urls.py                       # URL routing
│   ├── asgi.py                       # ASGI config
│   └── wsgi.py                       # WSGI config
├── properties/                       # Properties application
│   ├── models.py                     # Property data model
│   ├── views.py                      # View logic
│   ├── urls.py                       # App URL routing
│   ├── admin.py                      # Django admin configuration
│   ├── apps.py                       # App configuration
│   └── __init__.py
└── templates/                        # HTML templates
    └── properties/
        └── property_list.html        # Property listing page
```

## Prerequisites

- Python 3.11+
- PostgreSQL 12+ (or use Docker)
- pip (Python package manager)

## Setup Instructions

### Option 1: Local Setup (Without Docker)

1. **Install PostgreSQL**
   - Download and install PostgreSQL from https://www.postgresql.org/download/
   - Note: Port should be 5432 (default)

2. **Create PostgreSQL User and Database**
   ```sql
   -- Connect to PostgreSQL as admin
   -- Run these commands:
   CREATE USER postgres WITH PASSWORD 'Mbt*7tbm#pg723';
   ALTER USER postgres CREATEDB;
   CREATE DATABASE property_management OWNER postgres;
   ```

3. **Activate Virtual Environment** (Windows PowerShell)
   ```powershell
   & C:\Projects\p7project\venv\Scripts\Activate.ps1
   ```

4. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser (Admin Account)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

9. **Access the Application**
   - Application: http://127.0.0.1:8000/properties/
   - Admin Panel: http://127.0.0.1:8000/admin/

### Option 2: Docker Setup (Recommended)

1. **Build and Run with Docker Compose**
   ```bash
   cd property_management
   docker-compose up -d
   ```

2. **Run Migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create Superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Access the Application**
   - Application: http://localhost:8000/properties/
   - Admin Panel: http://localhost:8000/admin/

## Database Configuration

### PostgreSQL Connection Details

- **Host:** localhost (or `db` if using Docker)
- **Port:** 5432
- **Username:** postgres
- **Password:** Mbt*7tbm#pg723
- **Database:** property_management

All credentials are stored in the `.env` file and can be modified as needed.

## Available Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Collect static files
python manage.py collectstatic

# Access Django shell
python manage.py shell

# Run tests
python manage.py test

# Check for problems
python manage.py check
```

## Admin Panel Features

The Django admin panel (`/admin/`) includes:

- **Property Management:** Create, read, update, and delete properties
- **Filtering:** Filter by status and property type
- **Search:** Search properties by name, address, or city
- **Bulk Actions:** Perform operations on multiple properties

## Models

### Property Model

Fields:
- `name` - Property name
- `description` - Property description
- `address` - Street address
- `city` - City
- `state` - State/Province
- `postal_code` - Postal/Zip code
- `property_type` - Type (e.g., House, Apartment, Commercial)
- `bedrooms` - Number of bedrooms
- `bathrooms` - Number of bathrooms
- `square_feet` - Property size in square feet
- `price` - Property price
- `status` - Status (Available, Rented, Sold, Maintenance)
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## Troubleshooting

### PostgreSQL Connection Error
- Ensure PostgreSQL is running on port 5432
- Verify credentials in `.env` file
- Check that the `property_management` database exists

### Module Not Found Errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

### Migration Errors
- Run `python manage.py makemigrations`
- Then run `python manage.py migrate`

## Docker Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove all containers and volumes
docker-compose down -v

# Rebuild images
docker-compose build --no-cache
```

## Environment Variables (.env)

```
DEBUG=True                           # Enable debug mode (False in production)
DJANGO_SECRET_KEY=<your-key>        # Django secret key
DB_ENGINE=django.db.backends.postgresql
DB_NAME=property_management
DB_USER=postgres
DB_PASSWORD=Mbt*7tbm#pg723
DB_HOST=localhost
DB_PORT=5432
```

## Security Notes

⚠️ **Important:** Before deploying to production:
1. Change `DJANGO_SECRET_KEY` to a strong random value
2. Set `DEBUG=False`
3. Use strong passwords for database users
4. Configure `ALLOWED_HOSTS` appropriately
5. Use environment variables for sensitive data
6. Enable HTTPS
7. Set up proper database backups

## Next Steps

1. Access the admin panel and create some properties
2. Visit the property listing page to see them displayed
3. Customize the templates in `templates/` directory
4. Extend the Property model with additional fields as needed
5. Create additional views and APIs for more functionality

---

For more information, visit [Django Documentation](https://docs.djangoproject.com/)
