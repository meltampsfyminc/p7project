#!/usr/bin/env python
"""
Analyze Excel and PDF files to extract data structure
"""
import xlrd
from PyPDF2 import PdfReader
import os

print("=" * 100)
print("FILE ANALYSIS - EXCEL AND PDF")
print("=" * 100)

# ===== EXCEL FILE =====
print("\n\n" + "=" * 100)
print("1. EXCEL FILE: P-7-H - Unit 22.xls")
print("=" * 100)

try:
    wb = xlrd.open_workbook('P-7-H - Unit 22.xls')
    sheet = wb.sheet_by_index(0)
    
    print(f"\nShape: {sheet.nrows} rows × {sheet.ncols} columns")
    print(f"Sheet name: '{sheet.name}'\n")
    
    # Get headers
    headers = [sheet.cell_value(0, i) for i in range(sheet.ncols)]
    print("COLUMNS:")
    for i, h in enumerate(headers, 1):
        print(f"  {i}. '{h}'")
    
    # Show first 5 data rows
    print(f"\n\nFIRST 5 DATA ROWS:")
    print("-" * 100)
    for row_idx in range(1, min(6, sheet.nrows)):
        print(f"\nRow {row_idx}:")
        for col_idx, header in enumerate(headers):
            val = sheet.cell_value(row_idx, col_idx)
            print(f"  {header:30} : {val}")

except Exception as e:
    print(f"Error reading Excel file: {e}")

# ===== PDF FILE =====
print("\n\n" + "=" * 100)
print("2. PDF FILE: 1-17.pdf")
print("=" * 100)

try:
    pdf_reader = PdfReader('1-17.pdf')
    print(f"\nTotal pages: {len(pdf_reader.pages)}\n")
    
    # Extract text from first 3 pages
    print("CONTENT FROM FIRST 3 PAGES (First 500 chars each):\n")
    for page_num in range(min(3, len(pdf_reader.pages))):
        page = pdf_reader.pages[page_num]
        text = page.extract_text()
        print(f"\n--- PAGE {page_num + 1} ---")
        print(text[:500] if text else "[No text content]")
        print("\n" + "-" * 100)

except Exception as e:
    print(f"Error reading PDF file: {e}")

print("\n" + "=" * 100)
print("ANALYSIS COMPLETE")
print("=" * 100)
