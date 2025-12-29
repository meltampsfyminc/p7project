
import pandas as pd
import os

file_path = r"c:\Projects\p7project\P7 Annual Page 2 to 3.xls"

try:
    xls = pd.ExcelFile(file_path)
    for sheet in xls.sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        # Read rows 5-8 to catch headers
        df = pd.read_excel(xls, sheet_name=sheet, header=None, skiprows=5, nrows=3)
        print(df.fillna('').to_string())
except Exception as e:
    print(f"Error: {e}")
