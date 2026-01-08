import pandas as pd
import os
import numpy as np

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

df["price"] = df["price"].replace("", pd.NA)
df["price"] = pd.to_numeric(df["price"], errors="coerce")

missing_price_index = df[df["price"].isna()].index

df["unit_price"] = df["price"] / df["qty"]

unit_price_map = (
    df.dropna(subset=["unit_price"])
      .groupby("brand")["unit_price"]
      .first()
)

df["price"] = df.apply(
    lambda row: unit_price_map[row["brand"]] * row["qty"]
    if pd.isna(row["price"]) and row["brand"] in unit_price_map
    else row["price"],
    axis=1
)

changed_rows = df.loc[missing_price_index]

changed_rows = changed_rows.drop(columns=["unit_price"], errors="ignore")

print("\n🟢 Rows where PRICE was calculated/filled:")
print(changed_rows[["brand", "qty", "price"]])


#if price is null so other data accoding set 