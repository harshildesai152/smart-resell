import streamlit as st
import plotly.graph_objects as go

def show():
    # Check if data has been processed
    if not st.session_state.get('forecast_processed', False):
        st.warning("⚠️ Please upload both returns and sales data first using the 'Ingest Data' page to see smart forecast analysis.")
        st.info("Go to 'Ingest Data' → Upload your returns and sales data → Click 'Run Preprocessing & Predict'")
        return

    forecast_data = st.session_state.get('forecast_data', {})
    # Header
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("Smart Forecast & Opportunity")
    with col2:
        st.success("● AI Active")

    # Styling for tables
    st.markdown("""
    <style>
        .sf-card {
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .sf-title {
            color: #c9d1d9;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 5px;
            display: flex;
            align-items: center;
        }
        .sf-subtitle {
             color: #8b949e;
             font-size: 12px;
             margin-bottom: 15px;
        }
        .sf-table-header {
            display: grid;
            grid-template-columns: 2fr 1.5fr 1.5fr 2fr;
            padding: 10px 0;
            border-bottom: 1px solid #30363d;
            color: #8b949e;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .sf-table-row {
            display: grid;
            grid-template-columns: 2fr 1.5fr 1.5fr 2fr;
            padding: 15px 0;
            border-bottom: 1px solid #21262d;
            align-items: center;
            transition: background-color 0.2s;
        }
        .sf-table-row:hover {
            background-color: #161b22;
        }
        .sf-cell-main {
            color: #e6edf3;
            font-size: 14px;
            font-weight: 500;
        }
        .sf-cell-sub {
            color: #8b949e;
            font-size: 13px;
        }
        .sf-tag-high {
            background-color: rgba(35, 134, 54, 0.2);
            color: #3fb950;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            width: fit-content;
        }
        .sf-tag-med {
            background-color: rgba(210, 153, 34, 0.2);
            color: #d29922;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            width: fit-content;
        }
        .sf-metric-up {
            color: #3fb950;
            font-weight: 600;
            font-size: 13px;
        }
         .sf-metric-neutral {
            color: #8b949e;
            font-weight: 600;
            font-size: 13px;
        }
        .weather-badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 10px;
        }
        .weather-rain { background: rgba(88, 166, 255, 0.15); color: #58a6ff; border: 1px solid rgba(88, 166, 255, 0.3); }
        .weather-sun { background: rgba(210, 153, 34, 0.15); color: #d29922; border: 1px solid rgba(210, 153, 34, 0.3); }
    </style>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------
    # SECTION 1: RIGHT NOW (Current Weather)
    # -----------------------------------------------------
    current_weather = forecast_data.get('current_weather', {})
    weather_condition = current_weather.get('condition', 'Sunny')
    temperature = current_weather.get('temperature', '25°C')

    # Map weather conditions to emojis and CSS classes
    weather_mapping = {
        'Rainy': ('🌧️', 'weather-rain'),
        'Sunny': ('☀️', 'weather-sun'),
        'Cloudy': ('☁️', 'weather-rain'),
        'Windy': ('💨', 'weather-sun'),
        'Winter': ('❄️', 'weather-sun')
    }

    weather_emoji, weather_class = weather_mapping.get(weather_condition, ('☀️', 'weather-sun'))

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown(f"""
        <div class="sf-title">
            Live Opportunity: Current Weather Impact
            <span class="weather-badge {weather_class}">{weather_emoji} {weather_condition} • {temperature}</span>
        </div>
        <div class="sf-subtitle">Products with high sales velocity <b>right now</b> due to active weather conditions.</div>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div class="sf-table-header">
            <div>Product Name</div>
            <div>Category</div>
            <div>Current Velocity</div>
            <div>Stock Status</div>
        </div>
    """, unsafe_allow_html=True)

    # Get real live opportunity data
    live_opportunity = forecast_data.get('live_opportunity', [])

    if live_opportunity:
        for row in live_opportunity:
            product_name = row.get('product_name', 'Unknown Product')
            category = row.get('category', 'Unknown')
            velocity = row.get('current_velocity_display', '+0% vs avg')
            stock_status = row.get('stock_status', 'Medium')

            # Map stock status to CSS classes
            status_class = {
                'High': 'sf-tag-high',
                'Medium': 'sf-tag-med',
                'Low': 'sf-tag-med'  # Using med for low as well since we only have 2 classes
            }.get(stock_status, 'sf-tag-med')

            st.markdown(f"""
            <div class="sf-table-row">
                <div class="sf-cell-main">{product_name}</div>
                <div class="sf-cell-sub">{category}</div>
                <div class="sf-metric-up">⚡ {velocity}</div>
                <div><span class="{status_class}">{stock_status}</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Fallback data if no processed data available
        fallback_rows = [
            {"name": "StormBreaker Umbrella", "cat": "Accessories", "vel": "+145% vs avg", "stock": "High", "status": "sf-tag-high"},
            {"name": "Waterproof Trench Coat", "cat": "Apparel", "vel": "+85% vs avg", "stock": "Medium", "status": "sf-tag-med"},
            {"name": "Rubber Rain Boots", "cat": "Footwear", "vel": "+112% vs avg", "stock": "Low", "status": "sf-tag-med"},
            {"name": "Anti-Frizz Hair Serum", "cat": "Beauty", "vel": "+40% vs avg", "stock": "High", "status": "sf-tag-high"},
        ]

        for row in fallback_rows:
            st.markdown(f"""
            <div class="sf-table-row">
                <div class="sf-cell-main">{row['name']}</div>
                <div class="sf-cell-sub">{row['cat']}</div>
                <div class="sf-metric-up">⚡ {row['vel']}</div>
                <div><span class="{row['status']}">{row['stock']}</span></div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


    # -----------------------------------------------------
    # SECTION 2: FUTURE LOOK (Next Month)
    # -----------------------------------------------------
    next_month_weather = forecast_data.get('next_month_weather', {})
    next_weather_condition = next_month_weather.get('condition', 'Sunny')
    next_temperature = next_month_weather.get('temperature', '32°C')

    # Map weather conditions to emojis and CSS classes for next month
    weather_emoji, weather_class = weather_mapping.get(next_weather_condition, ('☀️', 'weather-sun'))

    st.markdown('<div class="sf-card">', unsafe_allow_html=True)
    st.markdown(f"""
        <div class="sf-title">
            Future Signal: Next Month Forecast
            <span class="weather-badge {weather_class}">{weather_emoji} {next_weather_condition} • {next_temperature} (Avg)</span>
        </div>
        <div class="sf-subtitle">Products predicted to spike <b>next month</b> based on long-range weather models.</div>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
        <div class="sf-table-header">
            <div>Predicted Winner</div>
            <div>Category</div>
            <div>Forecasted Demand</div>
            <div>Recommended Action</div>
        </div>
    """, unsafe_allow_html=True)

    # Get real future forecast data
    future_forecast = forecast_data.get('future_forecast', [])

    if future_forecast:
        for row in future_forecast:
            product_name = row.get('product_name', 'Unknown Product')
            category = row.get('category', 'Unknown')
            demand = row.get('forecasted_demand_label', 'Low')
            action = row.get('recommended_action', 'Monitor')

            # Map actions to CSS classes
            action_class = {
                'Increase Order': 'sf-tag-high',
                'Stock Up Now': 'sf-tag-high',
                'Monitor': 'sf-tag-med',
                'Avoid': 'sf-tag-med'
            }.get(action, 'sf-tag-med')

            st.markdown(f"""
            <div class="sf-table-row">
                <div class="sf-cell-main">{product_name}</div>
                <div class="sf-cell-sub">{category}</div>
                <div class="sf-metric-up">📈 {demand}</div>
                <div><span class="{action_class}">{action}</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Fallback data if no processed data available
        fallback_rows = [
            {"name": "SPF 50+ Sunscreen", "cat": "Beauty", "dem": "High (+200%)", "action": "Stock Up Now", "status": "sf-tag-high"},
            {"name": "Cooling Mist Spray", "cat": "Personal Care", "dem": "Very High", "action": "Increase Order", "status": "sf-tag-high"},
            {"name": "Portable Neck Fan", "cat": "Electronics", "dem": "Moderate", "action": "Monitor", "status": "sf-tag-med"},
            {"name": "UV Protection Sunglasses", "cat": "Accessories", "dem": "High", "action": "Stock Up Now", "status": "sf-tag-high"},
        ]

        for row in fallback_rows:
            st.markdown(f"""
            <div class="sf-table-row">
                <div class="sf-cell-main">{row['name']}</div>
                <div class="sf-cell-sub">{row['cat']}</div>
                <div class="sf-metric-up">📈 {row['dem']}</div>
                <div><span class="{row['status']}">{row['action']}</span></div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
