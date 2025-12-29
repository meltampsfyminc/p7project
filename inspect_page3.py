
import pandas as pd
import os

file_path = r"c:\Projects\p7project\P7 Annual Page 2 to 3.xls"

try:
    xls = pd.ExcelFile(file_path)
    if 'Page 3' in xls.sheet_names:
        print(f"\n--- Sheet: Page 3 ---")
        df = pd.read_excel(xls, sheet_name='Page 3', header=None, skiprows=5, nrows=5)
        print(df.fillna('').to_string())
except Exception as e:
    print(f"Error: {e}")
