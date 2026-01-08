# Project CRUD Documentation

This document outlines the CRUD (Create, Read, Update, Delete) modules for all applications within the project.

## Applications

The following applications have full CRUD functionality:

- **Gusali:** Manages building information.
- **Kagamitan:** Manages equipment and materials.
- **Lupa:** Manages land properties.
- **Plants:** Manages plants and agricultural data.
- **Properties:** Manages general property information.
- **Vehicles:** Manages vehicle records.

## CRUD Implementation Details

Each application follows a consistent pattern for its CRUD implementation:

- **`crud.py`:** Contains the view functions for handling CRUD operations.
- **`urls.py`:** Maps the URLs to the corresponding CRUD views.
- **`forms.py`:** Defines the forms used for creating and updating data.
- **`models.py`:** Defines the data models for the application.
- **`templates/`:** Contains the HTML templates for the list, detail, form, and confirmation pages.

### Generic CRUD

The `properties` app utilizes a generic CRUD implementation to handle its numerous models. This approach reduces code duplication and simplifies maintenance.

## Main URLs

The main `urls.py` file has been updated to include the URLs for each application's CRUD module.
