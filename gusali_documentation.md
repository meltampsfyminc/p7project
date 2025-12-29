# Gusali (Building) Report Module Documentation

## Overview

The `gusali` app is a Django module designed to manage building and property data, importing from the "GUSALI REPORT.xlsx" format. It tracks building details, costs, yearly records, and modifications.

## Key Features

1.  **Building Inventory Management**: Tracks core building info (code, name, classification, donation status, ownership, costs).
2.  **Yearly Record Tracking**: Records annual cost changes (construction, renovation, repairs, removed items).
3.  **Excel Import**: Automated import command for standard `GUSALI REPORT.xlsx` files.
4.  **Reporting**: Summary reports and list views with filtering by district, local, code, and year.
5.  **Search & Filter**: Robust search functionality by district code, district name, local code, and local name.

## Models

### `Building`
Stores static and current status of a building.
*   **Fields**: `code`, `name`, `classification`, `is_donated`, `original_cost`, `current_total_cost`, `local` (ForeignKey), etc.

### `BuildingYearlyRecord`
Stores historical data for specific years.
*   **Fields**: `year`, `cost_last_year`, `construction_cost`, `renovation_cost`, `total_added`, `year_end_total`, etc.

## Usage

### Web Interface

*   **Building List**: `http://localhost:7323/gusali/`
    *   View all buildings.
    *   Filter by District, Local, Code, Year.
    *   Search by dcode, distrito, lcode, lokal.
*   **Upload Report**: `http://localhost:7323/gusali/upload/`
    *   Upload `GUSALI REPORT.xlsx` files via drag-and-drop.
*   **Summary Report**: `http://localhost:7323/gusali/report/`

### Management Command

To import data from the CLI:

```bash
python manage.py import_gusali "path/to/gusali_Balayan_Batangas.xls"
```

**Filename Convention:**
*   The command automatically detects the Local and District from the filename: `gusali_{Lokal}_{District}.xls` (e.g., `gusali_Balayan_Batangas.xls`).
*   If the Local is found in the database, it will be automatically associated with the imported buildings.

**Options:**
*   `--force`: Overwrite existing records if duplicates are found based on file hash.
*   `--clear`: Delete all existing building data before importing (Use with caution).
*   `--local <lcode>`: Manually assign a specific local code (overrides filename detection).

## detailed Implementation Info

For developer details, refer to the source code in `property_management/gusali/`.
