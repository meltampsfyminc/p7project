#!/usr/bin/env python
import xlrd

file_path = r'c:\Projects\p7project\property_management\uploads\P-7-H - Unit 22.xls'

try:
    wb = xlrd.open_workbook(file_path)
    sheet = wb.sheet_by_index(0)
    
    print("="*80)
    print(f"XLS File: {file_path}")
    print("="*80)
    
    print("\nEXTRACTED VALUES:")
    occupant_name = sheet.cell_value(4, 12)
    department = sheet.cell_value(4, 33)
    section = sheet.cell_value(4, 42)
    job_title = sheet.cell_value(4, 54)
    
    housing_unit_name = sheet.cell_value(5, 5)
    building_name = sheet.cell_value(5, 14)
    floor = sheet.cell_value(5, 17)
    unit_number = sheet.cell_value(5, 22)
    address = sheet.cell_value(5, 31)
    
    date_str = sheet.cell_value(1, 47)
    
    print(f"Occupant Name (4,12): '{occupant_name}'")
    print(f"Department (4,33): '{department}'")
    print(f"Section (4,42): '{section}'")
    print(f"Job Title (4,54): '{job_title}'")
    print(f"Housing Unit Name (5,5): '{housing_unit_name}'")
    print(f"Building Name (5,14): '{building_name}'")
    print(f"Floor (5,17): '{floor}'")
    print(f"Unit Number (5,22): '{unit_number}'")
    print(f"Address (5,31): '{address}'")
    print(f"Date Reported (1,47): '{date_str}'")
    
    print("\n" + "="*80)
    print("NEARBY CELLS FOR BUILDING NAME (5,14):")
    print("="*80)
    for col in range(10, 20):
        val = sheet.cell_value(5, col)
        print(f"Cell (5,{col}): '{val}'")
    
    print("\n" + "="*80)
    print("NEARBY CELLS FOR ADDRESS (5,31):")
    print("="*80)
    for col in range(25, 35):
        val = sheet.cell_value(5, col)
        print(f"Cell (5,{col}): '{val}'")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
