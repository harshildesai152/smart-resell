import pandas as pd
import numpy as np
import os

from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor

def find_excel(target_name):
    for root, dirs, files in os.walk("D:\\"):
        for file in files:
            if target_name.lower() in file.lower() and file.lower().endswith(".xlsx"):
                return os.path.join(root, file)
    return None


SALES_FILE = find_excel("Instant_Delivery_Sales_PRICE_AWARE")
if SALES_FILE is None:
    raise FileNotFoundError("Instant Delivery Sales file not found")

print("✔ Sales File Found:", SALES_FILE)


# ===============================
# 📥 Load Data
# ===============================
sales_df = pd.read_excel(SALES_FILE)

print("\n📊 Columns Found:")
print(list(sales_df.columns))


# ===============================
# 🧠 Safe Encoding
# ===============================
encoders = {}
fallback_values = {}

for col in ["category", "weather", "city", "platform"]:
    le = LabelEncoder()
    sales_df[col] = sales_df[col].astype(str)
    sales_df[col] = le.fit_transform(sales_df[col])
    encoders[col] = le
    fallback_values[col] = le.classes_[0]


def safe_encode(col, value):
    if value in encoders[col].classes_:
        return encoders[col].transform([value])[0]
    return encoders[col].transform([fallback_values[col]])[0]


# ===============================
# 🎯 Target Variable
# ===============================
sales_df["sold"] = (sales_df["quantity"] > 0).astype(int)


# ===============================
# 📈 Logistic Regression (Demand)
# ===============================
X = sales_df[["category", "sale_price", "weather", "city"]]
y = sales_df["sold"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

log_model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)
log_model.fit(X_train, y_train)


# ===============================
# 📍 KNN (Recommended App)
# ===============================
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X, sales_df["platform"])


# ===============================
# 💰 Gradient Boosting (Price Model)
# ===============================
price_features = sales_df[["category", "weather", "city"]]
price_target = sales_df["sale_price"]

price_model = GradientBoostingRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=3,
    random_state=42
)
price_model.fit(price_features, price_target)


# ===============================
# 🧾 MANUAL INPUT (CHANGE FOR TESTING)
# ===============================
manual_input = {
    "product_name": "I phone",
    "category": "Smart  Phone",
    "original_price": 25000,
    "weather": "Winter",
    "city": "Ahmedabad"
}

print("\n📌 Manual Input:")
for k, v in manual_input.items():
    print(f"{k}: {v}")


manual_df = pd.DataFrame([{
    "category": safe_encode("category", manual_input["category"]),
    "sale_price": manual_input["original_price"],
    "weather": safe_encode("weather", manual_input["weather"]),
    "city": safe_encode("city", manual_input["city"]),
}])


# ===============================
# 📊 Base SELL Probability (Demand)
# ===============================
base_prob = log_model.predict_proba(manual_df)[0][1]


# ===============================
# 📱 Recommended App
# ===============================
app_code = knn.predict(manual_df)[0]
recommended_app = encoders["platform"].inverse_transform([app_code])[0]


# ===============================
# 💰 Price Acceptance (GBM)
# ===============================
predicted_market_price = price_model.predict(
    manual_df[["category", "weather", "city"]]
)[0]

price_ok = manual_input["original_price"] <= predicted_market_price

if not price_ok:
    base_prob *= 0.5   # price too high → reduce probability


seasonal_boost = {

    # 🌞 SUMMER
    "Air Conditioner": ["Summer"],
    "Cooler": ["Summer"],
    "Fan": ["Summer"],
    "Water Cooler": ["Summer"],
    "Refrigerator": ["Summer"],
    "Ice Cream": ["Summer"],
    "Cold Drink": ["Summer"],
    "Juice": ["Summer"],
    "Soft Drink": ["Summer"],
    "Sunscreen": ["Summer"],
    "Cotton Clothes": ["Summer"],
    "T-Shirt": ["Summer"],
    "Shorts": ["Summer"],
    "Cap": ["Summer"],

    # ❄️ WINTER
    "Heater": ["Winter"],
    "Room Heater": ["Winter"],
    "Geyser": ["Winter"],
    "Blanket": ["Winter"],
    "Quilt": ["Winter"],
    "Jacket": ["Winter"],
    "Sweater": ["Winter"],
    "Hoodie": ["Winter"],
    "Thermal Wear": ["Winter"],
    "Gloves": ["Winter"],

    # 🌧️ RAINY
    "Raincoat": ["Rainy"],
    "Umbrella": ["Rainy"],
    "Rain Shoes": ["Rainy"],
    "Waterproof Jacket": ["Rainy"],
    "Mosquito Repellent": ["Rainy"],
    "Insect Killer": ["Rainy"],

    # 🍲 MULTI-SEASON
    "Tea": ["Winter", "Rainy"],
    "Coffee": ["Winter", "Rainy"],
    "Soup": ["Winter", "Rainy"],
    "Instant Noodles": ["Winter", "Rainy"],
    "Snacks": ["Rainy", "Winter"],

    # ⚖️ ALL-SEASON / NEUTRAL
    "Electronics": ["Summer", "Winter", "Rainy"],
    "Smart Watch": ["Summer", "Winter", "Rainy"],
    "Mobile Phone": ["Summer", "Winter", "Rainy"],
    "Headphones": ["Summer", "Winter", "Rainy"]
}


weather_impact = "Neutral ⚖️"

if manual_input["category"] in seasonal_boost:
    if manual_input["weather"] in seasonal_boost[manual_input["category"]]:
        base_prob *= 1.15
        weather_impact = "Significant ✅"
    else:
        base_prob *= 0.7
        weather_impact = "Not Significant ❌"


# ===============================
# 🎯 Final Probability Clamp
# ===============================
sell_probability = round(
    min(max(base_prob, 0.05), 0.95) * 100, 2
)


# ===============================
# 💰 Estimated Profit
# ===============================
logistics_cost = 60
est_profit = round(predicted_market_price - manual_input["original_price"] - logistics_cost, 2)


print("\n===============================")
print("📈 MANUAL SELL CHECK RESULT")
print("===============================")
print("Product Name      :", manual_input["product_name"])
print("SELL PROBABILITY  :", f"{sell_probability}%")
print("EST. PROFIT (₹)   :", est_profit)
print("Recommended APP   :", recommended_app)
print("Weather Impact    :", weather_impact)
print("Predicted Market Price :", round(predicted_market_price, 2))
print("Price Acceptable  :", "YES ✅" if price_ok else "NO ❌")


#KNN-which APP performed best
#Logistic Regression : SELL PROBABILITY
#for price used this : Gradient Boosting (XGBoost)

#Manual Viability Check