
import pandas as pd
import os

file_path = r"c:\Projects\p7project\P7 Annual Page 2 to 3.xls"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
else:
    try:
        # Try reading with pandas (requires xlrd for .xls)
        xls = pd.ExcelFile(file_path)
        print(f"Sheet names: {xls.sheet_names}")
        
        for sheet in xls.sheet_names:
            print(f"\n--- Sheet: {sheet} ---")
            df = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=10)
            print(df.to_string())
    except Exception as e:
        print(f"Error reading excel: {e}")
