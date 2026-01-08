import pandas as pd
import numpy as np
import os
import requests
from math import radians, cos, sin, asin, sqrt
from sklearn.neighbors import NearestNeighbors
from prophet import Prophet

# Load environment variables from .env file
def load_env_file():
    """Manually load .env file if python-dotenv is not available"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

# Load .env file
load_env_file()

# =================================================
# 🔍 AUTO FIND UPDATED EXCEL FILES
# =================================================
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

returns_df = pd.read_excel(RETURNS_FILE)
sales_df   = pd.read_excel(SALES_FILE)

# =================================================
# 🧹 BASIC CLEANING
# =================================================
sales_df["sale_date"] = pd.to_datetime(sales_df["sale_date"], errors="coerce")
sales_df["month"] = sales_df["sale_date"].dt.month
sales_df["weather"] = sales_df["weather"].astype(str).str.title()

# =================================================
# 🌦 SEASON MAPPING (FIXED)
# =================================================
def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    if month in [3, 4, 5]:
        return "Summer"
    if month in [6, 7, 8]:
        return "Rainy"
    return "Cloudy"

sales_df["season"] = sales_df["month"].apply(get_season)

# =================================================
# 🌍 SAFE LIVE WEATHER API
# =================================================
# Load API key from .env file
OPENWEATHER_API_KEY = os.getenv("API_kay", "API")  # Fallback to "API" if not found
CITY_FOR_WEATHER = "Ahmedabad"

def map_weather(main, wind):
    main = main.lower()
    if "rain" in main:
        return "Rainy"
    if wind >= 8:
        return "Windy"
    if "cloud" in main:
        return "Cloudy"
    return "Sunny"

def get_weather_safe(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            raise Exception("API failed")
        d = r.json()
        return round(d["main"]["temp"]), map_weather(d["weather"][0]["main"], d["wind"]["speed"])
    except:
        fallback = sales_df.sort_values("sale_date").iloc[-1]["weather"]
        return "Derived", fallback

temp, CURRENT_WEATHER = get_weather_safe(CITY_FOR_WEATHER)
CURRENT_TEMP = f"{temp}°C"

# =================================================
# 🔴 LIVE OPPORTUNITY – CURRENT WEATHER
# =================================================
recent_days = 14
latest = sales_df["sale_date"].max()

recent = sales_df[sales_df["sale_date"] >= latest - pd.Timedelta(days=recent_days)]
baseline = sales_df[sales_df["sale_date"] < latest - pd.Timedelta(days=recent_days)]

live = (
    recent[recent["weather"] == CURRENT_WEATHER]
    .groupby(["product_name", "category"])
    .agg(current_velocity=("quantity", "sum"))
    .reset_index()
)

baseline_avg = (
    baseline.groupby(["product_name", "category"])["quantity"]
    .mean()
    .reset_index(name="baseline_velocity")
)

live = live.merge(baseline_avg, on=["product_name", "category"], how="left").dropna()
live["velocity_ratio"] = live["current_velocity"] / live["baseline_velocity"]

def stock_status(v):
    if v >= 1.5: return "High"
    if v >= 1.1: return "Medium"
    return "Low"

live["stock_status"] = live["velocity_ratio"].apply(stock_status)

print("\n🔴 LIVE OPPORTUNITY")
print(live[["product_name", "category", "current_velocity", "stock_status"]].head())

# =================================================
# 🔵 FUTURE SIGNAL – NEXT MONTH (SEASON FIX)
# =================================================
next_month = (latest.month % 12) + 1
NEXT_SEASON = get_season(next_month)

seasonal_sales = (
    sales_df[sales_df["season"] == NEXT_SEASON]
    .groupby(["product_name", "category"])
    .agg(avg_monthly_sales=("quantity", "mean"))
    .reset_index()
)

def demand_label(v):
    if v >= 15: return "Very High"
    if v >= 8: return "High"
    if v >= 4: return "Moderate"
    return "Low"

def action(v):
    if v >= 15: return "Increase Order"
    if v >= 8: return "Stock Up Now"
    if v >= 4: return "Monitor"
    return "Avoid"

seasonal_sales["forecasted_demand"] = seasonal_sales["avg_monthly_sales"].round(1)
seasonal_sales["recommended_action"] = seasonal_sales["forecasted_demand"].apply(action)

print("\n🔵 FUTURE SIGNAL – SEASONAL")
print(seasonal_sales.head())

# =================================================
# 📈 PROPHET FORECAST (NEW)
# =================================================
print("\n📈 PROPHET FORECAST")

prophet_results = []

for (p, c), g in sales_df.groupby(["product_name", "category"]):
    ts = g.groupby("sale_date")["quantity"].sum().reset_index()
    if len(ts) < 10:
        continue
    ts.columns = ["ds", "y"]
    m = Prophet(yearly_seasonality=True)
    m.fit(ts)
    future = m.make_future_dataframe(periods=30)
    forecast = m.predict(future)
    demand = forecast.tail(30)["yhat"].mean()
    prophet_results.append([p, c, round(demand, 1)])

prophet_df = pd.DataFrame(prophet_results, columns=["product", "category", "next_month_demand"])
print(prophet_df.head())

# =================================================
# 🧠 K-NN ALTERNATIVE PRODUCT RECOMMENDATION (NEW)
# =================================================
print("\n🧠 K-NN ALTERNATIVE PRODUCT")

sales_knn = sales_df[["lat", "lon", "quantity"]].dropna()
knn = NearestNeighbors(n_neighbors=5, metric="haversine")
coords = np.radians(sales_knn[["lat", "lon"]])
knn.fit(coords)

def recommend_alternative(lat, lon):
    dist, idx = knn.kneighbors([[radians(lat), radians(lon)]])
    return sales_df.iloc[idx[0]][["product_name", "category", "quantity"]]

sample_return = returns_df.iloc[0]
alt = recommend_alternative(sample_return["lat"], sample_return["lon"])
print(alt.head())

# =================================================
# ✅ END
# =================================================

#Smart Forecast – Live	Rolling Avg + Z-score
#Smart Forecast – Future	Prophet (Time Series)
#Opportunity Detection	Business Rules
#Alternative Product	K-NN
#Sell Probability	Logistic Regression
#Channel Analytics	Aggregation



#Smart Forecast
