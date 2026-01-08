import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression

# =================================================
# 🔍 AUTO FIND FILE
# =================================================
def find_excel(target_name, search_root="D:\\"):
    for root, dirs, files in os.walk(search_root):
        for file in files:
            if target_name.lower() in file.lower() and file.endswith(".xlsx"):
                return os.path.join(root, file)
    return None

SALES_FILE = find_excel("Instant_Delivery_Sales_MIXED_260_UPDATED")

if SALES_FILE is None:
    raise FileNotFoundError("Sales file not found")

print("✔ Sales File:", SALES_FILE)

# =================================================
# 📥 LOAD DATA
# =================================================
df = pd.read_excel(SALES_FILE)

df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
df["month"] = df["sale_date"].dt.month
df["product_name"] = df["product_name"].astype(str)

# =================================================
# 📊 MONTHLY DEMAND
# =================================================
monthly_demand = (
    df.groupby(["product_name", "month"])["quantity"]
    .sum()
    .reset_index()
)

# =================================================
# 🧠 LIFECYCLE CLASSIFICATION
# =================================================
results = []

for product, grp in monthly_demand.groupby("product_name"):
    grp = grp.sort_values("month")

    if len(grp) < 3:
        stage = "New"
        trend = "Growing"
        action = "Increase inventory by 25%"
    else:
        X = np.arange(len(grp)).reshape(-1, 1)
        y = grp["quantity"].values

        model = LinearRegression()
        model.fit(X, y)
        slope = model.coef_[0]

        if slope > 1:
            trend = "Growing"
            stage = "New"
            action = "Increase inventory by 25%"
        elif slope > -1:
            trend = "Stable"
            stage = "Mature"
            action = "Maintain current stock levels"
        else:
            trend = "Declining"
            stage = "Declining"
            action = "Reduce procurement by 40%"

    results.append({
        "product_name": product,
        "demand_trend": trend,
        "lifecycle_stage": stage,
        "action_recommendation": action
    })

lifecycle_df = pd.DataFrame(results)

# =================================================
# 📌 KPI CARDS
# =================================================
total_products = lifecycle_df.shape[0]
new_products = (lifecycle_df["lifecycle_stage"] == "New").sum()
mature_products = (lifecycle_df["lifecycle_stage"] == "Mature").sum()
declining_products = (lifecycle_df["lifecycle_stage"] == "Declining").sum()

print("\n===============================")
print("📊 KPI SUMMARY")
print("===============================")
print("Total Products:", total_products)
print("New Products:", new_products)
print("Mature Products:", mature_products)
print("Declining Products:", declining_products)

# =================================================
# 📈 PRODUCT DEMAND TRENDS (FOR LINE CHART)
# =================================================
trend_chart_data = (
    monthly_demand.pivot(
        index="month",
        columns="product_name",
        values="quantity"
    )
    .fillna(0)
)

print("\n===============================")
print("📈 PRODUCT DEMAND TRENDS (12 MONTHS)")
print("===============================")
print(trend_chart_data.head())

# =================================================
# 📋 PRODUCT LIFECYCLE TABLE
# =================================================
print("\n===============================")
print("📋 PRODUCT LIFECYCLE CLASSIFICATION")
print("===============================")
print(lifecycle_df)

# =================================================
# 🚨 CRITICAL INSIGHT BANNER
# =================================================
declining = lifecycle_df[lifecycle_df["lifecycle_stage"] == "Declining"]

if not declining.empty:
    critical_product = declining.iloc[0]["product_name"]
    insight = (
        f"Critical Insight: {critical_product} shows declining demand trend — "
        f"reduce procurement by 40% to avoid inventory buildup."
    )
else:
    insight = "All products show stable or growing demand."

print("\n===============================")
print("🚨 CRITICAL INSIGHT")
print("===============================")
print(insight)

# =================================================
# 📦 PROCUREMENT STRATEGY
# =================================================
print("\n===============================")
print("📦 PROCUREMENT STRATEGY RECOMMENDATIONS")
print("===============================")

print("\nIncrease Inventory:")
print(lifecycle_df[lifecycle_df["action_recommendation"].str.contains("Increase")][
    ["product_name"]
])

print("\nMaintain Stock Levels:")
print(lifecycle_df[lifecycle_df["action_recommendation"].str.contains("Maintain")][
    ["product_name"]
])

print("\nReduce Procurement:")
print(lifecycle_df[lifecycle_df["action_recommendation"].str.contains("Reduce")][
    ["product_name"]
])


#| Code               | Business Meaning                        |
#| ------------------ | --------------------------------------- |
#| `X`                | Time (Month 1, Month 2, Month 3…)       |
#| `y`                | Sales quantity in each month            |
#| `LinearRegression` | Fits a straight line through sales data |
#| `slope`            | Direction + speed of demand change      |

# Product Lifecycle Analysis

