# ---- Base Stage ----
# Use a specific version for reproducibility and a slim variant for size.
FROM python:3.11-slim as base

# Set environment variables to prevent Python from writing .pyc files and to run in unbuffered mode.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies
# - postgresql-client: For interacting with PostgreSQL.
# - tesseract-ocr: Required by pytesseract for OCR functionality.
# - poppler-utils: Required by pdf2image for PDF processing.
RUN apt-get update && apt-get install -y \
    postgresql-client \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# ---- Builder Stage ----
# This stage builds the Python dependencies to leverage caching.
FROM base as builder

# Copy only the requirements file to leverage Docker cache.
COPY requirements.txt .

# Build wheel files for all dependencies.
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# ---- Final Stage ----
# This is the final, lean image for the application.
FROM base as final

# Create a non-root user and group for security.
RUN addgroup --system app && adduser --system --ingroup app app

# Copy pre-built wheels and install them.
COPY --from=builder /app/wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# Switch to the application's directory and copy source code.
WORKDIR /home/app/web
COPY . .

# Change ownership to the non-root user.
RUN chown -R app:app /home/app

# Collect static files
RUN python manage.py collectstatic --noinput

# Switch to the non-root user.
USER app

EXPOSE 8000

# Use Gunicorn as the WSGI server for production.
# The 'runserver' command is not suitable for production.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "property_management.wsgi:application"]
