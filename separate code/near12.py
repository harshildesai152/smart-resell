import pandas as pd
import numpy as np
import os

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor

def find_excel(target_name, search_root="D:\\"):
    for root, dirs, files in os.walk(search_root):
        for file in files:
            if target_name.lower() in file.lower() and file.lower().endswith(".xlsx"):
                return os.path.join(root, file)
    return None

SALES_FILE = find_excel("Instant_Delivery_Sales_MIXED_260_UPDATED")

if SALES_FILE is None:
    raise FileNotFoundError("❌ Sales file not found")

print("✔ Sales File:", SALES_FILE)

sales_df = pd.read_excel(SALES_FILE)

PRICE_COL_CANDIDATES = ["price", "sale_price", "selling_price", "unit_price"]

price_col = None
for col in PRICE_COL_CANDIDATES:
    if col in sales_df.columns:
        price_col = col
        break

if price_col is None:
    raise ValueError(
        "❌ No price column found. Expected one of: "
        f"{PRICE_COL_CANDIDATES}"
    )

print(f"✔ Using price column: {price_col}")

# =================================================
# 🧹 CLEAN DATA
# =================================================
sales_df = sales_df.dropna(subset=[price_col, "quantity"])
sales_df = sales_df[sales_df["quantity"] > 0]
sales_df = sales_df[sales_df[price_col] > 0]

# =================================================
# 📊 BASE METRICS
# =================================================
BASE_PRICE = sales_df[price_col].mean()
BASE_DEMAND = sales_df["quantity"].mean()

# =================================================
# 🧠 TRAIN ML MODELS
# =================================================
X = sales_df[[price_col]]
y = sales_df["quantity"]

lin_model = LinearRegression()
lin_model.fit(X, y)

gbr_model = GradientBoostingRegressor(random_state=42)
gbr_model.fit(X, y)

# =================================================
# 🎚️ DISCOUNT SIMULATION
# =================================================
DISCOUNT_LEVELS = list(range(0, 51, 5))
sim_rows = []

for d in DISCOUNT_LEVELS:
    discounted_price = BASE_PRICE * (1 - d / 100)

    X_input = pd.DataFrame({price_col: [discounted_price]})

    predicted_demand = max(0, gbr_model.predict(X_input)[0])
    revenue = discounted_price * predicted_demand

    margin = 0.25  # 25% assumed margin
    profit = revenue * margin

    demand_impact = (predicted_demand / BASE_DEMAND) * 100
    revenue_impact = (revenue / (BASE_PRICE * BASE_DEMAND)) * 100
    profit_impact = (profit / ((BASE_PRICE * BASE_DEMAND) * margin)) * 100

    sim_rows.append({
        "discount_%": d,
        "demand_impact_%": round(demand_impact, 2),
        "revenue_impact_%": round(revenue_impact, 2),
        "profit_impact_%": round(profit_impact, 2)
    })

sim_df = pd.DataFrame(sim_rows)

# =================================================
# 🎯 CURRENT DISCOUNT ANALYSIS (15%)
# =================================================
CURRENT_DISCOUNT = 15
current_row = sim_df[sim_df["discount_%"] == CURRENT_DISCOUNT].iloc[0]

discount_summary = {
    "discount_%": CURRENT_DISCOUNT,
    "demand_impact_%": current_row["demand_impact_%"],
    "revenue_impact_%": current_row["revenue_impact_%"],
    "profit_impact_%": current_row["profit_impact_%"]
}

# =================================================
# 💰 PROFIT & BREAK-EVEN (SAFE)
# =================================================
break_even_candidates = sim_df[sim_df["profit_impact_%"] >= 100]

if break_even_candidates.empty:
    break_even_display = "No Break-even"
else:
    break_even_display = f"{int(break_even_candidates['discount_%'].min())}%"

profit_analysis = {
    "base_demand_units": int(BASE_DEMAND),
    "expected_demand_units": int(BASE_DEMAND * current_row["demand_impact_%"] / 100),
    "profit_change_%": round(current_row["profit_impact_%"] - 100, 2),
    "break_even_discount": break_even_display
}

# =================================================
# 📤 FINAL OUTPUTS (UI READY)
# =================================================
print("\n===============================")
print("🎚️ DISCOUNT SIMULATOR (15%)")
print("===============================")
print(discount_summary)

print("\n===============================")
print("📈 PRICE vs DEMAND GRAPH DATA")
print("===============================")
print(sim_df)

print("\n===============================")
print("💰 PROFIT IMPACT ANALYSIS")
print("===============================")
print(profit_analysis)

# =================================================
# 🧠 KEY INSIGHT
# =================================================
best_profit_row = sim_df.loc[sim_df["profit_impact_%"].idxmax()]

print("\n===============================")
print("💡 KEY INSIGHT")
print("===============================")
print(
    f"Optimal discount ≈ {best_profit_row['discount_%']}% "
    f"with profit impact {best_profit_row['profit_impact_%']}%"
)


#LinearRegression : Baseline elasticity
 #GradientBoostingRegressor : Baseline elasticity

#Price Sensitivity & Discount Simulator
