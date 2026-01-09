import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

class SegmentationProcessor:
    def __init__(self):
        self.returns_df = None
        self.sales_df = None
        self.processed_data = {}

    def load_and_process_data(self, returns_file=None, sales_file=None):
        """Load and process data using combined logic from near.py, near1.py, near2.py, near3.py, near10.py"""

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

        # Apply segmentation analysis (near10.py)
        self.processed_data = self._segmentation_analysis()

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

        # Ensure required columns for segmentation analysis exist
        required_cols = ["order_value", "commission_rate", "delivery_time_min", "conversion_rate", "return_rate", "rating"]
        for col in required_cols:
            if col not in df.columns:
                print(f"⚠️ Missing required column for segmentation analysis: {col}")
                # Create dummy data if missing
                if col in ["order_value", "commission_rate", "conversion_rate", "return_rate"]:
                    df[col] = np.random.uniform(0.1, 1.0, len(df))
                elif col == "delivery_time_min":
                    df[col] = np.random.uniform(10, 30, len(df))
                elif col == "rating":
                    df[col] = np.random.uniform(3.5, 5.0, len(df))

        print(f"✅ Cleaned sales data: {len(df)} records")
        return df

    def _segmentation_analysis(self):
        """Segmentation analysis logic from near10.py"""
        if self.returns_df is None or self.sales_df is None:
            return None

        returns_df = self.returns_df.copy()
        sales_df = self.sales_df.copy()

        # Ensure city columns are strings
        returns_df["city"] = returns_df["city"].astype(str)
        sales_df["city"] = sales_df["city"].astype(str)

        # =================================================
        # 📊 CITY DEMAND & RETURNS AGGREGATION
        # =================================================

        city_demand = (
            sales_df.groupby("city")["qty"]
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

        # Calculate return percentage
        city_metrics["return_pct"] = (
            city_metrics["total_returns"] /
            (city_metrics["total_sales"] + city_metrics["total_returns"])
        ) * 100

        # Get coordinates for each city
        coords = (
            sales_df.groupby("city")[["lat", "lon"]]
            .mean()
            .reset_index()
        )

        city_metrics = city_metrics.merge(coords, on="city", how="left")

        # =================================================
        # 📍 K-MEANS CLUSTERING
        # =================================================

        cluster_features = city_metrics[[
            "total_sales", "return_pct"
        ]].fillna(0)

        n_samples = len(cluster_features)
        n_clusters = min(4, n_samples)   # Safe clustering

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
        # 📊 KPI CALCULATIONS
        # =================================================

        total_cities = city_metrics["city"].nunique()
        high_demand_clusters = city_metrics[
            city_metrics["zone_type"].str.contains("High Demand")
        ]["city"].nunique()

        high_return_zones = city_metrics[
            city_metrics["zone_type"].str.contains("High Return")
        ]["city"].nunique()

        # Note: The user asked for "Expansion Opportunities" which should be High Demand / Low Return zones
        expansion_opportunities = city_metrics[
            city_metrics["zone_type"] == "🟢 High Demand / Low Return"
        ]["city"].nunique()

        # =================================================
        # 🗺️ CITY CLUSTER MAP DATA
        # =================================================

        city_cluster_map = city_metrics[[
            "city", "lat", "lon", "zone_type", "total_sales", "return_pct"
        ]].copy()

        # Add cluster colors for map visualization
        zone_colors = {
            "🟢 High Demand / Low Return": "#00E676",
            "🔴 High Demand / High Return": "#FF5252",
            "🟡 Low Demand / High Return": "#FFB74D",
            "🟣 Stable Zone": "#7C4DFF"
        }

        city_cluster_map["zone_color"] = city_cluster_map["zone_type"].map(zone_colors)

        # =================================================
        # 🚨 HIGH-RISK ZONES TABLE
        # =================================================

        def risk_level(pct):
            if pct >= 25:
                return "🔴 Critical"
            elif pct >= 12:
                return "🟡 High"
            elif pct >= 8:
                return "🟠 Medium"
            return "🟢 Low"

        city_metrics["risk_level"] = city_metrics["return_pct"].apply(risk_level)

        high_risk_table = city_metrics[[
            "city",
            "risk_level",
            "return_pct",
            "total_sales"
        ]].rename(columns={
            "return_pct": "return_pct",
            "total_sales": "demand"
        }).sort_values("return_pct", ascending=False)

        # Format return percentage for display
        high_risk_table["return_pct_display"] = high_risk_table["return_pct"].round(1).astype(str) + "%"

        # Format demand for display
        high_risk_table["demand_display"] = high_risk_table["demand"].apply(
            lambda x: "High" if x >= sales_avg else "Medium" if x >= sales_avg * 0.5 else "Low"
        )

        return {
            "kpi_metrics": {
                "total_cities": total_cities,
                "high_demand_clusters": high_demand_clusters,
                "high_return_zones": high_return_zones,
                "expansion_opportunities": expansion_opportunities
            },
            "city_cluster_map": city_cluster_map.to_dict('records'),
            "high_risk_zones": high_risk_table[[
                "city", "risk_level", "return_pct_display", "demand_display"
            ]].rename(columns={
                "return_pct_display": "return_pct",
                "demand_display": "demand"
            }).to_dict('records'),
            "zone_colors": zone_colors,
            "city_metrics": city_metrics.to_dict('records')
        }