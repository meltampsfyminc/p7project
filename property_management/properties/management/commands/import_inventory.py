from django.core.management.base import BaseCommand
from datetime import datetime, date
import xlrd
import hashlib
import os
from properties.models import Property, HousingUnit, PropertyInventory, ImportedFile


class Command(BaseCommand):
    help = 'Import inventory data from Excel file and track imports'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to Excel file (.xls or .xlsx)')
        parser.add_argument('--force', action='store_true', help='Force import even if already imported')
        parser.add_argument('--clear', action='store_true', help='Clear existing inventory before import')

    def handle(self, *args, **options):
        file_path = options['file_path']
        force_import = options.get('force', False)
        
        # Check if file exists
        try:
            wb = xlrd.open_workbook(file_path)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error opening file: {str(e)}'))
            return
        
        # Calculate file hash for duplicate detection
        file_hash = self._calculate_file_hash(file_path)
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)
        
        # Check if already imported (unless --force flag)
        if not force_import:
            existing_import = ImportedFile.objects.filter(file_hash=file_hash).first()
            if existing_import:
                self.stdout.write(self.style.WARNING(f'\n{"="*100}'))
                self.stdout.write(self.style.WARNING(f'FILE ALREADY IMPORTED'))
                self.stdout.write(self.style.WARNING(f'{"="*100}'))
                self.stdout.write(self.style.WARNING(f'Filename: {filename}'))
                self.stdout.write(self.style.WARNING(f'Previously imported on: {existing_import.imported_at}'))
                self.stdout.write(self.style.WARNING(f'Records imported: {existing_import.records_imported}'))
                self.stdout.write(self.style.WARNING(f'Status: {existing_import.status}'))
                self.stdout.write(self.style.WARNING(f'\nUse --force flag to re-import this file'))
                self.stdout.write(self.style.WARNING(f'{"="*100}\n'))
                return
        
        sheet = wb.sheet_by_index(0)
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*100}'))
        self.stdout.write(self.style.SUCCESS(f'IMPORTING INVENTORY DATA FROM: {file_path}'))
        self.stdout.write(self.style.SUCCESS(f'{"="*100}\n'))
        
        # Extract header information
        self.stdout.write(self.style.SUCCESS('EXTRACTING HEADER INFORMATION...'))
        
        occupant_name = sheet.cell_value(4, 12)
        department = sheet.cell_value(4, 33)
        section = sheet.cell_value(4, 42)
        job_title = sheet.cell_value(4, 54)
        
        housing_unit_name = sheet.cell_value(5, 5)
        building_name = sheet.cell_value(5, 14)
        floor = sheet.cell_value(5, 17)
        unit_number = sheet.cell_value(5, 22)
        address = sheet.cell_value(5, 31)
        
        # Extract unit number from housing_unit_name if unit_number is a label (e.g., "Unit no.")
        # This handles cases where the cell contains "Unit no." instead of actual number
        if unit_number and isinstance(unit_number, str) and ('Unit' in unit_number or 'unit' in unit_number):
            # Try to extract from housing_unit_name (e.g., "Unit 22" -> "22")
            try:
                unit_number = int(''.join(filter(str.isdigit, housing_unit_name)))
            except (ValueError, AttributeError):
                unit_number = housing_unit_name
        
        # Set default floor to 1 if blank or if it's a label like "Floor:"
        if not floor or floor == '' or 'Floor' in str(floor):
            floor = 1
        else:
            try:
                floor = int(floor)
            except (ValueError, TypeError):
                floor = 1
        
        date_str = sheet.cell_value(1, 47)
        date_reported = self._extract_date(date_str)
        
        self.stdout.write(f'Occupant: {occupant_name}')
        self.stdout.write(f'Department: {department}')
        self.stdout.write(f'Section: {section}')
        self.stdout.write(f'Job Title: {job_title}')
        self.stdout.write(f'Housing Unit: {housing_unit_name}')
        self.stdout.write(f'Building: {building_name}')
        self.stdout.write(f'Address: {address}')
        self.stdout.write(f'Date Reported: {date_reported}\n')
        
        # Clear existing if requested
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing inventory...'))
            PropertyInventory.objects.all().delete()
        
        # Create or get Property first
        # Try to find existing property by building name and address
        property_obj = Property.objects.filter(
            name=building_name,
            address=address
        ).first()
        
        property_created = False
        if not property_obj:
            # If not found, try by name only (in case address was slightly different)
            property_obj = Property.objects.filter(
                name=building_name
            ).first()
            
            if not property_obj:
                # Try partial match for building name (e.g., "Abra" matches "Abra Building")
                property_obj = Property.objects.filter(
                    name__icontains=building_name
                ).first()
            
            if not property_obj:
                # Create new property if not found
                property_obj = Property.objects.create(
                    name=building_name,
                    owner=occupant_name if occupant_name else 'Unknown',
                    address=address if address else '',
                    city='',
                    property_type='Building',
                    total_units=1,
                )
                property_created = True
                self.stdout.write(self.style.SUCCESS(f'✓ Created new Property: {property_obj}'))
                self.stdout.write(f'  Owner: {occupant_name}')
                self.stdout.write(f'  Address: {address}')
            else:
                self.stdout.write(self.style.SUCCESS(f'✓ Found existing Property: {property_obj}'))
                # Update address if it was empty
                if not property_obj.address and address:
                    property_obj.address = address
                    property_obj.save()
                    self.stdout.write(f'  Updated address: {address}')
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Found existing Property: {property_obj}'))
        
        # Create or get HousingUnit
        self.stdout.write(self.style.SUCCESS('CREATING/UPDATING HOUSING UNIT...'))
        housing_unit, created = HousingUnit.objects.get_or_create(
            housing_unit_name=housing_unit_name,
            unit_number=unit_number,
            property=property_obj,
            defaults={
                'occupant_name': occupant_name,
                'department': department,
                'section': section,
                'job_title': job_title,
                'date_reported': date_reported or datetime.now().date(),
                'floor': floor,
                'address': address,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created new Housing Unit: {housing_unit}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Using existing Housing Unit: {housing_unit}'))
        
        # Extract inventory items
        self.stdout.write(self.style.SUCCESS(f'\nEXTRACTING INVENTORY ITEMS...'))
        self.stdout.write('-' * 100)
        
        inventory_count = 0
        skipped_count = 0
        
        # Column mapping
        col_date_acquired = 3
        col_qty = 7
        col_item_name = 9
        col_make = 32
        col_color = 37
        col_size = 42
        col_remarks = 52
        
        for row_idx in range(9, sheet.nrows):
            try:
                date_acquired_val = sheet.cell_value(row_idx, col_date_acquired)
                qty = sheet.cell_value(row_idx, col_qty)
                item_name = sheet.cell_value(row_idx, col_item_name)
                
                if not item_name or item_name.strip() == '':
                    continue
                
                # Handle date_acquired - convert to a proper date
                if isinstance(date_acquired_val, float):
                    # If it's a float, treat it as year
                    year = int(date_acquired_val)
                    date_acquired = date(year, 1, 1)
                elif isinstance(date_acquired_val, int):
                    # If it's an int, treat it as year
                    date_acquired = date(date_acquired_val, 1, 1)
                elif isinstance(date_acquired_val, str):
                    # If it's a string, try to parse it
                    try:
                        date_acquired = datetime.strptime(date_acquired_val, '%Y-%m-%d').date()
                    except:
                        # If parsing fails, use 2024
                        date_acquired = date(2024, 1, 1)
                else:
                    # Default to 2024
                    date_acquired = date(2024, 1, 1)
                
                if isinstance(qty, float):
                    quantity = int(qty)
                else:
                    quantity = 1
                
                make = sheet.cell_value(row_idx, col_make)
                color = sheet.cell_value(row_idx, col_color)
                size = sheet.cell_value(row_idx, col_size)
                remarks = sheet.cell_value(row_idx, col_remarks)
                
                inventory_item = PropertyInventory.objects.create(
                    housing_unit=housing_unit,
                    date_acquired=date_acquired,
                    quantity=quantity,
                    item_name=item_name,
                    make=make,
                    color=color,
                    size=size,
                    remarks=remarks,
                )
                
                self.stdout.write(f'✓ Row {row_idx}: {item_name} (Qty: {quantity})')
                inventory_count += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Row {row_idx}: Error - {str(e)}'))
                skipped_count += 1
                continue
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*100}'))
        self.stdout.write(self.style.SUCCESS('IMPORT COMPLETE'))
        self.stdout.write(self.style.SUCCESS(f'{"="*100}'))
        self.stdout.write(self.style.SUCCESS(f'Housing Units: 1'))
        self.stdout.write(self.style.SUCCESS(f'Inventory Items Created: {inventory_count}'))
        self.stdout.write(self.style.WARNING(f'Rows Skipped: {skipped_count}'))
        self.stdout.write(self.style.SUCCESS(f'Total Items: {inventory_count}'))
        self.stdout.write(self.style.SUCCESS(f'{"="*100}\n'))
        
        # Save or update import record for tracking
        status = 'partial' if skipped_count > 0 else 'success'
        ImportedFile.objects.update_or_create(
            file_hash=file_hash,
            defaults={
                'filename': filename,
                'file_size': file_size,
                'records_imported': inventory_count,
                'status': status,
                'error_message': f'Skipped {skipped_count} rows' if skipped_count > 0 else ''
            }
        )
        
        self.stdout.write(self.style.SUCCESS(f'Import record saved for duplicate detection'))
        self.stdout.write(self.style.SUCCESS(f'File Hash: {file_hash}'))



    def _calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of file for duplicate detection"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error calculating file hash: {str(e)}'))
            raise

    def _extract_date(self, date_str):
        """Convert date string to Python date object"""
        try:
            for fmt in ['%B %d, %Y', '%b %d, %Y', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(str(date_str).strip(), fmt).date()
                except ValueError:
                    continue
            return None
        except:
            return None
