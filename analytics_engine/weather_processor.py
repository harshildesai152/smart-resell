import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

class WeatherProcessor:
    def __init__(self):
        self.returns_df = None
        self.sales_df = None
        self.processed_data = {}

    def load_and_process_data(self, returns_file=None, sales_file=None):
        """Load and process data using combined logic from near.py, near1.py, near2.py, near3.py, near6.py"""

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

        # Apply weather analysis (near6.py)
        self.processed_data = self._weather_analysis()

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
            'category': ['category']
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

        # Ensure weather and category are strings
        df["weather"] = df.get("weather", "").astype(str).str.title()
        df["category"] = df.get("category", "").astype(str)

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
            'lon': ['lon', 'longitude']
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

        # Ensure weather and category are strings
        df["weather"] = df.get("weather", "").astype(str).str.title()
        df["category"] = df.get("category", "").astype(str)

        print(f"✅ Cleaned sales data: {len(df)} records")
        return df

    def _weather_analysis(self):
        """Weather analysis logic from near6.py"""
        if self.returns_df is None or self.sales_df is None:
            return None

        # Ensure required columns exist
        returns_required = ["product_name", "return_lat", "return_lon", "weather", "category"]
        sales_required = ["product_name", "lat", "lon", "platform", "weather", "category", "sales_count"]

        for col in returns_required:
            if col not in self.returns_df.columns:
                print(f"⚠️ Missing required column in returns data: {col}")
                return None

        for col in sales_required:
            if col not in self.sales_df.columns:
                print(f"⚠️ Missing required column in sales data: {col}")
                return None

        # Clean data
        returns_df = self.returns_df.dropna(subset=["product_name", "return_lat", "return_lon"]).copy()
        sales_df = self.sales_df.dropna(subset=["product_name", "lat", "lon", "platform"]).copy()

        # ML Model training (from near6.py)
        cat_enc = LabelEncoder()
        weather_enc = LabelEncoder()

        sales_df["category_code"] = cat_enc.fit_transform(sales_df["category"])
        sales_df["weather_code"] = weather_enc.fit_transform(sales_df["weather"])
        sales_df["sold"] = (sales_df["sales_count"] > 0).astype(int)

        X = sales_df[["category_code", "weather_code", "sales_count"]]
        y = sales_df["sold"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        log_model = LogisticRegression(max_iter=1000)
        log_model.fit(X_train, y_train)

        # Generate ML predictions
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
                lambda s: haversine(r["return_lat"], r["return_lon"], s["lat"], s["lon"]),
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
                "city": r.get("city", "Unknown"),
                "return_price": r.get("price", 0),
                "sell_probability": round(sell_prob, 2),
                "recommended_app": nearest.get("platform", "Unknown"),
                "recommended_city": nearest["city"],
                "ml_used": True
            })

        final_ml_df = pd.DataFrame(ml_results)

        # PAGE-1: Weather Impact Assessment
        page1_graph = (
            final_ml_df.groupby("category")["product_name"]
            .count()
            .reset_index(name="sales_count")
        )

        # Weather list for analysis
        WEATHER_LIST = ["Sunny", "Rainy", "Cloudy", "Windy", "Winter"]

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

        # PAGE-2: Product Performance by Weather
        page2_graph = (
            final_ml_df.groupby("weather")["product_name"]
            .count()
            .reset_index(name="sales_count")
        )

        # Weather Impact Statistics Table
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

        return {
            "weather_impact_table": weather_impact_table,
            "page2_graph": page2_graph,
            "page1_graph": page1_graph,
            "page1_tables": page1_tables,
            "ml_results": final_ml_df
        }

# Utility function
def haversine(lat1, lon1, lat2, lon2):
    """Calculate haversine distance between two points"""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    return 6371 * 2 * asin(sqrt(a))