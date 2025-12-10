# Django Property Management - Setup Guide

## ✅ Installation Status

All Python dependencies are installed and Django is verified! 

**Installed packages:**
- Django 4.2.8 ✅
- psycopg 3.2.2 (PostgreSQL adapter) ✅
- python-dotenv 1.0.0 ✅

## Next Steps - Choose Your Database Option

### Option 1: Use Your Host PostgreSQL (Recommended for Development)

**Current Setup:** `.env` is configured for `localhost:5432`

#### Step 1: Create PostgreSQL Database

Open PostgreSQL command line (psql) and run:

```sql
-- Connect as superuser first
-- Then create the database and user:

CREATE DATABASE property_management;

-- Verify it was created:
\l
```

**Or use Windows CMD:**
```cmd
psql -U postgres -h localhost -p 5432 -c "CREATE DATABASE property_management;"
```

#### Step 2: Run Django Migrations

```powershell
cd C:\Projects\p7project\property_management
python manage.py migrate
```

#### Step 3: Create Superuser (Admin Account)

```powershell
python manage.py createsuperuser
```

When prompted:
- Username: (choose your admin username)
- Email: (your email)
- Password: (your admin password)

#### Step 4: Start Development Server

```powershell
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

#### Step 5: Access Application

- **Properties:** http://127.0.0.1:8000/properties/
- **Admin Panel:** http://127.0.0.1:8000/admin/

---

### Option 2: Use Docker PostgreSQL with Persistent Volume

#### Step 1: Start Docker Services

```powershell
cd C:\Projects\p7project\property_management
docker-compose up -d
```

This will:
- Pull PostgreSQL 15 Alpine image
- Create persistent volume `postgres_data`
- Create Django web container
- Create Docker network

#### Step 2: Wait for Database to Start

```powershell
docker-compose logs db
# Wait until you see: "database system is ready to accept connections"
```

#### Step 3: Run Migrations

```powershell
docker-compose exec web python manage.py migrate
```

#### Step 4: Create Superuser

```powershell
docker-compose exec web python manage.py createsuperuser
```

#### Step 5: Access Application

- **Properties:** http://localhost:8000/properties/
- **Admin Panel:** http://localhost:8000/admin/

**Useful Docker Commands:**
```powershell
# View logs
docker-compose logs -f web
docker-compose logs -f db

# Access PostgreSQL directly
docker-compose exec db psql -U postgres -d property_management

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

### Option 3: Docker App Connected to Host PostgreSQL

#### Step 1: Update .env

```ini
DB_HOST=host.docker.internal
```

#### Step 2: Start Docker App Only

```powershell
cd C:\Projects\p7project\property_management
docker-compose -f docker-compose.host.yml up -d
```

#### Step 3: Run Migrations

```powershell
docker-compose -f docker-compose.host.yml exec web python manage.py migrate
```

#### Step 4: Create Superuser

```powershell
docker-compose -f docker-compose.host.yml exec web python manage.py createsuperuser
```

#### Step 5: Access Application

- **Properties:** http://localhost:8000/properties/
- **Admin Panel:** http://localhost:8000/admin/

---

## Troubleshooting

### PostgreSQL Connection Error

**Error:** `connection to server at "127.0.0.1", port 5432 failed`

**Solutions:**
1. Ensure PostgreSQL is running
   - Windows: Open pgAdmin or Services
   - Check port 5432 is listening: `netstat -an | findstr 5432`

2. Create the database (if not exists):
   ```sql
   CREATE DATABASE property_management;
   ```

3. Verify credentials in `.env`:
   - Username: `postgres`
   - Password: `"Mbt*7tbm#pg723"` (with quotes)
   - Host: `localhost`
   - Port: `5432`

### Database Already Exists

Skip database creation, just run:
```powershell
python manage.py migrate
```

### Port Already in Use

If port 8000 is in use:
```powershell
python manage.py runserver 8080
# Access at http://127.0.0.1:8080/
```

### Docker Connection Issues

```powershell
# Check container status
docker ps

# View logs
docker-compose logs db

# Restart services
docker-compose restart
```

---

## Quick Reference

### Local Development (Host PostgreSQL)

```powershell
# Activate virtual environment
& C:\Projects\p7project\venv\Scripts\Activate.ps1

# Navigate to project
cd C:\Projects\p7project\property_management

# Run migrations
python manage.py migrate

# Create admin account
python manage.py createsuperuser

# Start server
python manage.py runserver

# Access at http://127.0.0.1:8000/
```

### Docker Development (PostgreSQL in Container)

```powershell
# Start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create admin account
docker-compose exec web python manage.py createsuperuser

# View logs
docker-compose logs -f web

# Access at http://localhost:8000/
```

---

## Admin Panel Features

Once logged in at http://127.0.0.1:8000/admin/:

1. **Add Properties:** Click "Properties" → "Add Property"
2. **View Properties:** Click "Properties" to see all
3. **Edit Properties:** Click on any property to edit
4. **Filter:** Use status and property type filters
5. **Search:** Search by name, address, or city

---

## Next: Add Some Properties

1. Go to Admin: http://127.0.0.1:8000/admin/
2. Click "Properties" → "Add Property"
3. Fill in details:
   - Name: "Beautiful Downtown Loft"
   - Address: "123 Main St"
   - City: "New York"
   - State: "NY"
   - Postal Code: "10001"
   - Property Type: "Apartment"
   - Bedrooms: 2
   - Bathrooms: 1
   - Square Feet: 1200
   - Price: 2500000
   - Status: "Available"
4. Click Save

4. Visit http://127.0.0.1:8000/properties/ to see your property!

---

## Environment Variables

Current `.env` configuration:

```ini
# Django
DEBUG=True
DJANGO_SECRET_KEY=xTbqn)XanfeUtcTwAk0RQvXo(kbL6Y4%s*Sg)-5^Ux=XdC^e%

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=property_management
DB_USER=postgres
DB_PASSWORD="Mbt*7tbm#pg723"
DB_HOST=localhost
DB_PORT=5432
```

To switch options, edit `DB_HOST`:
- Local: `localhost`
- Docker: `db`
- Host from Docker: `host.docker.internal`

---

## Production Checklist

Before deploying:
- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate new `DJANGO_SECRET_KEY`
- [ ] Use strong database password
- [ ] Configure `ALLOWED_HOSTS` in settings.py
- [ ] Set up HTTPS
- [ ] Configure static/media files properly
- [ ] Set up database backups
- [ ] Use strong admin password

---

## Support

For detailed information, see:
- `DATABASE_OPTIONS.md` - All database configuration options
- `README.md` - Full project documentation
