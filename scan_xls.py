#!/usr/bin/env python
import xlrd

file_path = r'c:\Projects\p7project\property_management\uploads\P-7-H - Unit 22.xls'

try:
    wb = xlrd.open_workbook(file_path)
    sheet = wb.sheet_by_index(0)
    
    print("="*80)
    print("SCANNING ROW 4 (Header row for unit info)")
    print("="*80)
    for col in range(0, min(60, sheet.ncols)):
        val = sheet.cell_value(4, col)
        if val:
            print(f"(4,{col:2d}): '{val}'")
    
    print("\n" + "="*80)
    print("SCANNING ROW 5 (Data row for unit info)")
    print("="*80)
    for col in range(0, min(60, sheet.ncols)):
        val = sheet.cell_value(5, col)
        if val:
            print(f"(5,{col:2d}): '{val}'")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
