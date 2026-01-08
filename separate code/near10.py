import pandas as pd
import numpy as np
import os
from sklearn.cluster import KMeans

def find_excel(target_name, search_root="D:\\"):
    for root, dirs, files in os.walk(search_root):
        for file in files:
            if target_name.lower() in file.lower() and file.lower().endswith(".xlsx"):
                return os.path.join(root, file)
    return None

RETURNS_FILE = find_excel("Amazon_Flipkart_Returns_MIXED_220_UPDATED")
SALES_FILE   = find_excel("Instant_Delivery_Sales_MIXED_260_UPDATED")

if not RETURNS_FILE or not SALES_FILE:
    raise FileNotFoundError("Required dataset not found")

print("✔ Returns File:", RETURNS_FILE)
print("✔ Sales File  :", SALES_FILE)


returns_df = pd.read_excel(RETURNS_FILE)
sales_df   = pd.read_excel(SALES_FILE)

returns_df["city"] = returns_df["city"].astype(str)
sales_df["city"] = sales_df["city"].astype(str)

city_demand = (
    sales_df.groupby("city")["quantity"]
    .sum()
    .reset_index(name="total_sales")
)

city_returns = (
    returns_df.groupby("city")["order_id"]
    .count()
    .reset_index(name="total_returns")
)

city_metrics = city_demand.merge(
    city_returns, on="city", how="left"
).fillna(0)

city_metrics["return_pct"] = (
    city_metrics["total_returns"] /
    (city_metrics["total_sales"] + city_metrics["total_returns"])
) * 100

coords = (
    sales_df.groupby("city")[["lat", "lon"]]
    .mean()
    .reset_index()
)

city_metrics = city_metrics.merge(coords, on="city", how="left")

# =================================================
# 📍 K-MEANS CLUSTERING (SAFE)
# =================================================
cluster_features = city_metrics[[
    "total_sales", "return_pct"
]].fillna(0)

n_samples = len(cluster_features)
n_clusters = min(4, n_samples)   # ✅ FIX

if n_clusters >= 2:
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    city_metrics["cluster"] = kmeans.fit_predict(cluster_features)
else:
    city_metrics["cluster"] = 0  

# =================================================
# 🟢🔴🟡🟣 ZONE ASSIGNMENT
# =================================================
sales_avg = city_metrics["total_sales"].mean()
return_avg = city_metrics["return_pct"].mean()

def assign_zone(row):
    if row["total_sales"] >= sales_avg and row["return_pct"] <= return_avg:
        return "🟢 High Demand / Low Return"
    if row["total_sales"] >= sales_avg and row["return_pct"] > return_avg:
        return "🔴 High Demand / High Return"
    if row["total_sales"] < sales_avg and row["return_pct"] > return_avg:
        return "🟡 Low Demand / High Return"
    return "🟣 Stable Zone"

city_metrics["zone_type"] = city_metrics.apply(assign_zone, axis=1)

# =================================================
# 📊 KPI CARDS
# =================================================
total_cities = city_metrics["city"].nunique()
high_demand_clusters = city_metrics[
    city_metrics["zone_type"].str.contains("High Demand")
]["city"].nunique()

high_return_zones = city_metrics[
    city_metrics["zone_type"].str.contains("High Return")
]["city"].nunique()

expansion_opportunities = city_metrics[
    city_metrics["zone_type"] == "🟢 High Demand / Low Return"
]["city"].nunique()

print("\n===============================")
print("📊 KPI SUMMARY")
print("===============================")
print("Total Cities:", total_cities)
print("High-Demand Clusters:", high_demand_clusters)
print("High-Return Zones:", high_return_zones)
print("Expansion Opportunities:", expansion_opportunities)

# =================================================
# 🗺️ CITY CLUSTER MAP DATA
# =================================================
city_cluster_map = city_metrics[[
    "city", "lat", "lon", "zone_type"
]]

print("\n===============================")
print("🗺️ CITY CLUSTER MAP DATA")
print("===============================")
print(city_cluster_map)

# =================================================
# 🚨 HIGH-RISK ZONES TABLE
# =================================================
def risk_level(pct):
    if pct >= 25:
        return "High"
    elif pct >= 12:
        return "Medium"
    return "Low"

city_metrics["risk_level"] = city_metrics["return_pct"].apply(risk_level)

high_risk_table = city_metrics[[
    "city",
    "risk_level",
    "return_pct",
    "total_sales"
]].rename(columns={
    "total_sales": "demand"
}).sort_values("return_pct", ascending=False)

print("\n===============================")
print("🚨 HIGH-RISK ZONES")
print("===============================")
print(high_risk_table)



#used KMeans for High Demand zone
#Customer & Location Segmentation