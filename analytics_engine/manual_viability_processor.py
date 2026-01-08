import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor

class ManualViabilityProcessor:
    def __init__(self, sales_df=None):
        self.sales_df = sales_df
        self.encoders = {}
        self.fallback_values = {}
        self.log_model = None
        self.knn_model = None
        self.price_model = None
        self.trained = False

    def load_and_train_models(self, sales_df=None):
        """Load sales data and train the ML models for manual viability check"""
        if sales_df is not None:
            self.sales_df = sales_df

        if self.sales_df is None:
            return False

        # Apply data cleaning logic from near3.py
        self._clean_sales_data()

        # Train the ML models (logic from near5.py)
        self._train_models()
        self.trained = True
        return True

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
            'price': ['price', 'sale_price', 'selling_price', 'unit_price']
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

        if "price" not in df.columns:
            print("⚠️ 'price' column not found — assuming price = 1000")
            df["price"] = 1000

        self.sales_df = df

    def _train_models(self):
        """Train the ML models (logic from near5.py)"""
        # Safe Encoding
        for col in ["category", "weather", "city", "platform"]:
            if col in self.sales_df.columns:
                le = LabelEncoder()
                self.sales_df[col] = self.sales_df[col].astype(str)
                self.sales_df[col] = le.fit_transform(self.sales_df[col])
                self.encoders[col] = le
                self.fallback_values[col] = le.classes_[0]

        def safe_encode(col, value):
            if value in self.encoders[col].classes_:
                return self.encoders[col].transform([value])[0]
            return self.encoders[col].transform([self.fallback_values[col]])[0]

        # Target Variable
        self.sales_df["sold"] = (self.sales_df["qty"] > 0).astype(int)

        # Logistic Regression (Demand)
        X = self.sales_df[["category", "price", "weather", "city"]]
        y = self.sales_df["sold"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.log_model = LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        )
        self.log_model.fit(X_train, y_train)

        # KNN (Recommended App)
        self.knn_model = KNeighborsClassifier(n_neighbors=5)
        self.knn_model.fit(X, self.sales_df["platform"])

        # Gradient Boosting (Price Model)
        price_features = self.sales_df[["category", "weather", "city"]]
        price_target = self.sales_df["price"]

        self.price_model = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=3,
            random_state=42
        )
        self.price_model.fit(price_features, price_target)

    def analyze_product(self, product_details):
        """Analyze a single product's viability using the trained models"""
        if not self.trained:
            return {"error": "Models not trained. Please load sales data first."}

        def safe_encode(col, value):
            if value in self.encoders[col].classes_:
                return self.encoders[col].transform([value])[0]
            return self.encoders[col].transform([self.fallback_values[col]])[0]

        # Prepare input data
        manual_df = pd.DataFrame([{
            "category": safe_encode("category", product_details.get("category", "")),
            "price": product_details.get("original_price", 1000),
            "weather": safe_encode("weather", product_details.get("weather", "")),
            "city": safe_encode("city", product_details.get("city", ""))
        }])

        # Base SELL Probability (Demand)
        base_prob = self.log_model.predict_proba(manual_df)[0][1]

        # Recommended App
        app_code = self.knn_model.predict(manual_df)[0]
        recommended_app = self.encoders["platform"].inverse_transform([app_code])[0]

        # Price Acceptance (GBM)
        predicted_market_price = self.price_model.predict(
            manual_df[["category", "weather", "city"]]
        )[0]

        price_ok = product_details.get("original_price", 1000) <= predicted_market_price

        if not price_ok:
            base_prob *= 0.5   # price too high → reduce probability

        # Weather Impact
        seasonal_boost = {
            # 🌞 SUMMER
            "Air Conditioner": ["Summer"], "Cooler": ["Summer"], "Fan": ["Summer"],
            "Water Cooler": ["Summer"], "Refrigerator": ["Summer"], "Ice Cream": ["Summer"],
            "Cold Drink": ["Summer"], "Juice": ["Summer"], "Soft Drink": ["Summer"],
            "Sunscreen": ["Summer"], "Cotton Clothes": ["Summer"], "T-Shirt": ["Summer"],
            "Shorts": ["Summer"], "Cap": ["Summer"],

            # ❄️ WINTER
            "Heater": ["Winter"], "Room Heater": ["Winter"], "Geyser": ["Winter"],
            "Blanket": ["Winter"], "Quilt": ["Winter"], "Jacket": ["Winter"],
            "Sweater": ["Winter"], "Hoodie": ["Winter"], "Thermal Wear": ["Winter"],
            "Gloves": ["Winter"],

            # 🌧️ RAINY
            "Raincoat": ["Rainy"], "Umbrella": ["Rainy"], "Rain Shoes": ["Rainy"],
            "Waterproof Jacket": ["Rainy"], "Mosquito Repellent": ["Rainy"],
            "Insect Killer": ["Rainy"],

            # 🍲 MULTI-SEASON
            "Tea": ["Winter", "Rainy"], "Coffee": ["Winter", "Rainy"],
            "Soup": ["Winter", "Rainy"], "Instant Noodles": ["Winter", "Rainy"],
            "Snacks": ["Rainy", "Winter"],

            # ⚖️ ALL-SEASON / NEUTRAL
            "Electronics": ["Summer", "Winter", "Rainy"], "Smart Watch": ["Summer", "Winter", "Rainy"],
            "Mobile Phone": ["Summer", "Winter", "Rainy"], "Headphones": ["Summer", "Winter", "Rainy"]
        }

        weather_impact = "Neutral ⚖️"
        category = product_details.get("category", "")
        weather = product_details.get("weather", "")

        if category in seasonal_boost:
            if weather in seasonal_boost[category]:
                base_prob *= 1.15
                weather_impact = "Significant ✅"
            else:
                base_prob *= 0.7
                weather_impact = "Not Significant ❌"

        # Final Probability Clamp
        sell_probability = round(
            min(max(base_prob, 0.05), 0.95) * 100, 2
        )

        # Estimated Profit
        logistics_cost = 60
        est_profit = round(predicted_market_price - product_details.get("original_price", 1000) - logistics_cost, 2)

        return {
            "product_name": product_details.get("product_name", ""),
            "sell_probability": f"{sell_probability}%",
            "est_profit": f"₹{est_profit}",
            "recommended_app": recommended_app,
            "weather_impact": weather_impact,
            "predicted_market_price": f"₹{round(predicted_market_price, 2)}",
            "price_acceptable": "YES ✅" if price_ok else "NO ❌"
        }