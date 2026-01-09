import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt

class DemandProcessor:
    def __init__(self):
        self.returns_df = None
        self.sales_df = None
        self.processed_data = {}

    def load_and_process_data(self, returns_file=None, sales_file=None):
        """Load and process data using combined logic from near.py, near1.py, near2.py, near3.py, near7.py"""

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

        # Apply demand matching analysis (near7.py)
        self.processed_data = self._demand_matching_analysis()

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
            'sale_date': ['sale_date', 'sale date', 'date']
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

        # Ensure weather and category are strings, handle sale_date
        df["weather"] = df.get("weather", "").astype(str).str.title()
        df["category"] = df.get("category", "").astype(str).str.title()

        if "sale_date" in df.columns:
            df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")

        print(f"✅ Cleaned sales data: {len(df)} records")
        return df

    def _demand_matching_analysis(self):
        """Demand matching analysis logic from near7.py"""
        if self.returns_df is None or self.sales_df is None:
            return None

        # Ensure required columns exist
        returns_required = ["product_name", "category", "city", "return_lat", "return_lon", "weather"]
        sales_required = ["product_name", "category", "platform", "lat", "lon", "weather", "sales_count", "sale_date"]

        for col in returns_required:
            if col not in self.returns_df.columns:
                print(f"⚠️ Missing required column in returns data: {col}")
                return None

        for col in sales_required:
            if col not in self.sales_df.columns:
                print(f"⚠️ Missing required column in sales data: {col}")
                return None

        # Clean data
        returns_df = self.returns_df.copy()
        sales_df = self.sales_df.copy()

        # 1. RECENT RETURNS (UI LEFT PANEL)
        # Sort by return_date if available, otherwise just take first 8
        if "return_date" in returns_df.columns and returns_df["return_date"].notna().any():
            recent_returns = returns_df.sort_values("return_date", ascending=False).head(8)
        else:
            recent_returns = returns_df.head(8)

        recent_returns = recent_returns[[
            "product_name", "category", "city", "return_lat", "return_lon", "weather"
        ]].reset_index(drop=True)

        # 2. DEMAND MATCHING ANALYSIS (KNN)
        K = 5  # number of nearest neighbors
        ui_results = []

        for idx, r in recent_returns.iterrows():
            # Step 1: Filter similar category
            candidates = sales_df[sales_df["category"] == r["category"]].copy()
            if candidates.empty:
                # Create empty result for items with no matches
                ui_results.append({
                    "id": idx,
                    "product_name": r["product_name"],
                    "category": r["category"],
                    "city": r["city"],
                    "lat": r["return_lat"],
                    "lon": r["return_lon"],
                    "weather": r["weather"],
                    "local_similar_sales": 0,
                    "avg_distance_km": 0.0,
                    "resale_viability": "None",
                    "evidence": pd.DataFrame()  # Empty dataframe
                })
                continue

            # Step 2: Compute distance (KNN core)
            candidates["distance_km"] = candidates.apply(
                lambda s: haversine(
                    r["return_lat"], r["return_lon"],
                    s["lat"], s["lon"]
                ),
                axis=1
            )

            # Step 3: Get K nearest neighbors
            knn_neighbors = candidates.sort_values("distance_km").head(K)

            # Step 4: Metrics for Demand Matching Analysis
            local_similar_sales = len(knn_neighbors)
            avg_distance = round(knn_neighbors["distance_km"].mean(), 2) if not knn_neighbors.empty else 0.0

            # Step 5: Resale viability logic (business rules)
            if local_similar_sales >= 5 and avg_distance <= 5:
                resale_viability = "High"
            elif local_similar_sales >= 3:
                resale_viability = "Medium"
            else:
                resale_viability = "Low"

            # Prepare evidence data for UI
            evidence_df = knn_neighbors[[
                "sale_date", "platform", "distance_km", "weather", "qty"
            ]].copy()

            # Format sale_date for display
            if "sale_date" in evidence_df.columns:
                evidence_df["sale_date"] = evidence_df["sale_date"].astype(str)

            ui_results.append({
                "id": idx,
                "product_name": r["product_name"],
                "category": r["category"],
                "city": r["city"],
                "lat": r["return_lat"],
                "lon": r["return_lon"],
                "weather": r["weather"],
                "local_similar_sales": local_similar_sales,
                "avg_distance_km": avg_distance,
                "resale_viability": resale_viability,
                "evidence": evidence_df
            })

        return {
            "recent_returns": recent_returns,
            "demand_matching_results": ui_results
        }

# Utility function
def haversine(lat1, lon1, lat2, lon2):
    """Calculate haversine distance between two points"""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    return 6371 * 2 * asin(sqrt(a))