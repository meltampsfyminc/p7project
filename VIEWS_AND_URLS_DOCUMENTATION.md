# Views and URLs Documentation

This document provides an overview of the views and URL configurations for each app in the project.

## Gusali App

### Views (`gusali/views.py`)

- `building_list`: Displays a list of all buildings with filtering and search functionality.
- `building_detail`: Shows the details of a specific building and its yearly records.
- `building_upload`: Handles the upload of GUSALI report files (Excel).
- `building_report`: Displays a summary report of all buildings.
- `building_create`, `building_update`, `building_delete`: Standard CRUD views for buildings.
- `yearly_record_create`, `yearly_record_update`, `yearly_record_delete`: CRUD views for yearly building records.
- `gusali_csv_upload`: Handles CSV file uploads for bulk data import.

### URLs (`gusali/urls.py`)

- `/gusali/`: Lists all buildings.
- `/gusali/<int:pk>/`: Detail view for a building.
- `/gusali/upload/`: Upload page for GUSALI reports.
- `/gusali/report/`: Summary report page.
- `/gusali/create/`: Create a new building.
- `/gusali/<int:pk>/update/`: Update a building.
- `/gusali/<int:pk>/delete/`: Delete a building.
- `/gusali/<int:building_pk>/yearly-record/create/`: Create a yearly record.
- `/gusali/yearly-record/<int:pk>/update/`: Update a yearly record.
- `/gusali/yearly-record/<int:pk>/delete/`: Delete a yearly record.
- `/gusali/upload-csv/`: Upload page for CSV files.

## Kagamitan App

### Views (`kagamitan/views.py`)

- `item_list`: Displays a list of all items.
- `item_list_by_category`: Filters and displays items by category.
- `item_detail`: Shows the details of a specific item.
- `item_create`, `item_update`, `item_delete`: Standard CRUD views for items.
- `kagamitan_csv_upload`: Handles CSV file uploads for bulk data import.
- `item_upload`: Placeholder for Excel file upload.
- `item_report`: Displays a summary report of all items.

### URLs (`kagamitan/urls.py`)

- `/kagamitan/`: Lists all items.
- `/kagamitan/<int:pk>/`: Detail view for an item.
- `/kagamitan/create/`: Create a new item.
- `/kagamitan/<int:pk>/update/`: Update an item.
- `/kagamitan/<int:pk>/delete/`: Delete an item.
- `/kagamitan/upload-csv/`: Upload page for CSV files.
- `/kagamitan/upload/`: Placeholder for Excel upload.
- `/kagamitan/category/<str:category>/`: Lists items by category.

## Lupa App

### Views (`lupa/views.py`)

- `land_list`: Displays a list of all land properties.
- `land_detail`: Shows the details of a specific land property.
- `land_create`, `land_update`, `land_delete`: Standard CRUD views for land properties.
- `lupa_csv_upload`: Handles CSV file uploads for bulk data import.
- `land_upload`: Placeholder for Excel file upload.
- `land_report`: Displays a summary report of all land properties.

### URLs (`lupa/urls.py`)

- `/lupa/`: Lists all land properties.
- `/lupa/<int:pk>/`: Detail view for a land property.
- `/lupa/create/`: Create a new land property.
- `/lupa/<int:pk>/update/`: Update a land property.
- `/lupa/<int:pk>/delete/`: Delete a land property.
- `/lupa/upload-csv/`: Upload page for CSV files.
- `/lupa/upload/`: Placeholder for Excel upload.
- `/lupa/report/`: Summary report page.

## Plants App

### Views (`plants/views.py`)

- `plant_list`: Displays a list of all plants with filtering.
- `plant_upload`: Handles file uploads for plant data.

### URLs (`plants/urls.py`)

- `/plants/`: Lists all plants.
- `/plants/upload/`: Upload page for plant data.
- `/plants/crud/`: CRUD list view for plants.
- `/plants/crud/<int:pk>/`: CRUD detail view for a plant.
- `/plants/crud/new/`: CRUD create view for a plant.
- `/plants/crud/<int:pk>/edit/`: CRUD update view for a plant.
- `/plants/crud/<int:pk>/delete/`: CRUD delete view for a plant.

## Properties App

### Views (`properties/views.py`)

- `index`, `login_view`, `logout_view`: Authentication and landing pages.
- `dashboard`: User dashboard with statistics.
- `setup_2fa`, `view_backup_codes`: Two-factor authentication views.
- `property_list`, `inventory_list`, `housing_unit_detail`: Views for managing properties, inventory, and housing units.
- `upload_file`, `import_history`: File upload and import history views.
- `transfer_list`, `transfer_create`, `transfer_detail`, `transfer_history`: Views for managing item transfers.
- `district_search`, `district_detail`, `local_summary`: Views for searching and summarizing district and local data.

### URLs (`properties/urls.py`)

- `/properties/`: Main property list.
- `/properties/login/`, `/properties/logout/`: Authentication URLs.
- `/properties/dashboard/`: User dashboard.
- `/properties/inventory/`: Inventory list.
- `/properties/upload/`: File upload page.
- `/properties/transfers/`: Item transfer list.
- `/properties/search/district/`: District search page.

## Vehicles App

### Views (`vehicles/views.py`)

- `vehicle_list`: Displays a list of all vehicles with filtering.

### URLs (`vehicles/urls.py`)

- `/vehicles/`: Lists all vehicles.
- `/vehicles/crud/`: CRUD list view for vehicles.
- `/vehicles/crud/<int:pk>/`: CRUD detail view for a vehicle.
- `/vehicles/crud/new/`: CRUD create view for a vehicle.
- `/vehicles/crud/<int:pk>/edit/`: CRUD update view for a vehicle.
- `/vehicles/crud/<int:pk>/delete/`: CRUD delete view for a vehicle.
