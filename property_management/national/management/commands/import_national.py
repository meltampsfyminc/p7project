# Replace the process_page3, process_page4, process_page5 methods in your P7Importer class
# Also update the create_summaries method

# ============================================================================
# ADD THESE THREE METHODS TO REPLACE THE EMPTY STUBS IN P7Importer CLASS
# ============================================================================

from email.utils import parsedate
from property_management.national.models import Chapel, ItemRemoved, Land, OfficeBuilding, OtherBuilding, PastoralHouse, Plant, ReportSummary, Vehicle, VehicleSummary


def process_page3(self, df):
    """Process PAGE 3 - Added Items (Approved additions)."""
    items_created = 0
    current_kaukulan = None
    
    # Find header row
    header_row_idx = None
    for idx, row in df.iterrows():
        row_text = ' '.join([str(cell).upper() for cell in row[:15] if str(cell).strip()])
        if 'IIN' in row_text and ('DATE' in row_text or 'QTY' in row_text):
            header_row_idx = idx
            break
    
    if header_row_idx is None:
        if self.debug:
            print("  Warning: Could not find header row in PAGE 3")
        return 0
    
    # Process data rows
    for idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[idx]
        first_cell = str(row[0]).strip() if len(row) > 0 else ''
        
        # Skip empty rows
        if not any(str(cell).strip() for cell in row[:10]):
            continue
        
        # Check for section/kaukulan headers
        if (first_cell and 
            len(first_cell) < 100 and
            not any(char.isdigit() for char in first_cell[:5]) and
            not any(marker in first_cell.upper() for marker in ['IIN', 'DATE', 'QTY', 'BRAND'])):
            if any(word in first_cell.upper() for word in ['KAPILYA', 'KORO', 'TRIBUNAL', 'MAINHALL', 'BODEGA', 'LOBBY']):
                current_kaukulan = first_cell
                continue
        
        # Check if this row has IIN code
        if first_cell and '-' in first_cell and any(char.isdigit() for char in first_cell):
            item_data = {
                'kaukulan': current_kaukulan,
                'iin_code': first_cell,
                'date_received': parsedate(str(row[1]).strip()) if len(row) > 1 else None,
            }
            
            # Find quantity
            qty_idx = None
            for i in range(2, 10):
                if i < len(row):
                    cell_str = str(row[i]).strip()
                    if cell_str and cell_str.isdigit():
                        item_data['qty'] = int(cell_str)
                        qty_idx = i
                        break
            
            # Brand/Make/Color/Size/Serial
            if qty_idx:
                # Scan columns after qty for attributes
                for col_idx in range(qty_idx + 1, min(len(row), 50)):
                    cell_str = str(row[col_idx]).strip()
                    if not cell_str:
                        continue
                    
                    # Skip numbers (prices/amounts)
                    if clean_num(cell_str):
                        if 'unit_price' not in item_data:
                            item_data['unit_price'] = clean_num(cell_str)
                        elif 'amount' not in item_data:
                            item_data['amount'] = clean_num(cell_str)
                        continue
                    
                    # Store first few text values as brand, make, color, size, serial
                    if 'brand' not in item_data and len(cell_str) < 100:
                        item_data['brand'] = cell_str[:255]
                    elif 'make' not in item_data and len(cell_str) < 100:
                        item_data['make'] = cell_str[:255]
                    elif 'color' not in item_data and any(color in cell_str.lower() for color in ['brown', 'black', 'white', 'blue', 'red', 'green', 'gray', 'yellow']):
                        item_data['color'] = cell_str[:255]
                    elif 'size' not in item_data and any(unit in cell_str.lower() for unit in ['m', 'cm', 'inch', '"', 'sq', 'x']):
                        item_data['size'] = cell_str[:255]
                    elif 'serial_number' not in item_data:
                        item_data['serial_number'] = cell_str[:255]
            
            # Look for approval number in later columns
            for col_idx in range(40, min(len(row), 100)):
                cell_str = str(row[col_idx]).strip()
                if cell_str and len(cell_str) > 2 and len(cell_str) < 50:
                    if 'approval_number' not in item_data:
                        item_data['approval_number'] = cell_str[:100]
                        break
            
            # Create record
            ItemAdded.objects.create(
                report=self.report,
                **item_data
            )
            items_created += 1
    
    if self.debug:
        print(f"  Created {items_created} added items")
    
    return items_created


