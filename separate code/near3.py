import pandas as pd
import os
import numpy as np
from sklearn.preprocessing import LabelEncoder

TARGET_FILE = "Instant_Delivery_Sales_350"
file_path = None

for root, dirs, files in os.walk("D:\\"):
    for file in files:
        if TARGET_FILE.lower() in file.lower() and file.lower().endswith(".xlsx"):
            file_path = os.path.join(root, file)
            break
    if file_path:
        break

if file_path is None:
    raise FileNotFoundError("❌ Excel file not found in D:\\")

print(f"📂 File found at: {file_path}")

df = pd.read_excel(file_path)

df.columns = df.columns.str.strip().str.lower()

brand_col = "brand"
qty_col = "qty"
weather_col = "weather condition"

df[weather_col] = df[weather_col].replace("", np.nan)

brand_weather_qty = (
    df.dropna(subset=[weather_col])
      .groupby([brand_col, weather_col], as_index=False)[qty_col]
      .sum()
)

top_weather_per_brand = (
    brand_weather_qty
      .sort_values(by=[brand_col, qty_col], ascending=[True, False])
      .drop_duplicates(subset=[brand_col])
      .rename(columns={weather_col: "top_weather"})
      [[brand_col, "top_weather"]]
)

df = df.merge(top_weather_per_brand, on=brand_col, how="left")

df[weather_col] = df[weather_col].fillna(df["top_weather"])

df[weather_col] = df[weather_col].fillna("Unknown")

df.drop(columns=["top_weather"], inplace=True)

le = LabelEncoder()
df["weather_encoded"] = le.fit_transform(df[weather_col])

print("\n🔢 WEATHER Encoding Mapping:")
for w, i in zip(le.classes_, range(len(le.classes_))):
    print(f"{w} → {i}")

print("\n📊 Final Sample Data:")
print(df[[brand_col, qty_col, weather_col, "weather_encoded"]].head(15))

print("\n✅ WEATHER filled using MERGE + brand most-selling QTY logic successfully")


#LabelEncoder with if  weather is missing so filed data