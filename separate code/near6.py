import pandas as pd
import numpy as np
import os
from math import radians, cos, sin, asin, sqrt
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# =================================================
# 🔍 AUTO FIND EXCEL FILES
# =================================================
def find_excel(target_name, search_root="D:\\"):
    for root, dirs, files in os.walk(search_root):
        for file in files:
            if target_name.lower() in file.lower() and file.lower().endswith(".xlsx"):
                return os.path.join(root, file)
    return None

RETURNS_FILE = find_excel("Amazon_Flipkart_Returns_MIXED_220")
SALES_FILE   = find_excel("Instant_Delivery_Sales_MIXED_260")

if RETURNS_FILE is None or SALES_FILE is None:
    raise FileNotFoundError("Required Excel files not found")

print("✔ Returns File:", RETURNS_FILE)
print("✔ Sales File  :", SALES_FILE)

# =================================================
# 📥 LOAD DATA
# =================================================
returns_df = pd.read_excel(RETURNS_FILE)
sales_df   = pd.read_excel(SALES_FILE)

returns_df["weather"] = returns_df["weather"].astype(str).str.title()
sales_df["weather"]   = sales_df["weather"].astype(str).str.title()

returns_df["category"] = returns_df["category"].astype(str)
sales_df["category"]   = sales_df["category"].astype(str)

sales_df["sales_count"] = sales_df.get("sales_count", sales_df.get("quantity", 0))

# =================================================
# 📏 DISTANCE FUNCTION
# =================================================
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return 6371 * 2 * asin(sqrt(a))

# =================================================
# 🧠 ENCODING + ML MODEL
# =================================================
cat_enc = LabelEncoder()
weather_enc = LabelEncoder()

sales_df["category_code"] = cat_enc.fit_transform(sales_df["category"])
sales_df["weather_code"]  = weather_enc.fit_transform(sales_df["weather"])
sales_df["sold"] = (sales_df["sales_count"] > 0).astype(int)

X = sales_df[["category_code", "weather_code", "sales_count"]]
y = sales_df["sold"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

log_model = LogisticRegression(max_iter=1000)
log_model.fit(X_train, y_train)

# =================================================
# 🔮 FINAL ML PREDICTION OUTPUT
# =================================================
ml_results = []

for _, r in returns_df.iterrows():

    candidates = sales_df[
        (sales_df["category"] == r["category"]) &
        (sales_df["weather"] == r["weather"])
    ]

    if candidates.empty:
        continue

    candidates = candidates.copy()
    candidates["distance_km"] = candidates.apply(
        lambda s: haversine(r["lat"], r["lon"], s["lat"], s["lon"]),
        axis=1
    )

    nearest = candidates.sort_values("distance_km").iloc[0]

    X_input = pd.DataFrame([{
        "category_code": cat_enc.transform([r["category"]])[0],
        "weather_code": weather_enc.transform([r["weather"]])[0],
        "sales_count": nearest["sales_count"]
    }])

    sell_prob = log_model.predict_proba(X_input)[0][1] * 100

    ml_results.append({
        "weather": r["weather"],
        "product_name": r["product_name"],
        "category": r["category"],
        "city": r.get("return_city", r["city"]),
        "return_price": r.get("price", r.get("return_price")),
        "sell_probability": round(sell_prob, 2),
        "recommended_app": nearest.get("app_name", nearest["platform"]),
        "recommended_city": nearest["city"],
        "ml_used": True
    })

final_ml_df = pd.DataFrame(ml_results)

print("\n===============================")
print("📊 FINAL ML PREDICTION OUTPUT")
print("===============================")
print(final_ml_df.head(10))

# =================================================
# PAGE-1: WEATHER IMPACT ASSESSMENT
# =================================================

# -------- Graph: CATEGORY vs SALES COUNT --------
page1_graph = (
    final_ml_df.groupby("category")["product_name"]
    .count()
    .reset_index(name="sales_count")
)

# -------- Table: category performance per weather --------
WEATHER_LIST = ["Sunny", "Rainy", "Cloudy", "Windy","Winter"]

page1_tables = {}
overall_avg = (
    final_ml_df.groupby("category")["product_name"]
    .count()
    .rename("overall_avg")
    .reset_index()
)

for weather in WEATHER_LIST:
    w_df = final_ml_df[final_ml_df["weather"] == weather]
    if w_df.empty:
        continue

    cat_perf = (
        w_df.groupby("category")["product_name"]
        .count()
        .reset_index(name="sales_count")
    )

    cat_perf = cat_perf.merge(overall_avg, on="category", how="left")

    cat_perf["trend_vs_avg"] = (
        (cat_perf["sales_count"] - cat_perf["overall_avg"])
        / cat_perf["overall_avg"]
    ) * 100

    def stock_rule(v):
        if v >= 10:
            return "High Priority"
        elif v >= 0:
            return "Medium Priority"
        return "Low Priority"

    cat_perf["recommended_stock"] = cat_perf["trend_vs_avg"].apply(stock_rule)
    cat_perf["trend_vs_avg"] = cat_perf["trend_vs_avg"].round(2)

    page1_tables[weather] = cat_perf

# =================================================
# PAGE-2: PRODUCT PERFORMANCE BY WEATHER
# =================================================

page2_graph = (
    final_ml_df.groupby("weather")["product_name"]
    .count()
    .reset_index(name="sales_count")
)

page2_tables = page1_tables

# =================================================
# ✅ NEW ADDITION: PAGE-2 TABLE – WEATHER IMPACT STATISTICS
# =================================================

total_txn = len(final_ml_df)

weather_impact_table = (
    final_ml_df.groupby("weather")
    .agg(
        total_transactions=("product_name", "count"),
        avg_order_value=("return_price", "mean")
    )
    .reset_index()
)

weather_impact_table["market_share"] = (
    weather_impact_table["total_transactions"] / total_txn * 100
).round(2)

weather_impact_table["avg_order_value"] = (
    weather_impact_table["avg_order_value"].round(0)
)

print("\n===============================")
print("📋 PAGE-2 TABLE: WEATHER IMPACT STATISTICS")
print("===============================")
print(weather_impact_table)

# =================================================
# ✅ FINAL OUTPUTS (READY FOR UI)
# =================================================

print("\n📈 PAGE-1 GRAPH (CATEGORY vs SALES COUNT)")
print(page1_graph)

print("\n📈 PAGE-2 GRAPH (WEATHER vs SALES COUNT)")
print(page2_graph)

for weather in page1_tables:
    print(f"\n📋 PAGE-1 TABLE – {weather}")
    print(page1_tables[weather][[
        "category", "sales_count", "trend_vs_avg", "recommended_stock"
    ]])


#Weather Trends
#Weather x Product
