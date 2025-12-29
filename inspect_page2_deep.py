
import pandas as pd

file_path = r"c:\Projects\p7project\P7 Annual Page 2 to 3.xls"
xls = pd.ExcelFile(file_path)

print("\n--- Page 2 Inspection ---")
df = pd.read_excel(xls, sheet_name='Page 2', header=None)
for idx, row in df.iterrows():
    if idx < 20:
        c4 = str(row[4]).strip() if len(row) > 4 else "N/A"
        print(f"Row {idx}: Col4='{c4}' | Full: {row.tolist()[:5]}...")
