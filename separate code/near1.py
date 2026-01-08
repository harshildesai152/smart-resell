import pandas as pd
import os


TARGET_FILE = "Amazon_Flipkart_Returns_320"
file_path = None

for root, dirs, files in os.walk("D:\\"):
    for file in files:
        if TARGET_FILE.lower() in file.lower() and file.lower().endswith(".xlsx"):
            file_path = os.path.join(root, file)
            break
    if file_path:
        break

if file_path is None:
    raise FileNotFoundError("Excel file not found")


df = pd.read_excel(file_path)

df = df.dropna(subset=["return_lat", "return_lon"])


duplicate_rows = df[df.duplicated(subset=["return_lat", "return_lon"], keep="first")]

df = df.drop_duplicates(subset=["return_lat", "return_lon"], keep="first")

df = df.reset_index(drop=True)

print("\n REMOVED DUPLICATE ROWS (based on latitude & longitude):")
if duplicate_rows.empty:
    print("No duplicate rows found.")
else:
    print(duplicate_rows)

print("\n✅ Final record count:", len(df))

# remove any feild null so remove 