def process_page4(self, df):
    """Process PAGE 4 - Removed Items."""
    items_created = 0
    
    # Find header row
    header_row_idx = None
    for idx, row in df.iterrows():
        row_text = ' '.join([str(cell).upper() for cell in row[:15] if str(cell).strip()])
        if 'IIN' in row_text or ('SOURCE' in row_text and 'DATE' in row_text):
            header_row_idx = idx
            break
    
    if header_row_idx is None:
        if self.debug:
            print("  Warning: Could not find header row in PAGE 4")
        return 0
    
    # Process data rows
    for idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[idx]
        first_cell = str(row[0]).strip() if len(row) > 0 else ''
        
        # Skip empty rows
        if not any(str(cell).strip() for cell in row[:10]):
            continue
        
        # Check if this row has IIN code or source
        if first_cell and (('-' in first_cell and any(char.isdigit() for char in first_cell)) or len(first_cell) > 5):
            item_data = {
                'source_place': first_cell,
                'date_received': parse_date(str(row[1]).strip()) if len(row) > 1 else None,
            }
            
            # Look for IIN in subsequent columns
            for i in range(1, min(len(row), 10)):
                cell_str = str(row[i]).strip()
                if '-' in cell_str and any(char.isdigit() for char in cell_str):
                    item_data['iin_code'] = cell_str
                    break
            
            # Find quantity
            qty_idx = None
            for i in range(2, 10):
                if i < len(row):
                    cell_str = str(row[i]).strip()
                    if cell_str and cell_str.isdigit():
                        item_data['qty'] = int(cell_str)
                        qty_idx = i
                        break
            
            # Find amounts
            for col_idx in range(qty_idx + 1 if qty_idx else 2, min(len(row), 50)):
                cell_str = str(row[col_idx]).strip()
                n = clean_num(cell_str)
                if n:
                    if 'unit_price' not in item_data:
                        item_data['unit_price'] = n
                    elif 'amount' not in item_data:
                        item_data['amount'] = n
                        break
            
            # Look for reason and approval number in later columns
            text_columns = []
            for col_idx in range(max(10, qty_idx + 3) if qty_idx else 10, min(len(row), 100)):
                cell_str = str(row[col_idx]).strip()
                if cell_str and not clean_num(cell_str) and len(cell_str) > 2:
                    text_columns.append(cell_str[:255])
            
            if text_columns:
                item_data['reason'] = text_columns[0]  # First text is reason
            if len(text_columns) > 1:
                item_data['approval_number'] = text_columns[1]  # Second text is approval
            
            # Create record
            ItemRemoved.objects.create(
                report=self.report,
                **item_data
            )
            items_created += 1
    
    if self.debug:
        print(f"  Created {items_created} removed items")
    
    return items_created


