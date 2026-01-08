import pandas as pd
import numpy as np
import os

def find_excel(target_name, search_root="D:\\"):
    for root, dirs, files in os.walk(search_root):
        for file in files:
            if target_name.lower() in file.lower() and file.lower().endswith(".xlsx"):
                return os.path.join(root, file)
    return None

RETURNS_FILE = find_excel("Amazon_Flipkart_Returns_MIXED_220_UPDATED")
SALES_FILE   = find_excel("Instant_Delivery_Sales_MIXED_260_UPDATED")

if RETURNS_FILE is None or SALES_FILE is None:
    raise FileNotFoundError("Updated Excel files not found")

print("✔ Returns File:", RETURNS_FILE)
print("✔ Sales File  :", SALES_FILE)

returns_df = pd.read_excel(RETURNS_FILE)
sales_df   = pd.read_excel(SALES_FILE)

# Normalize
returns_df["return_month"] = returns_df["return_month"].astype("Int64")
sales_df["sale_date"] = pd.to_datetime(sales_df["sale_date"], errors="coerce")
sales_df["month"] = sales_df["sale_date"].dt.month

# =================================================
# 📊 TOP METRICS (HEADER CARDS)
# =================================================

# TOTAL RETURNS
total_returns = len(returns_df)

# TOTAL REVENUE BY CHANNEL
sales_df["revenue"] = sales_df["order_value"] * (1 - sales_df["commission_rate"])
revenue_by_channel = sales_df.groupby("platform")["revenue"].sum()

top_channel = revenue_by_channel.idxmax()

# AVG COMMISSION
avg_commission = (sales_df["commission_rate"].mean() * 100).round(2)

# RETURN RATE (from dataset)
return_rate = (sales_df["return_rate"].mean() * 100).round(2)

print("\n===============================")
print("📊 HEADER METRICS")
print("===============================")
print("TOTAL RETURNS :", total_returns)
print("TOP CHANNEL   :", top_channel)
print("AVG COMMISSION:", f"{avg_commission}%")
print("RETURN RATE   :", f"{return_rate}%")

# =================================================
# 📈 REVENUE BY CHANNEL (MONTHLY TREND)
# =================================================
revenue_trend = (
    sales_df.groupby(["month", "platform"])["revenue"]
    .sum()
    .reset_index()
    .sort_values(["month", "platform"])
)

print("\n===============================")
print("📈 REVENUE BY CHANNEL (TREND)")
print("===============================")
print(revenue_trend.head(10))

# =================================================
# 🥧 MARKET SHARE
# =================================================
market_share = (
    revenue_by_channel / revenue_by_channel.sum() * 100
).round(2).reset_index(name="market_share")

print("\n===============================")
print("🥧 MARKET SHARE (%)")
print("===============================")
print(market_share)

# =================================================
# 📋 PLATFORM PERFORMANCE METRICS (TABLE)
# =================================================
platform_metrics = (
    sales_df.groupby("platform")
    .agg(
        delivery_speed=("delivery_time_min", "mean"),
        conversion=("conversion_rate", "mean"),
        rtn_rate=("return_rate", "mean"),
        rating=("rating", "mean")
    )
    .reset_index()
)

platform_metrics["delivery_speed"] = platform_metrics["delivery_speed"].round(0)
platform_metrics["conversion"] = (platform_metrics["conversion"] * 100).round(2)
platform_metrics["rtn_rate"] = (platform_metrics["rtn_rate"] * 100).round(2)
platform_metrics["rating"] = platform_metrics["rating"].round(1)

print("\n===============================")
print("📋 PLATFORM PERFORMANCE METRICS")
print("===============================")
print(platform_metrics)

output = {
    "header_metrics": {
        "total_returns": total_returns,
        "top_channel": top_channel,
        "avg_commission_percent": avg_commission,
        "return_rate_percent": return_rate
    },
    "revenue_trend": revenue_trend,
    "market_share": market_share,
    "platform_metrics": platform_metrics
}

print("\n✅ CHANNEL PERFORMANCE ANALYTICS READY FOR UI")



#Channel Analysis