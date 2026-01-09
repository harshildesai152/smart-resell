import pandas as pd
import numpy as np
import os
import requests
from math import radians
from sklearn.neighbors import NearestNeighbors
from prophet import Prophet

class SmartForecastProcessor:
    def __init__(self):
        self.returns_df = None
        self.sales_df = None
        self.processed_data = {}

    def load_and_process_data(self, returns_file=None, sales_file=None):
        """Load and process data using combined logic from near.py, near1.py, near2.py, near3.py, near9.py"""

        # Load data
        if returns_file:
            self.returns_df = pd.read_excel(returns_file) if returns_file.endswith('.xlsx') else pd.read_csv(returns_file)
        if sales_file:
            self.sales_df = pd.read_excel(sales_file) if sales_file.endswith('.xlsx') else pd.read_csv(sales_file)

        if self.returns_df is None or self.sales_df is None:
            return None

        # Apply data cleaning logic (near.py, near1.py, near2.py, near3.py)
        if self.returns_df is not None:
            self.returns_df = self._clean_returns_data()
        if self.sales_df is not None:
            self.sales_df = self._clean_sales_data()

        # Apply smart forecast analysis (near9.py)
        self.processed_data = self._smart_forecast_analysis()

        return self.processed_data

    def _clean_returns_data(self):
        """Combined data cleaning logic from near.py, near1.py, near2.py"""
        df = self.returns_df.copy()

        # near.py logic: Clean column names and remove missing critical data
        df.columns = df.columns.str.strip().str.lower()

        # Handle different column name variations
        column_mapping = {
            'return_lat': ['return_lat', 'lat'],
            'return_lon': ['return_lon', 'lon'],
            'return product platform': ['return product platform', 'platform'],
            'product_name': ['product_name', 'product name', 'product'],
            'city': ['city', 'return_city'],
            'order_id': ['order_id', 'order id'],
            'brand': ['brand'],
            'price': ['price'],
            'qty': ['qty', 'quantity'],
            'weather': ['weather', 'weather condition'],
            'category': ['category'],
            'return_date': ['return_date', 'return date', 'date']
        }

        # Rename columns to standard names
        for standard_col, possible_names in column_mapping.items():
            for possible_name in possible_names:
                if possible_name in df.columns:
                    df.rename(columns={possible_name: standard_col}, inplace=True)
                    break

        required_cols = ["return_lat", "return_lon"]
        for col in required_cols:
            if col not in df.columns:
                print(f"⚠️ Missing column: {col}")
                continue

        # near.py logic: Handle missing values and convert to numeric
        df[required_cols] = (
            df[required_cols]
            .replace(r'^\s*$', pd.NA, regex=True)
        )

        df["return_lat"] = pd.to_numeric(df["return_lat"], errors="coerce")
        df["return_lon"] = pd.to_numeric(df["return_lon"], errors="coerce")

        # Remove rows with missing lat/lon
        removed_rows = df[
            df["return_lat"].isna() | df["return_lon"].isna()
        ]

        if not removed_rows.empty:
            print(f"❌ Removed {len(removed_rows)} rows with missing lat/lon")

        df = df.drop(removed_rows.index).reset_index(drop=True)

        # near1.py logic: Remove duplicates based on lat/lon
        duplicate_rows = df[df.duplicated(subset=["return_lat", "return_lon"], keep="first")]
        if not duplicate_rows.empty:
            print(f"❌ Removed {len(duplicate_rows)} duplicate rows")
        df = df.drop_duplicates(subset=["return_lat", "return_lon"], keep="first").reset_index(drop=True)

        # near2.py logic: Handle price data
        if "price" in df.columns:
            df["price"] = df["price"].replace("", pd.NA)
            df["price"] = pd.to_numeric(df["price"], errors="coerce")

            if "qty" in df.columns and "brand" in df.columns:
                missing_price_index = df[df["price"].isna()].index

                df["unit_price"] = df["price"] / df["qty"]

                unit_price_map = (
                    df.dropna(subset=["unit_price"])
                      .groupby("brand")["unit_price"]
                      .first()
                )

                df["price"] = df.apply(
                    lambda row: unit_price_map.get(row["brand"], row["price"]) * row["qty"]
                    if pd.isna(row["price"]) and row["brand"] in unit_price_map.index and pd.notna(row["qty"])
                    else row["price"],
                    axis=1
                )

                df.drop(columns=["unit_price"], errors="ignore", inplace=True)

        # Ensure weather and category are strings, handle return_date
        df["weather"] = df.get("weather", "").astype(str).str.title()
        df["category"] = df.get("category", "").astype(str).str.title()

        if "return_date" in df.columns:
            df["return_date"] = pd.to_datetime(df["return_date"], errors="coerce")

        print(f"✅ Cleaned returns data: {len(df)} records")
        return df

    def _clean_sales_data(self):
        """Combined data cleaning logic from near3.py"""
        df = self.sales_df.copy()

        # Clean column names
        df.columns = df.columns.str.strip().str.lower()

        # Handle column name variations
        column_mapping = {
            'product_name': ['product_name', 'product name', 'product'],
            'platform': ['platform', 'app', 'channel'],
            'qty': ['qty', 'quantity', 'sales_count'],
            'weather': ['weather', 'weather condition', 'weather_condition'],
            'brand': ['brand'],
            'category': ['category'],
            'city': ['city'],
            'lat': ['lat', 'latitude'],
            'lon': ['lon', 'longitude'],
            'sale_date': ['sale_date', 'sale date', 'date'],
            'order_value': ['order_value', 'order value', 'value'],
            'commission_rate': ['commission_rate', 'commission', 'rate'],
            'delivery_time_min': ['delivery_time_min', 'delivery_time', 'time'],
            'conversion_rate': ['conversion_rate', 'conversion'],
            'return_rate': ['return_rate', 'return rate'],
            'rating': ['rating', 'customer_rating']
        }

        # Rename columns to standard names
        for standard_col, possible_names in column_mapping.items():
            for possible_name in possible_names:
                if possible_name in df.columns:
                    df.rename(columns={possible_name: standard_col}, inplace=True)
                    break

        # near3.py logic: Handle weather data imputation
        if "weather" in df.columns:
            df["weather"] = df["weather"].replace("", np.nan)

            if "brand" in df.columns and "qty" in df.columns:
                # Fill missing weather based on brand's most selling weather pattern
                brand_weather_qty = (
                    df.dropna(subset=["weather"])
                      .groupby(["brand", "weather"], as_index=False)["qty"]
                      .sum()
                )

                top_weather_per_brand = (
                    brand_weather_qty
                      .sort_values(by=["brand", "qty"], ascending=[True, False])
                      .drop_duplicates(subset=["brand"])
                      .rename(columns={"weather": "top_weather"})
                      [["brand", "top_weather"]]
                )

                df = df.merge(top_weather_per_brand, on="brand", how="left")
                df["weather"] = df["weather"].fillna(df["top_weather"])
                df["weather"] = df["weather"].fillna("Unknown")
                df.drop(columns=["top_weather"], inplace=True, errors="ignore")

        # Ensure required columns exist
        if "qty" not in df.columns:
            print("⚠️ 'qty' column not found — assuming qty = 1 per sale")
            df["qty"] = 1

        if "sales_count" not in df.columns:
            df["sales_count"] = df["qty"]

        # Ensure date column and month extraction
        if "sale_date" in df.columns:
            df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
            df["month"] = df["sale_date"].dt.month

        # Ensure weather and category are strings
        df["weather"] = df.get("weather", "").astype(str).str.title()
        df["category"] = df.get("category", "").astype(str).str.title()

        # Ensure required columns for forecast analysis exist
        required_cols = ["order_value", "commission_rate", "delivery_time_min", "conversion_rate", "return_rate", "rating"]
        for col in required_cols:
            if col not in df.columns:
                print(f"⚠️ Missing required column for forecast analysis: {col}")
                # Create dummy data if missing
                if col in ["order_value", "commission_rate", "conversion_rate", "return_rate"]:
                    df[col] = np.random.uniform(0.1, 1.0, len(df))
                elif col == "delivery_time_min":
                    df[col] = np.random.uniform(10, 30, len(df))
                elif col == "rating":
                    df[col] = np.random.uniform(3.5, 5.0, len(df))

        print(f"✅ Cleaned sales data: {len(df)} records")
        return df

    def _smart_forecast_analysis(self):
        """Smart forecast analysis logic from near9.py"""
        if self.returns_df is None or self.sales_df is None:
            return None

        returns_df = self.returns_df.copy()
        sales_df = self.sales_df.copy()

        # =================================================
        # 🌦 WEATHER API AND SEASON MAPPING
        # =================================================

        def get_season(month):
            if month in [12, 1, 2]:
                return "Winter"
            if month in [3, 4, 5]:
                return "Summer"
            if month in [6, 7, 8]:
                return "Rainy"
            return "Cloudy"

        # Load API key from .env file
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

        load_env_file()
        OPENWEATHER_API_KEY = os.getenv("API_kay", "API")
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
                # Fallback to most recent weather in data
                if not sales_df.empty and "weather" in sales_df.columns:
                    fallback_weather = sales_df["weather"].mode().iloc[0] if not sales_df["weather"].mode().empty else "Sunny"
                    return "Derived", fallback_weather
                return "Derived", "Sunny"

        # Get current weather
        temp, CURRENT_WEATHER = get_weather_safe(CITY_FOR_WEATHER)
        CURRENT_TEMP = f"{temp}°C" if isinstance(temp, (int, float)) else temp

        # Add season mapping to sales data
        sales_df["season"] = sales_df["month"].apply(get_season)

        # =================================================
        # 🔴 LIVE OPPORTUNITY – CURRENT WEATHER IMPACT
        # =================================================

        recent_days = 14
        latest = sales_df["sale_date"].max() if not sales_df["sale_date"].isna().all() else pd.Timestamp.now()

        recent = sales_df[sales_df["sale_date"] >= latest - pd.Timedelta(days=recent_days)]
        baseline = sales_df[sales_df["sale_date"] < latest - pd.Timedelta(days=recent_days)]

        # Current weather impact analysis
        live_opportunity = (
            recent[recent["weather"] == CURRENT_WEATHER]
            .groupby(["product_name", "category"])
            .agg(current_velocity=("qty", "sum"))
            .reset_index()
        )

        baseline_avg = (
            baseline.groupby(["product_name", "category"])["qty"]
            .mean()
            .reset_index(name="baseline_velocity")
        )

        live_opportunity = live_opportunity.merge(baseline_avg, on=["product_name", "category"], how="left").dropna()
        live_opportunity["velocity_ratio"] = live_opportunity["current_velocity"] / live_opportunity["baseline_velocity"]

        def stock_status(v):
            if v >= 1.5: return "High"
            if v >= 1.1: return "Medium"
            return "Low"

        live_opportunity["stock_status"] = live_opportunity["velocity_ratio"].apply(stock_status)

        # Format current velocity for display
        live_opportunity["current_velocity_display"] = live_opportunity["velocity_ratio"].apply(
            lambda x: f"+{int((x-1)*100)}% vs avg" if x > 1 else f"{int((x-1)*100)}% vs avg"
        )

        # =================================================
        # 🔵 FUTURE SIGNAL – NEXT MONTH FORECAST
        # =================================================

        next_month = (latest.month % 12) + 1 if hasattr(latest, 'month') else 7  # Default to July if no date
        NEXT_SEASON = get_season(next_month)

        # Get next month weather forecast (simplified - using seasonal average)
        next_month_weather = NEXT_SEASON  # Use season as weather proxy
        next_month_temp = "32°C" if NEXT_SEASON == "Summer" else "18°C" if NEXT_SEASON == "Rainy" else "25°C"

        # Seasonal sales forecasting
        seasonal_sales = (
            sales_df[sales_df["season"] == NEXT_SEASON]
            .groupby(["product_name", "category"])
            .agg(avg_monthly_sales=("qty", "mean"))
            .reset_index()
        )

        def demand_label(v):
            if v >= 15: return "Very High"
            if v >= 8: return "High (+200%)"
            if v >= 4: return "Moderate"
            return "Low"

        def action(v):
            if v >= 15: return "Increase Order"
            if v >= 8: return "Stock Up Now"
            if v >= 4: return "Monitor"
            return "Avoid"

        seasonal_sales["forecasted_demand"] = seasonal_sales["avg_monthly_sales"].round(1)
        seasonal_sales["forecasted_demand_label"] = seasonal_sales["avg_monthly_sales"].apply(demand_label)
        seasonal_sales["recommended_action"] = seasonal_sales["avg_monthly_sales"].apply(action)

        # =================================================
        # 📈 PROPHET FORECASTING (Optional Advanced Feature)
        # =================================================

        prophet_forecasts = []
        try:
            for (product_name, category), group in sales_df.groupby(["product_name", "category"]):
                ts = group.groupby("sale_date")["qty"].sum().reset_index()
                if len(ts) < 10:  # Need minimum data points
                    continue

                ts.columns = ["ds", "y"]
                m = Prophet(yearly_seasonality=True)
                m.fit(ts)
                future = m.make_future_dataframe(periods=30)
                forecast = m.predict(future)
                next_month_demand = forecast.tail(30)["yhat"].mean()

                prophet_forecasts.append({
                    "product_name": product_name,
                    "category": category,
                    "prophet_forecast": round(next_month_demand, 1)
                })
        except Exception as e:
            print(f"⚠️ Prophet forecasting failed: {e}")

        return {
            "current_weather": {
                "condition": CURRENT_WEATHER,
                "temperature": CURRENT_TEMP
            },
            "next_month_weather": {
                "condition": next_month_weather,
                "temperature": next_month_temp
            },
            "live_opportunity": live_opportunity[[
                "product_name", "category", "current_velocity_display", "stock_status"
            ]].head(10).to_dict('records'),
            "future_forecast": seasonal_sales[[
                "product_name", "category", "forecasted_demand_label", "recommended_action"
            ]].head(10).to_dict('records'),
            "prophet_forecasts": prophet_forecasts
        }