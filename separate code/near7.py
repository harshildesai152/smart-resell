import pandas as pd
import os
from math import radians, cos, sin, asin, sqrt

def find_excel(target_name, search_root="D:\\"):
    for root, _, files in os.walk(search_root):
        for file in files:
            if target_name.lower() in file.lower() and file.endswith(".xlsx"):
                return os.path.join(root, file)
    return None

RETURNS_FILE = find_excel("Amazon_Flipkart_Returns_MIXED_220")
SALES_FILE   = find_excel("Instant_Delivery_Sales_MIXED_260")

if not RETURNS_FILE or not SALES_FILE:
    raise FileNotFoundError("Required Excel files not found")

print("✔ Returns File:", RETURNS_FILE)
print("✔ Sales File  :", SALES_FILE)

returns_df = pd.read_excel(RETURNS_FILE)
sales_df   = pd.read_excel(SALES_FILE)

returns_df["weather"] = returns_df["weather"].astype(str).str.title()
sales_df["weather"]   = sales_df["weather"].astype(str).str.title()

returns_df["category"] = returns_df["category"].astype(str).str.title()
sales_df["category"]   = sales_df["category"].astype(str).str.title()

sales_df["qty"] = sales_df.get("sales_count", sales_df.get("quantity", 1))

# =================================================
# 📏 HAVERSINE DISTANCE (KNN METRIC)
# =================================================
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 6371 * 2 * asin(sqrt(a))

# =================================================
# 1️⃣ RECENT RETURNS (UI LEFT PANEL)
# =================================================
recent_returns = returns_df.sort_values("return_date", ascending=False).head(8)[[
    "product_name", "category", "city", "lat", "lon", "weather"
]]

print("\n===============================")
print("🧾 RECENT RETURNS")
print("===============================")
print(recent_returns[["product_name", "category", "city"]])

# =================================================
# 2️⃣ DEMAND MATCHING ANALYSIS (KNN)
# =================================================
K = 5   # number of nearest neighbors
ui_results = []

for _, r in recent_returns.iterrows():

    # Step 1: Filter similar category
    candidates = sales_df[sales_df["category"] == r["category"]].copy()
    if candidates.empty:
        continue

    # Step 2: Compute distance (KNN core)
    candidates["distance_km"] = candidates.apply(
        lambda s: haversine(
            r["lat"], r["lon"],
            s["lat"], s["lon"]
        ),
        axis=1
    )

    # Step 3: Get K nearest neighbors
    knn_neighbors = candidates.sort_values("distance_km").head(K)

    # Step 4: Metrics for Demand Matching Analysis
    local_similar_sales = len(knn_neighbors)
    avg_distance = round(knn_neighbors["distance_km"].mean(), 2)

    # Step 5: Resale viability logic (business rules)
    if local_similar_sales >= 5 and avg_distance <= 5:
        resale_viability = "High"
    elif local_similar_sales >= 3:
        resale_viability = "Medium"
    else:
        resale_viability = "Low"

    ui_results.append({
        "product_name": r["product_name"],
        "category": r["category"],
        "city": r["city"],
        "local_similar_sales": local_similar_sales,
        "avg_distance_km": avg_distance,
        "resale_viability": resale_viability,
        "evidence": knn_neighbors[[
            "sale_date", "platform", "distance_km", "weather", "qty"
        ]]
    })

# =================================================
# 🖥️ OUTPUT FOR UI (SECTIONS 2 & 3)
# =================================================
for item in ui_results:

    print("\n==============================================")
    print(f"📊 DEMAND MATCHING – {item['product_name']} ({item['category']})")
    print("==============================================")
    print("Local Similar Sales :", item["local_similar_sales"])
    print("Avg Distance (km)   :", item["avg_distance_km"])
    print("Resale Viability   :", item["resale_viability"])

    print("\n🔎 Nearest Historical Transactions (Evidence)")
    print(
        item["evidence"]
        .rename(columns={
            "sale_date": "DATE",
            "platform": "APP CHANNEL",
            "distance_km": "DISTANCE (km)",
            "weather": "WEATHER",
            "qty": "QTY"
        })
        .reset_index(drop=True)
    )

print("\n✅ Demand Matching Analysis Completed")







#knn_neighbors  :Metrics for Demand Matching Analysis
#Demand Matching