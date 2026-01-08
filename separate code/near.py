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

df.columns = df.columns.str.strip().str.lower()

required_cols = ["return_lat", "return_lon", "return product platform"]
for col in required_cols:
    if col not in df.columns:
        raise KeyError(f"Missing column: {col}")


df[required_cols] = (
    df[required_cols]
    .replace(r'^\s*$', pd.NA, regex=True)
)


df["return_lat"] = pd.to_numeric(df["return_lat"], errors="coerce")
df["return_lon"] = pd.to_numeric(df["return_lon"], errors="coerce")

#  Identify rows to remove
removed_rows = df[
    df["return_lat"].isna()
    | df["return_lon"].isna()
    | df["return product platform"].isna()
]

print("\n❌ REMOVED ROWS (lat / lon / platform missing):")
if removed_rows.empty:
    print("No rows removed.")
else:
    print(removed_rows)

print("\n❌ TOTAL REMOVED ROWS:", len(removed_rows))

#  Remove those rows
df = df.drop(removed_rows.index).reset_index(drop=True)

print("\n✅ CLEANED DATA RECORD COUNT:", len(df))
