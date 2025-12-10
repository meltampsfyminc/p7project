# Property Management System - Django + PostgreSQL

A comprehensive Django-based property management application with multiple database options: Host PostgreSQL, Docker PostgreSQL with persistent volume, or Supabase.

## Project Structure

```
property_management/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── .env                              # Environment variables - DATABASE CONFIGURATION HERE
├── Dockerfile                        # Docker container configuration
├── docker-compose.yml                # Docker Compose with PostgreSQL + persistent volume
├── docker-compose.host.yml           # Connect to host PostgreSQL via host.docker.internal
├── docker-compose.supabase.yml       # Supabase PostgreSQL option
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
- Docker & Docker Compose (for containerized PostgreSQL)
- PostgreSQL 12+ installed locally OR Supabase account

## Database Options

### Option 1: Host PostgreSQL (Windows - Recommended for Development)

Use your installed PostgreSQL on your Windows machine.

**Setup:**
1. Ensure PostgreSQL is running on port 5432 with user `postgres` and password `Mbt*7tbm#pg723`
2. Create database:
   ```sql
   CREATE DATABASE property_management OWNER postgres;
   ```

**In `.env` file:**
```ini
DATABASE_CHOICE=host_postgres
DB_ENGINE=django.db.backends.postgresql
DB_NAME=property_management
DB_USER=postgres
DB_PASSWORD="Mbt*7tbm#pg723"
DB_HOST=localhost
DB_PORT=5432
```

**Run locally:**
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

### Option 2: Docker PostgreSQL with Persistent Volume (Recommended for Production)

Containerized PostgreSQL with automatic data persistence.

**In `.env` file:**
```ini
DATABASE_CHOICE=docker_postgres
DB_ENGINE=django.db.backends.postgresql
DB_NAME=property_management
DB_USER=postgres
DB_PASSWORD="Mbt*7tbm#pg723"
DB_HOST=db
DB_PORT=5432
```

**Run:**
```bash
cd property_management
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

**Access:**
- Application: http://localhost:8000/properties/
- Admin: http://localhost:8000/admin/
- PostgreSQL: localhost:5432

**Persistent Volume:**
- Data is stored in `postgres_data` volume
- Data persists even after stopping containers
- To remove data: `docker-compose down -v`

---

### Option 3: Docker App with Host PostgreSQL

Run Django in Docker but connect to PostgreSQL on your Windows host machine.

**In `.env` file:**
```ini
DATABASE_CHOICE=host_postgres
DB_ENGINE=django.db.backends.postgresql
DB_NAME=property_management
DB_USER=postgres
DB_PASSWORD="Mbt*7tbm#pg723"
DB_HOST=host.docker.internal
DB_PORT=5432
```

**Run:**
```bash
cd property_management
docker-compose -f docker-compose.host.yml up -d
docker-compose -f docker-compose.host.yml exec web python manage.py migrate
docker-compose -f docker-compose.host.yml exec web python manage.py createsuperuser
```

**Note:** `host.docker.internal` is a special DNS name that resolves to the host machine's IP on Windows/Mac Docker Desktop.

---

### Option 4: Supabase PostgreSQL (Cloud)

Use Supabase's managed PostgreSQL service.

**Setup:**
1. Create account at https://supabase.com
2. Create new project (note your credentials)
3. Get connection details from Project Settings > Database

**In `.env` file:**
```ini
DATABASE_CHOICE=supabase
DB_ENGINE=django.db.backends.postgresql
DB_HOST=your-project.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_supabase_password
```

**Run locally:**
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Or with Docker:**
```bash
# Update docker-compose.supabase.yml with your Supabase credentials first
docker-compose -f docker-compose.supabase.yml up -d
```

---

## Installation & Setup

### Local Development (Option 1)

1. **Activate Virtual Environment** (Windows PowerShell):
   ```powershell
   & C:\Projects\p7project\venv\Scripts\Activate.ps1
   ```

2. **Install Dependencies:**
   ```bash
   cd property_management
   pip install -r requirements.txt
   ```

3. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Collect Static Files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

6. **Start Development Server:**
   ```bash
   python manage.py runserver
   ```

7. **Access:**
   - Application: http://127.0.0.1:8000/properties/
   - Admin Panel: http://127.0.0.1:8000/admin/

### Docker Setup (Option 2)

```bash
cd property_management