def process_page5(self, df):
    """Process PAGE 5 - Land, Plants, Vehicles."""
    items_created = 0
    section = None
    
    for idx, row in df.iterrows():
        row_text = ' '.join([str(cell) for cell in row[:10] if str(cell).strip()])
        row_upper = row_text.upper()
        
        # Skip empty rows
        if not row_text.strip():
            continue
        
        # Detect sections
        if 'LUPA' in row_upper or 'LAND' in row_upper:
            section = 'land'
            continue
        elif 'PUNO' in row_upper or 'PLANT' in row_upper or 'HALAMAN' in row_upper:
            section = 'plant'
            continue
        elif 'SASAKYAN' in row_upper or 'VEHICLE' in row_upper or 'KOTSE' in row_upper:
            section = 'vehicle'
            continue
        
        # Process based on section
        if section == 'land' and any(str(cell).strip() for cell in row[:5]):
            # Extract land address, area, date, value
            address = str(row[0]).strip() if len(row) > 0 else ''
            
            if address and len(address) > 3 and not any(marker in address.upper() for marker in ['TOTAL', 'SUMMARY', 'PAGE']):
                land_data = {
                    'address': address[:255],
                    'category': 'existing'
                }
                
                # Extract area, date, value
                nums = []
                date_val = None
                for i in range(1, len(row)):
                    cell_str = str(row[i]).strip()
                    if cell_str:
                        # Try to parse as date
                        if not date_val:
                            date_val = parse_date(cell_str)
                            if date_val:
                                land_data['date_acquired'] = date_val
                                continue
                        
                        # Try to parse as number
                        n = clean_num(cell_str)
                        if n:
                            nums.append(n)
                
                # First number is usually area, last is value
                if len(nums) >= 1:
                    land_data['area_sqm'] = nums[0]
                if len(nums) >= 2:
                    land_data['value'] = nums[-1]
                elif len(nums) == 1 and 'area_sqm' not in land_data:
                    land_data['value'] = nums[0]
                
                if 'address' in land_data:
                    Land.objects.create(
                        report=self.report,
                        **land_data
                    )
                    items_created += 1
        
        elif section == 'plant' and any(str(cell).strip() for cell in row[:5]):
            # Extract plant name, quantities, values
            plant_name = str(row[0]).strip() if len(row) > 0 else ''
            
            if plant_name and len(plant_name) > 2 and not any(marker in plant_name.upper() for marker in ['TOTAL', 'SUMMARY', 'PAGE']):
                plant_data = {
                    'name': plant_name[:255],
                }
                
                # Extract numbers (quantities and values)
                nums = []
                for i in range(1, len(row)):
                    cell_str = str(row[i]).strip()
                    n = clean_num(cell_str)
                    if n:
                        nums.append(n)
                
                # Assuming: last_qty, last_value, this_qty, this_value, sub_qty, sub_value, total
                if len(nums) >= 1:
                    plant_data['last_year_qty'] = int(nums[0])
                if len(nums) >= 2:
                    plant_data['last_year_value'] = nums[1]
                if len(nums) >= 3:
                    plant_data['this_year_qty'] = int(nums[2])
                if len(nums) >= 4:
                    plant_data['this_year_value'] = nums[3]
                if len(nums) >= 5:
                    plant_data['sub_qty'] = int(nums[4])
                if len(nums) >= 6:
                    plant_data['sub_value'] = nums[5]
                if len(nums) >= 7:
                    plant_data['total_value_current'] = nums[6]
                
                if 'name' in plant_data:
                    Plant.objects.create(
                        report=self.report,
                        **plant_data
                    )
                    items_created += 1
        
        elif section == 'vehicle' and any(str(cell).strip() for cell in row[:5]):
            # Extract vehicle make/type, plate, year, date, cost
            make_type = str(row[0]).strip() if len(row) > 0 else ''
            
            if make_type and len(make_type) > 2 and not any(marker in make_type.upper() for marker in ['TOTAL', 'SUMMARY', 'PAGE']):
                vehicle_data = {
                    'make_type': make_type[:255],
                    'category': 'existing'
                }
                
                # Extract plate, year, date, cost
                for i in range(1, len(row)):
                    cell_str = str(row[i]).strip()
                    if not cell_str:
                        continue
                    
                    # Check if it's a plate number (contains letters/numbers)
                    if '-' in cell_str and len(cell_str) < 20 and any(c.isalpha() for c in cell_str):
                        if 'plate_number' not in vehicle_data:
                            vehicle_data['plate_number'] = cell_str[:50]
                            continue
                    
                    # Check if it's a year (4 digits)
                    if cell_str.isdigit() and len(cell_str) == 4:
                        if 'year_model' not in vehicle_data:
                            vehicle_data['year_model'] = int(cell_str)
                            continue
                    
                    # Check if it's a date
                    date_val = parse_date(cell_str)
                    if date_val and 'date_purchased' not in vehicle_data:
                        vehicle_data['date_purchased'] = date_val
                        continue
                    
                    # Check if it's a number (cost/price)
                    n = clean_num(cell_str)
                    if n and 'cost' not in vehicle_data:
                        vehicle_data['cost'] = n
                
                if 'make_type' in vehicle_data:
                    Vehicle.objects.create(
                        report=self.report,
                        **vehicle_data
                    )
                    items_created += 1
    
    if self.debug:
        print(f"  Processed PAGE 5 sections - created {items_created} land/plant/vehicle records")
    
    return items_created


# ============================================================================
# REPLACE THE create_summaries METHOD WITH THIS UPDATED VERSION
# ============================================================================

