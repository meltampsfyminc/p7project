#!/usr/bin/env python
import xlrd

file_path = r'c:\Projects\p7project\property_management\uploads\P-7-H - Unit 22.xls'

try:
    wb = xlrd.open_workbook(file_path)
    sheet = wb.sheet_by_index(0)
    
    print("FLOOR AND UNIT NUMBER area:")
    for col in range(15, 25):
        val = sheet.cell_value(5, col)
        print(f"(5,{col:2d}): '{val}'")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