# Start services with PostgreSQL
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f web
```

### Docker with Host PostgreSQL (Option 3)

```bash
cd property_management

# Start Django container only
docker-compose -f docker-compose.host.yml up -d

# Run migrations
docker-compose -f docker-compose.host.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.host.yml exec web python manage.py createsuperuser
```

---

## Environment Variables (.env)

### Currently Used Variables

```ini
# Application Settings
DEBUG=True                           # Set to False in production
DJANGO_SECRET_KEY=...               # Your secret key

# Database Selection
DATABASE_CHOICE=host_postgres       # Options: host_postgres, docker_postgres, supabase

# Database Connection
DB_ENGINE=django.db.backends.postgresql
DB_NAME=property_management
DB_USER=postgres
DB_PASSWORD="Mbt*7tbm#pg723"
DB_HOST=localhost                   # Change based on your option
DB_PORT=5432
```

---

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

## Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f web
docker-compose logs -f db

# Access PostgreSQL
docker-compose exec db psql -U postgres -d property_management

# Remove all data (volumes)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Rebuild and start
docker-compose up --build
```

---

## Database Connection Troubleshooting

### Connection Refused

**Local PostgreSQL:**
- Ensure PostgreSQL is running
- Check port 5432 is accessible
- Verify credentials in `.env`

**Docker PostgreSQL:**
- Check container is running: `docker ps`
- Check logs: `docker-compose logs db`
- Ensure volume is mounted: `docker volume ls`

**Host PostgreSQL from Docker:**
- Use `host.docker.internal` instead of `localhost`
- Ensure Windows Firewall allows PostgreSQL

**Supabase:**
- Check credentials are correct
- Verify firewall isn't blocking connections
- Check Supabase project status

### Special Characters in Passwords

The `.env` file quotes passwords to handle special characters:
```ini
DB_PASSWORD="Mbt*7tbm#pg723"
```

This preserves special characters like `#`, `*`, `&`, etc.

---

## Admin Panel Features

Access at `/admin/` with superuser credentials

- **Property Management:** Create, read, update, delete properties
- **Filtering:** Filter by status and property type
- **Search:** Search by name, address, city
- **Bulk Actions:** Perform operations on multiple properties

---

## Models

### Property Model

| Field | Type | Notes |
|-------|------|-------|
| name | CharField(255) | Property name |
| description | TextField | Property description |
| address | CharField(255) | Street address |
| city | CharField(100) | City |
| state | CharField(100) | State/Province |
| postal_code | CharField(20) | Postal/Zip code |
| property_type | CharField(100) | House, Apartment, etc. |
| bedrooms | IntegerField | Number of bedrooms |
| bathrooms | IntegerField | Number of bathrooms |
| square_feet | IntegerField | Property size |
| price | DecimalField | Property price |
| status | CharField | Available, Rented, Sold, Maintenance |
| created_at | DateTimeField | Creation timestamp |
| updated_at | DateTimeField | Last update timestamp |

---

## Switching Databases

To switch between database options:

1. **Update `.env` file** with appropriate credentials
2. **Update docker-compose** file selection if using Docker
3. **Create database** if needed (except Supabase)
4. **Run migrations:** `python manage.py migrate`

Example - Switch from Host to Docker PostgreSQL:

```bash
# Edit .env
DATABASE_CHOICE=docker_postgres
DB_HOST=db

# Start containers
docker-compose up -d

# Migrate
docker-compose exec web python manage.py migrate
```

---

## Security Notes

⚠️ **Before Production:**

1. Change `DJANGO_SECRET_KEY` to a strong random value
2. Set `DEBUG=False`
3. Update `ALLOWED_HOSTS` in settings.py
4. Use strong database passwords
5. Enable HTTPS
6. Set up proper database backups
7. Use environment variables for all secrets
8. Don't commit `.env` to version control

---

## Useful Supabase Commands

If using Supabase, manage your database via their dashboard:
- https://app.supabase.com
- Project Settings > Database for credentials
- SQL Editor for direct database management
- Backups tab for automated backups

---

## Next Steps

1. Choose your database option and update `.env`
2. Install dependencies or start Docker
3. Run migrations
4. Create superuser
5. Add properties via admin panel
6. Visit property listing page
7. Customize templates as needed

---

For more information:
- Django: https://docs.djangoproject.com/
- PostgreSQL: https://www.postgresql.org/docs/
- Supabase: https://supabase.com/docs
- Docker: https://docs.docker.com/
