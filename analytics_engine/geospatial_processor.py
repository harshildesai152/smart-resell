import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
from collections import defaultdict

class GeospatialProcessor:
    def __init__(self):
        self.returns_df = None
        self.sales_df = None
        self.processed_data = {}

    def load_and_process_data(self, returns_file=None, sales_file=None):
        """Load and process data using combined logic from near.py, near1.py, near2.py, near3.py, near4.py"""

        # Load data
        if returns_file:
            self.returns_df = pd.read_excel(returns_file) if returns_file.endswith('.xlsx') else pd.read_csv(returns_file)
        if sales_file:
            self.sales_df = pd.read_excel(sales_file) if sales_file.endswith('.xlsx') else pd.read_csv(sales_file)

        if self.returns_df is None and self.sales_df is None:
            return None

        # Apply data cleaning logic (near.py, near1.py, near2.py, near3.py)
        if self.returns_df is not None:
            self.returns_df = self._clean_returns_data()
        if self.sales_df is not None:
            self.sales_df = self._clean_sales_data()

        # Apply geospatial demand analysis (near4.py)
        self.processed_data = self._geospatial_demand_analysis()

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
            'qty': ['qty', 'quantity']
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

        # Ensure qty column exists
        if "qty" not in df.columns:
            print("⚠️ 'qty' column not found — assuming qty = 1 per sale")
            df["qty"] = 1

        print(f"✅ Cleaned sales data: {len(df)} records")
        return df

    def _geospatial_demand_analysis(self):
        """Geospatial demand analysis logic from near4.py"""
        if self.returns_df is None or self.sales_df is None:
            return None

        MAX_DISTANCE_KM = 15
        MIN_TOTAL_QTY = 5
        YES_THRESHOLD = 70
        MAYBE_THRESHOLD = 40

        PLATFORM_WEIGHT = {
            "Blinkit": 1.0,
            "Swiggy Instamart": 0.9,
            "Zepto": 0.8
        }

        # Ensure required columns exist
        returns_required = ["product_name", "return_lat", "return_lon"]
        sales_required = ["product_name", "lat", "lon", "platform", "qty"]

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

        # Regional summary storage
        regional_summary = defaultdict(lambda: {"returns": 0, "sales": 0})
        analysis_results = []

        for _, ret in returns_df.iterrows():
            order_id = ret.get("order_id", f"RET-{len(analysis_results)+1}")
            product = ret["product_name"]
            city = ret.get("city", "Unknown")
            r_lat = ret["return_lat"]
            r_lon = ret["return_lon"]

            matched_sales = sales_df[sales_df["product_name"] == product].copy()

            if matched_sales.empty:
                decision = "NO"
                confidence = 0
                reason = "No instant-delivery sales history"
                regional_summary[city]["returns"] += 1
            else:
                matched_sales.loc[:, "distance_km"] = matched_sales.apply(
                    lambda row: haversine(r_lat, r_lon, row["lat"], row["lon"]),
                    axis=1
                )

                nearby_sales = matched_sales[matched_sales["distance_km"] <= MAX_DISTANCE_KM]

                if nearby_sales.empty:
                    decision = "NO"
                    confidence = 0
                    reason = "No nearby demand within radius"
                    regional_summary[city]["returns"] += 1
                else:
                    total_qty = nearby_sales["qty"].sum()

                    if total_qty < MIN_TOTAL_QTY:
                        decision = "NO"
                        confidence = 0
                        reason = "Insufficient demand volume"
                        regional_summary[city]["returns"] += 1
                    else:
                        platform_qty = nearby_sales.groupby("platform")["qty"].sum()
                        best_app = platform_qty.idxmax()

                        platform_strength = PLATFORM_WEIGHT.get(best_app, 0.7)
                        avg_distance = nearby_sales["distance_km"].mean()

                        distance_score = max(0, (MAX_DISTANCE_KM - avg_distance) / MAX_DISTANCE_KM)
                        demand_score = min(1, total_qty / 30)
                        platform_score = platform_strength

                        confidence = int((
                            0.5 * distance_score +
                            0.3 * demand_score +
                            0.2 * platform_score
                        ) * 100)

                        if confidence < MAYBE_THRESHOLD:
                            decision = "NO"
                            reason = "Low confidence after demand & distance evaluation"
                            regional_summary[city]["returns"] += 1
                        elif confidence < YES_THRESHOLD:
                            decision = "MAYBE"
                            reason = "Moderate demand near return location"
                            regional_summary[city]["sales"] += 1
                        else:
                            decision = "YES"
                            reason = "Strong nearby demand with platform dominance"
                            regional_summary[city]["sales"] += 1

            # Determine best platform if available
            best_platform = "Unknown"
            if not matched_sales.empty and not nearby_sales.empty:
                platform_qty = nearby_sales.groupby("platform")["qty"].sum()
                if not platform_qty.empty:
                    best_platform = platform_qty.idxmax()

            analysis_results.append({
                "order_id": order_id,
                "product": product,
                "city": city,
                "lat": r_lat,
                "lon": r_lon,
                "sell_near_me": decision,
                "sell_confidence": confidence,
                "reason": reason,
                "best_platform": best_platform
            })

        return {
            "regional_summary": dict(regional_summary),
            "analysis_results": analysis_results,
            "map_data": [{"lat": r["lat"], "lon": r["lon"], "decision": r["sell_near_me"],
                         "confidence": r["sell_confidence"], "product": r["product"],
                         "city": r["city"], "platform": r["best_platform"]} for r in analysis_results]
        }

# Utility function
def haversine(lat1, lon1, lat2, lon2):
    """Calculate haversine distance between two points"""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    return 6371 * 2 * asin(sqrt(a))