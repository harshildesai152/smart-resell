# 🚀 Sell Best - AI Inventory Intelligence Platform

## 📋 Table of Contents
- [⚙️ Installation & Setup](#️-installation--setup)
- [🏗️ Project Structure](#️-project-structure)
- [🚀 How to Run](#-how-to-run)
- [🔧 Key Dependencies](#-key-dependencies)

---

## ⚙️ Installation & Setup

### 📋 Prerequisites
- **Python 3.8 or higher**
- **Git**

### 🔄 Step-by-Step Installation

#### 1. **Clone the Repository**
```bash
git clone https://github.com/your-username/sell-best-ai-inventory.git
cd sell-best-ai-inventory
```

#### 2. **Create Virtual Environment** (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

#### 3. **Install Python Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. **Install Streamlit** (If not included in requirements.txt)
```bash
pip install streamlit
```

#### 5. **Setup Environment Variables**
Create a `.env` file in the root directory:
```env
API_kay=your_openweather_api_key_here
```

#### 6. **Verify Installation**
```bash
python -c "import streamlit, pandas, sklearn, plotly; print('✅ All dependencies installed successfully!')"
```

---

## Project Structure

```
sell-best-ai-inventory/
│
├── analytics_engine/           # ML Processing Modules
│   ├── demand_processor.py        # Demand matching & geospatial analysis
│   ├── channel_processor.py       # Multi-platform analytics
│   ├── weather_processor.py       # Weather impact analysis
│   ├── smart_forecast_processor.py # Time-series forecasting
│   ├── segmentation_processor.py  # K-means customer clustering
│   ├── product_lifecycle_processor.py # ML lifecycle classification
│   ├── price_sensitivity_processor.py # Price elasticity modeling
│   └── manual_viability_processor.py # Manual analysis support
|
├── all_SQL_queries/            # Databricks Dashboard SQL Queries
│   ├── TREND_&_STOCK_RULE.sql              # Category performance & stock recommendations
│   ├── WEATHER_IMPACT_STATISTICS.sql         # Weather-based transaction analysis
│   ├── Demand_Matching.sql                  # KNN-based demand matching with Haversine
│   ├── Monthly_Revenue_by_Platform_from_Sales_Data.sql # Channel revenue trends
│   ├── Market_Share.sql                    # Platform market share analysis
│   ├── Sales_Performance_by_Platform_and_Product_Variety.sql # Platform metrics
│   ├── Smart_Forecast.sql                 # Predictive analytics with seasonal trends
│   ├── High_Demand_zone.sql               # Geographic segmentation & risk analysis
│   ├── Product_Lifecycle_Classification.sql  # Product trend analysis via regression
│   ├── PRODUCT_DEMAND_TRENDS.sql          # Monthly demand line data
│   ├── Price_vs_Demand_Relationship.sql    # Price elasticity modeling
│   ├── Profit_Impact_Analysis.sql         # Discount simulation & break-even
│   └── Sell Near Me.lvdash.json          # Complete Databricks dashboard config
|
├── data set/
|   ├──Amazon_Flipkart_Returns_MIXED.xlsx
|   ├──Instant_Delivery_Sales_MIXED.xlsx
|
├── separate code/              # Original Analysis Scripts
│   ├── near1.py to near12.py      # Individual ML experiments
│   └── README files               # Analysis documentation
│
├── 📄 app.py                      # 🚀 Main Application Entry Point
├── 📄 ingestion.py                # 📤 Data Upload & Processing
├── 📄 dashboard.py                # 📊 Main Dashboard Overview
├── 📄 manual.py                   # 🔍 Manual Viability Checker
├── 📄 geospatial.py               # 🗺️ Demand Mapping
├── 📄 weather.py                  # 🌤️ Weather Impact Stats
├── 📄 weatherProduct.py           # 🌦️ Category Performance
├── 📄 demand.py                   # 🔗 Demand Matching
├── 📄 ChannelAn.py                # 📈 Channel Analytics
├── 📄 smartForecast.py            # 🔮 Weather-aware Forecasting
├── 📄 segmentation.py             # 🗂️ Customer Clustering
├── 📄 productLifecycle.py         # 📊 Product Maturity Analysis
├── 📄 priceSensitivity.py         # 💰 Price Elasticity Simulator
├── 📄 generateLabel.py            # 🏷️ Label Generation Utility
│
├── 📄 requirements.txt            # 📦 Python Dependencies
├── 📄 .env                        # 🔐 Environment Variables
├── 📄 .gitignore                  # 🚫 Git Ignore Rules
└── 📄 README.MD                   # 📖 This Documentation
```

### 🧠 System Architecture & Methodology

| Component | Method / Algorithm | Purpose | Key Output |
| :--- | :--- | :--- | :--- |
| **🌤️ Weather Processor** | `LabelEncoder` | Convert categorical weather data to numerical format | Encoded numerical values |
| | `LogisticRegression` | Predict sell probability based on weather & sales patterns | Sell probability (0-100%) |
| | `train_test_split` | Split data to prevent overfitting | Validation datasets |
| | `Haversine Distance` | Calculate geographic distance (Return vs. Sales) | Distance (km) |
| | `Pandas Aggregation` | Group data by weather and category | Weather impact tables |
| **📢 Channel Processor** | `Pandas Aggregation` | Group sales by platform | Revenue & market share stats |
| | `Math Utils` | Calculate commissions, return rates, delivery speeds | Performance metrics table |
| | `Trend Analysis` | Track revenue changes over time | Time-series data |
| **📉 Demand Processor** | `KNN (K-Nearest Neighbors)` | Find similar sales near return locations | Demand matching neighbors |
| | `Haversine Distance` | Calculate proximity for similarity scoring | Distance measurements |
| | `Business Logic` | Apply thresholds based on volume/distance | Resale Viability (High/Med/Low) |
| **🗺️ Geospatial Processor** | `Haversine Distance` | Measure distance between return & sales points | Proximity analysis |
| | `Weighted Scoring` | Combine distance, demand, and platform factors | Confidence Score (0-100%) |
| | `Threshold Logic` | Apply rules for final decision | Recommendations (YES/NO/MAYBE) |
| **🖐️ Manual Viability** | `LabelEncoder` | Pre-processing for ML models | Encoded feature values |
| | `LogisticRegression` | Predict base sell probability | Base probability score |
| | `KNeighborsClassifier` | Recommend best platform via similarity | Platform recommendation |
| | `GradientBoostingRegressor` | Predict optimal market price | Predicted Market Price |
| **💰 Price Sensitivity** | `LinearRegression` | Model basic price elasticity | Demand prediction (Linear) |
| | `GradientBoostingRegressor` | Capture non-linear price patterns | Demand prediction (Complex) |
| | `Discount Simulation` | Test impact of 0-50% discounts | Revenue/Profit impact analysis |
| | `Break-even Analysis` | Find profitability thresholds | Break-even discount % |
| **🔄 Lifecycle Processor** | `LinearRegression` | Analyze demand slope over time | Trend (Growing/Stable/Declining) |
| | `Slope Classification` | Determine lifecycle stage via regression slope | Stage: New / Mature / Declining |
| **🧩 Segmentation** | `KMeans Clustering` | Group cities by sales/return patterns | City Clusters |
| | `Risk Calculation` | Assess return risk percentages | Risk Level (Critical to Low) |
| **🔮 Smart Forecast** | `Prophet` | Time series prediction with seasonality | 30-Day Demand Forecast |
| | `NearestNeighbors` | Find similar products | Product similarity matching |
| | `Weather API` | Real-time weather integration | Current condition impact |

### 🎨 **Architecture Overview:**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Upload   │───▶│  Data Processing │───▶│   ML Analysis   │
│   CSV/XLS Files │    │  Cleaning & Prep │    │   Predictions   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Streamlit UI    │◀───│ Session Storage  │◀───│   Analytics     │
│ Interactive     │    │   State Mgmt    │    │   Results       │
│ Dashboard       │    └──────────────────┘    └─────────────────┘
└─────────────────┘
```

---

## 🚀 How to Run

### 🎯 **Quick Start (3 Commands)**

```bash
# 1. Clone and navigate
git clone <repository-url>
cd sell-best-ai-inventory

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
streamlit run app.py
```

### 📊 **Detailed Running Instructions**

#### **Method 1: Direct Run**
```bash
streamlit run app.py
```

#### **Method 2: Python Module**
```bash
python -m streamlit run app.py
```

#### **Method 3: With Custom Port**
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### 🌐 **Access the Application**
Once running, open your browser to: `http://localhost:8501`

### 🔧 **Troubleshooting**

**If you get import errors:**
```bash
pip install --upgrade streamlit pandas scikit-learn plotly
```

**If weather API fails:**
- Add your OpenWeather API key to `.env` file
- Or the app will use fallback weather data

**For large datasets:**
```bash
# Increase Streamlit memory limit
streamlit run app.py --server.maxUploadSize 1024
```

---

## 🔧 Key Dependencies

### 📦 **Core Dependencies**
```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
plotly>=5.15.0
folium>=0.14.0
prophet>=1.1.0
requests>=2.31.0
python-dotenv>=1.0.0
openpyxl>=3.1.0
xlrd>=2.0.1
```

---
