
import pandas as pd
import os

file_path = r"c:\Projects\p7project\P7 Annual Page 2 to 3.xls"

try:
    xls = pd.ExcelFile(file_path)
    for sheet in xls.sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        # Read rows 0-15
        df = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=15)
        # Print non-null values for each row to identify structure
        for index, row in df.iterrows():
            values = [str(v).strip() for v in row if pd.notna(v) and str(v).strip()]
            if values:
                print(f"Row {index+1}: {values}")
except Exception as e:
    print(f"Error: {e}")
