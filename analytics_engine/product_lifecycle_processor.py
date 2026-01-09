import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

class ProductLifecycleProcessor:
    def __init__(self):
        self.sales_df = None
        self.processed_data = {}

    def load_and_process_data(self, returns_file=None, sales_file=None):
        """Load and process data using combined logic from near.py, near1.py, near2.py, near3.py, near11.py"""

        # Load data
        if sales_file:
            self.sales_df = pd.read_excel(sales_file) if sales_file.endswith('.xlsx') else pd.read_csv(sales_file)

        if self.sales_df is None:
            return None

        # Apply data cleaning logic (near.py, near1.py, near2.py, near3.py)
        self.sales_df = self._clean_sales_data()

        # Apply product lifecycle analysis (near11.py)
        self.processed_data = self._product_lifecycle_analysis()

        return self.processed_data

    def _clean_sales_data(self):
        """Combined data cleaning logic from near3.py (simplified for sales data)"""
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

        # Ensure product_name is string
        if "product_name" in df.columns:
            df["product_name"] = df["product_name"].astype(str)

        # Ensure weather and category are strings
        df["weather"] = df.get("weather", "").astype(str).str.title()
        df["category"] = df.get("category", "").astype(str).str.title()

        print(f"✅ Cleaned sales data: {len(df)} records")
        return df

    def _product_lifecycle_analysis(self):
        """Product lifecycle analysis logic from near11.py"""
        if self.sales_df is None:
            return None

        df = self.sales_df.copy()

        # =================================================
        # 📊 MONTHLY DEMAND AGGREGATION
        # =================================================

        monthly_demand = (
            df.groupby(["product_name", "month"])["qty"]
            .sum()
            .reset_index()
        )

        # =================================================
        # 🧠 LIFECYCLE CLASSIFICATION WITH LINEAR REGRESSION
        # =================================================

        results = []

        for product, grp in monthly_demand.groupby("product_name"):
            grp = grp.sort_values("month")

            if len(grp) < 3:
                # New products with insufficient data points
                stage = "New"
                trend = "Growing"
                action = "Increase inventory by 25%"
                emoji_trend = "📈"
                emoji_stage = "🟡"
            else:
                # Linear regression analysis
                X = np.arange(len(grp)).reshape(-1, 1)
                y = grp["qty"].values

                model = LinearRegression()
                model.fit(X, y)
                slope = model.coef_[0]

                if slope > 1:
                    trend = "Growing"
                    stage = "New"
                    action = "Increase inventory by 25%"
                    emoji_trend = "📈"
                    emoji_stage = "🟡"
                elif slope > -1:
                    trend = "Stable"
                    stage = "Mature"
                    action = "Maintain current stock levels"
                    emoji_trend = "➡️"
                    emoji_stage = "🟢"
                else:
                    trend = "Declining"
                    stage = "Declining"
                    action = "Reduce procurement by 40%"
                    emoji_trend = "📉"
                    emoji_stage = "🔴"

            results.append({
                "product_name": product,
                "demand_trend": f"{emoji_trend} {trend}",
                "lifecycle_stage": f"{emoji_stage} {stage}",
                "action_recommendation": action
            })

        lifecycle_df = pd.DataFrame(results)

        # =================================================
        # 📌 KPI CALCULATIONS
        # =================================================

        total_products = lifecycle_df.shape[0]
        new_products = (lifecycle_df["lifecycle_stage"].str.contains("New")).sum()
        mature_products = (lifecycle_df["lifecycle_stage"].str.contains("Mature")).sum()
        declining_products = (lifecycle_df["lifecycle_stage"].str.contains("Declining")).sum()

        # =================================================
        # 📈 PRODUCT DEMAND TRENDS CHART DATA
        # =================================================

        trend_chart_data = (
            monthly_demand.pivot(
                index="month",
                columns="product_name",
                values="qty"
            )
            .fillna(0)
            .round(1)
        )

        # =================================================
        # 🚨 CRITICAL INSIGHT
        # =================================================

        declining = lifecycle_df[lifecycle_df["lifecycle_stage"].str.contains("Declining")]

        if not declining.empty:
            critical_product = declining.iloc[0]["product_name"]
            insight = (
                f"Critical Insight: {critical_product} shows declining demand trend — "
                f"reduce procurement by 40% to avoid inventory buildup."
            )
        else:
            insight = "All products show stable or growing demand."

        # =================================================
        # 📦 PROCUREMENT STRATEGY RECOMMENDATIONS
        # =================================================

        increase_inventory = lifecycle_df[
            lifecycle_df["action_recommendation"].str.contains("Increase")
        ]["product_name"].tolist()

        maintain_stock = lifecycle_df[
            lifecycle_df["action_recommendation"].str.contains("Maintain")
        ]["product_name"].tolist()

        reduce_procurement = lifecycle_df[
            lifecycle_df["action_recommendation"].str.contains("Reduce")
        ]["product_name"].tolist()

        return {
            "kpi_metrics": {
                "total_products": total_products,
                "new_products": new_products,
                "mature_products": mature_products,
                "declining_products": declining_products
            },
            "trend_chart_data": trend_chart_data.to_dict('index'),
            "lifecycle_table": lifecycle_df.to_dict('records'),
            "critical_insight": insight,
            "procurement_strategy": {
                "increase_inventory": increase_inventory[:3],  # Limit to top 3 for display
                "maintain_stock": maintain_stock[:3],  # Limit to top 3 for display
                "reduce_procurement": reduce_procurement[:3]  # Limit to top 3 for display
            }
        }