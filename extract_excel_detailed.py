#!/usr/bin/env python
"""
Extract detailed data from Excel file
"""
import xlrd

print("=" * 120)
print("DETAILED EXCEL DATA EXTRACTION")
print("=" * 120)

wb = xlrd.open_workbook('P-7-H - Unit 22.xls')
sheet = wb.sheet_by_index(0)

print(f"\nSheet: '{sheet.name}' | Total rows: {sheet.nrows} | Total columns: {sheet.ncols}\n")

# Print all rows with values
print("ALL ROWS WITH DATA:\n")
for row_idx in range(sheet.nrows):
    row_data = []
    for col_idx in range(sheet.ncols):
        val = sheet.cell_value(row_idx, col_idx)
        if val:  # Only include non-empty cells
            row_data.append((col_idx, val))
    
    if row_data:  # Only print rows with data
        print(f"Row {row_idx}:")
        for col_idx, val in row_data:
            print(f"  Col {col_idx}: {val}")
        print()
