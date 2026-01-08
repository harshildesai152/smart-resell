import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
import os
from collections import defaultdict

def find_excel(target_name):
    for root, dirs, files in os.walk("D:\\"):
        for file in files:
            if target_name.lower() in file.lower() and file.lower().endswith(".xlsx"):
                return os.path.join(root, file)
    return None


RETURN_FILE = find_excel("Amazon_Flipkart_Returns_MIXED_220")
SALES_FILE  = find_excel("Instant_Delivery_Sales_MIXED_260")

if RETURN_FILE is None or SALES_FILE is None:
    raise FileNotFoundError("Required Excel files not found")

MAX_DISTANCE_KM = 15
MIN_TOTAL_QTY   = 5
YES_THRESHOLD   = 70
MAYBE_THRESHOLD = 40

PLATFORM_WEIGHT = {
    "Blinkit": 1.0,
    "Swiggy Instamart": 0.9,
    "Zepto": 0.8
}

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    return 6371 * 2 * asin(sqrt(a))

returns_df = pd.read_excel(RETURN_FILE)
sales_df   = pd.read_excel(SALES_FILE)

if "qty" not in sales_df.columns:
    print("⚠️ 'qty' column not found — assuming qty = 1 per sale")
    sales_df["qty"] = 1

returns_df = returns_df.dropna(subset=["product_name", "lat", "lon"])
sales_df   = sales_df.dropna(subset=["product_name", "lat", "lon", "platform"])

# ✅ REGIONAL SUMMARY STORAGE
regional_summary = defaultdict(lambda: {"returns": 0, "sales": 0})

for _, ret in returns_df.iterrows():

    order_id = ret.get("order_id", "NA")
    product  = ret["product_name"]
    city     = ret.get("city", "Unknown")
    r_lat    = ret["lat"]
    r_lon    = ret["lon"]

    print(f"Order ID       : {order_id}")
    print(f"Product        : {product}")
    print(f"Return City    : {city}")
    print(f"Return Lat/Lon : {r_lat}, {r_lon}")

    matched_sales = sales_df[sales_df["product_name"] == product].copy()

    if matched_sales.empty:
        print("SELL NEAR ME   : NO")
        print("SELL CONFIDENCE: 0 %")
        print("Reason         : No instant-delivery sales history")
        regional_summary[city]["returns"] += 1
        print("-" * 45)
        continue

    matched_sales.loc[:, "distance_km"] = matched_sales.apply(
        lambda row: haversine(r_lat, r_lon, row["lat"], row["lon"]),
        axis=1
    )

    nearby_sales = matched_sales[matched_sales["distance_km"] <= MAX_DISTANCE_KM]

    if nearby_sales.empty:
        print("SELL NEAR ME   : NO")
        print("SELL CONFIDENCE: 0 %")
        print("Reason         : No nearby demand within radius")
        regional_summary[city]["returns"] += 1
        print("-" * 45)
        continue

    total_qty = nearby_sales["qty"].sum()

    if total_qty < MIN_TOTAL_QTY:
        print("SELL NEAR ME   : NO")
        print("SELL CONFIDENCE: 0 %")
        print("Reason         : Insufficient demand volume")
        regional_summary[city]["returns"] += 1
        print("-" * 45)
        continue

    platform_qty = nearby_sales.groupby("platform")["qty"].sum()
    best_app = platform_qty.idxmax()

    platform_strength = PLATFORM_WEIGHT.get(best_app, 0.7)
    avg_distance = nearby_sales["distance_km"].mean()

    distance_score = max(0, (MAX_DISTANCE_KM - avg_distance) / MAX_DISTANCE_KM)
    demand_score   = min(1, total_qty / 30)
    platform_score = platform_strength

    sell_confidence = int((
        0.5 * distance_score +
        0.3 * demand_score +
        0.2 * platform_score
    ) * 100)

    if sell_confidence < MAYBE_THRESHOLD:
        decision = "NO"
        regional_summary[city]["returns"] += 1

    else:
        decision = "YES" if sell_confidence >= YES_THRESHOLD else "MAYBE"
        regional_summary[city]["sales"] += 1
        best_row = nearby_sales.sort_values("distance_km").iloc[0]
        sell_lat = best_row["lat"]
        sell_lon = best_row["lon"]

    print(f"SELL NEAR ME   : {decision}")
    print(f"SELL CONFIDENCE: {sell_confidence} %")

    if decision != "NO":
        print(f"BEST APP       : {best_app}")
        print(f"SELL Lat/Lon   : {sell_lat}, {sell_lon}")

    print("-" * 45)

# =====================================================
# 📊 REGIONAL SALES VS RETURNS SUMMARY
# =====================================================
print("\n📍 Regional Sales vs Returns:\n")

for city, data in regional_summary.items():
    print(
        f"{city:<12} : "
        f"Returns = {data['returns']:<3} | "
        f"Sales = {data['sales']:<3}"
    )

#Geospatial Demand Analysis