def create_summaries(self):
    """Create all summary records with proper data aggregation."""
    from decimal import Decimal
    
    # PAGE 1 SUMMARY
    total_chapels = Chapel.objects.filter(report=self.report).aggregate(
        total=djmodels.Sum('total_cost_this_year'))['total'] or Decimal(0)
    total_pastoral = PastoralHouse.objects.filter(report=self.report).aggregate(
        total=djmodels.Sum('total_cost'))['total'] or Decimal(0)
    total_offices = OfficeBuilding.objects.filter(report=self.report).aggregate(
        total=djmodels.Sum('total_cost'))['total'] or Decimal(0)
    total_other = OtherBuilding.objects.filter(report=self.report).aggregate(
        total=djmodels.Sum('total_cost'))['total'] or Decimal(0)
    
    p1_grand_total = total_chapels + total_pastoral + total_offices + total_other
    
    Page1Summary.objects.update_or_create(
        report=self.report,
        defaults={
            'total_chapels': total_chapels,
            'total_pastoral': total_pastoral,
            'total_offices': total_offices,
            'total_other_buildings': total_other,
            'grand_total': p1_grand_total
        }
    )
    if self.debug:
        print(f"  Page 1 Summary: Total = {p1_grand_total}")
    
    # PAGE 2 SUMMARY
    total_items = Item.objects.filter(report=self.report).aggregate(
        total=djmodels.Sum('amount'))['total'] or Decimal(0)
    
    ItemsSummary.objects.update_or_create(
        report=self.report,
        defaults={'total_amount': total_items}
    )
    if self.debug:
        print(f"  Page 2 Summary: Total Items = {total_items}")
    
    # PAGE 3 SUMMARY
    total_added = ItemAdded.objects.filter(report=self.report).aggregate(
        total=djmodels.Sum('amount'))['total'] or Decimal(0)
    
    ItemAddedSummary.objects.update_or_create(
        report=self.report,
        defaults={'total_amount': total_added}
    )
    if self.debug:
        print(f"  Page 3 Summary: Total Added = {total_added}")
    
    # PAGE 4 SUMMARY
    total_removed = ItemRemoved.objects.filter(report=self.report).aggregate(
        total=djmodels.Sum('amount'))['total'] or Decimal(0)
    
    ItemRemovedSummary.objects.update_or_create(
        report=self.report,
        defaults={'total_amount': total_removed}
    )
    if self.debug:
        print(f"  Page 4 Summary: Total Removed = {total_removed}")
    
    # PAGE 5 SUMMARY - Land
    total_land = Land.objects.filter(report=self.report).aggregate(
        total=djmodels.Sum('value'))['total'] or Decimal(0)
    
    LandSummary.objects.update_or_create(
        report=self.report,
        defaults={'total_value': total_land}
    )
    if self.debug:
        print(f"  Page 5 Summary - Land: Total Value = {total_land}")
    
    # PAGE 5 SUMMARY - Plant
    total_plant = Plant.objects.filter(report=self.report).aggregate(
        total=djmodels.Sum('total_value_current'))['total'] or Decimal(0)
    
    PlantSummary.objects.update_or_create(
        report=self.report,
        defaults={'total_value': total_plant}
    )
    if self.debug:
        print(f"  Page 5 Summary - Plant: Total Value = {total_plant}")
    
    # PAGE 5 SUMMARY - Vehicle
    total_vehicle = Vehicle.objects.filter(report=self.report).aggregate(
        total=djmodels.Sum('cost'))['total'] or Decimal(0)
    
    VehicleSummary.objects.update_or_create(
        report=self.report,
        defaults={'total_value': total_vehicle}
    )
    if self.debug:
        print(f"  Page 5 Summary - Vehicle: Total Value = {total_vehicle}")
    
    # AGGREGATE SUMMARY (All pages)
    p5_total = total_land + total_plant + total_vehicle
    total_summary = p1_grand_total + total_items + total_added + total_removed + p5_total
    
    ReportSummary.objects.update_or_create(
        report=self.report,
        defaults={
            'p1_total': p1_grand_total,
            'p2_total': total_items,
            'p3_total': total_added,
            'p4_total': total_removed,
            'p5_total': p5_total,
            'total_summary': total_summary
        }
    )
    if self.debug:
        print(f"  Report Summary: Grand Total = {total_summary}")