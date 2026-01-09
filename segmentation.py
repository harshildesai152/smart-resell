import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import folium
from folium import plugins
from streamlit.components.v1 import html

def show():
    # Check if data has been processed
    if not st.session_state.get('segmentation_processed', False):
        st.warning("⚠️ Please upload both returns and sales data first using the 'Ingest Data' page to see customer & location segmentation.")
        st.info("Go to 'Ingest Data' → Upload your returns and sales data → Click 'Run Preprocessing & Predict'")
        return

    segmentation_data = st.session_state.get('segmentation_data', {})
    # Page Header
    st.title("Customer & Location Segmentation")
    st.markdown("*Cluster cities & identify high-risk zones*")
    st.markdown("---")

    # Get real KPI metrics
    kpi_metrics = segmentation_data.get('kpi_metrics', {})

    # KPI Metrics (4 columns)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    total_cities = kpi_metrics.get('total_cities', 0)
    high_demand_clusters = kpi_metrics.get('high_demand_clusters', 0)
    high_return_zones = kpi_metrics.get('high_return_zones', 0)
    expansion_opportunities = kpi_metrics.get('expansion_opportunities', 0)

    # Calculate percentages
    high_demand_pct = int((high_demand_clusters / total_cities * 100) if total_cities > 0 else 0)
    high_return_pct = int((high_return_zones / total_cities * 100) if total_cities > 0 else 0)
    expansion_pct = int((expansion_opportunities / total_cities * 100) if total_cities > 0 else 0)

    with kpi1:
        st.metric(
            label="Total Cities",
            value=str(total_cities),
            delta="+3 added this quarter"
        )

    with kpi2:
        st.metric(
            label="High-Demand Clusters",
            value=str(high_demand_clusters),
            delta=f"{high_demand_pct}% of total cities"
        )

    with kpi3:
        st.metric(
            label="High-Return Zones",
            value=str(high_return_zones),
            delta=f"{high_return_pct}% of total cities"
        )

    with kpi4:
        st.metric(
            label="Expansion Opportunities",
            value=str(expansion_opportunities),
            delta=f"{expansion_pct}% of total cities"
        )

    st.markdown("---")

    # City Cluster Map (Using Folium)
    st.subheader("City Cluster Map")

    # Get real city cluster map data
    city_cluster_map = segmentation_data.get('city_cluster_map', [])
    zone_colors = segmentation_data.get('zone_colors', {})

    if city_cluster_map:
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(city_cluster_map)

        # Map zone types to display names and colors
        zone_display_mapping = {
            "🟢 High Demand / Low Return": "High Demand / Low Return",
            "🔴 High Demand / High Return": "High Demand / High Return",
            "🟡 Low Demand / High Return": "Low Demand / High Return",
            "🟣 Stable Zone": "Stable Zones"
        }

        # Update zone_type for display and ensure colors
        df['cluster'] = df['zone_type'].map(zone_display_mapping)
        df['zone_color'] = df['zone_type'].map(zone_colors)

        cluster_colors = {
            "High Demand / Low Return": "#00E676",
            "High Demand / High Return": "#FF5252",
            "Low Demand / High Return": "#FFB74D",
            "Stable Zones": "#7C4DFF"
        }
    else:
        # Fallback to dummy data if no processed data available
        cities_data = [
            {"city": "Mumbai", "lat": 19.0760, "lon": 72.8777, "cluster": "High Demand / Low Return", "demand": 95, "returns": 12},
            {"city": "Delhi", "lat": 28.7041, "lon": 77.1025, "cluster": "High Demand / High Return", "demand": 88, "returns": 28},
            {"city": "Bangalore", "lat": 12.9716, "lon": 77.5946, "cluster": "High Demand / Low Return", "demand": 92, "returns": 15}
        ]
        df = pd.DataFrame(cities_data)
        cluster_colors = {
            "High Demand / Low Return": "#00E676",
            "High Demand / High Return": "#FF5252",
            "Low Demand / High Return": "#FFB74D",
            "Stable Zones": "#7C4DFF",
            "Expansion Opportunities": "#26A69A"
        }

    # Create Folium map centered on India
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles='CartoDB positron')

    # Add markers for each city
    for _, city in df.iterrows():
        # Calculate marker size based on total_sales (normalized)
        size = max(15, min(40, city['total_sales'] / 2))

        # Create popup content
        popup_content = f"""
        <div style="font-family: Arial, sans-serif; font-size: 14px;">
            <h4 style="margin: 0; color: {cluster_colors[city['cluster']]};">{city['city']}</h4>
            <p style="margin: 5px 0;"><strong>Cluster:</strong> {city['cluster']}</p>
            <p style="margin: 5px 0;"><strong>Demand Score:</strong> {int(city['total_sales'])}</p>
            <p style="margin: 5px 0;"><strong>Return Rate:</strong> {city['return_pct']:.1f}%</p>
        </div>
        """

        # Add circle marker
        folium.CircleMarker(
            location=[city['lat'], city['lon']],
            radius=size,
            color=cluster_colors[city['cluster']],
            fill=True,
            fill_color=cluster_colors[city['cluster']],
            fill_opacity=0.7,
            popup=folium.Popup(popup_content, max_width=250),
            tooltip=f"{city['city']} - {city['cluster']}"
        ).add_to(m)

    # Add layer control for different clusters (optional)
    # Since we have different clusters, we'll add a simple legend using HTML

    # Create legend HTML
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: rgba(0,0,0,0.8);
                padding: 10px; border-radius: 5px; color: white; font-size: 12px;">
        <p style="margin: 0; font-weight: bold;">City Clusters</p>
        <div style="display: flex; align-items: center; margin: 2px 0;">
            <div style="width: 12px; height: 12px; background-color: #00E676; border-radius: 50%; margin-right: 5px;"></div>
            High Demand / Low Return
        </div>
        <div style="display: flex; align-items: center; margin: 2px 0;">
            <div style="width: 12px; height: 12px; background-color: #FF5252; border-radius: 50%; margin-right: 5px;"></div>
            High Demand / High Return
        </div>
        <div style="display: flex; align-items: center; margin: 2px 0;">
            <div style="width: 12px; height: 12px; background-color: #FFB74D; border-radius: 50%; margin-right: 5px;"></div>
            Low Demand / High Return
        </div>
        <div style="display: flex; align-items: center; margin: 2px 0;">
            <div style="width: 12px; height: 12px; background-color: #7C4DFF; border-radius: 50%; margin-right: 5px;"></div>
            Stable Zones
        </div>
        <div style="display: flex; align-items: center; margin: 2px 0;">
            <div style="width: 12px; height: 12px; background-color: #26A69A; border-radius: 50%; margin-right: 5px;"></div>
            Expansion Opportunities
        </div>
    </div>
    '''

    m.get_root().html.add_child(folium.Element(legend_html))

    # Display the map in Streamlit
    html(m._repr_html_(), height=500)

    st.markdown("---")

    # Cluster Legend
    st.subheader("Cluster Legend")

    legend_col1, legend_col2, legend_col3, legend_col4 = st.columns(4)

    with legend_col1:
        st.markdown("### 🟢 High Demand / Low Return")
        st.markdown("*High sales, minimal returns*")
        st.markdown("*Best performing cities*")

    with legend_col2:
        st.markdown("### 🔴 High Demand / High Return")
        st.markdown("*Strong sales but quality issues*")
        st.markdown("*Focus on product quality*")

    with legend_col3:
        st.markdown("### 🟡 Low Demand / High Return")
        st.markdown("*Low sales, high return rate*")
        st.markdown("*Consider store closure*")

    with legend_col4:
        st.markdown("### 🟣 Stable Zones")
        st.markdown("*Moderate performance*")
        st.markdown("*Monitor closely*")

    st.markdown("---")

    # High-Risk Zones Table
    st.subheader("High-Risk Zones")

    # Get real high-risk zones data
    high_risk_zones = segmentation_data.get('high_risk_zones', [])

    if high_risk_zones:
        # Convert to DataFrame and rename columns for display
        risk_df = pd.DataFrame(high_risk_zones)
        risk_df = risk_df.rename(columns={
            'city': 'City',
            'risk_level': 'Risk Level',
            'return_pct': 'Return %',
            'demand': 'Demand'
        })

        # Display as table
        st.dataframe(
            risk_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        # Fallback to dummy data if no processed data available
        risk_data = [
            {"City": "Delhi", "Risk Level": "🔴 Critical", "Return %": "28%", "Demand": "High"},
            {"City": "Hyderabad", "Risk Level": "🔴 Critical", "Return %": "31%", "Demand": "High"},
            {"City": "Kolkata", "Risk Level": "🟡 High", "Return %": "35%", "Demand": "Low"}
        ]
        risk_df = pd.DataFrame(risk_data)
        st.dataframe(
            risk_df,
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")

    # Get top performing cities for insight
    if city_cluster_map:
        df_temp = pd.DataFrame(city_cluster_map)
        top_cities = df_temp[df_temp['zone_type'] == '🟢 High Demand / Low Return']['city'].head(2).tolist()
        if len(top_cities) >= 2:
            insight_text = f"**🎯 Key Insight:** {top_cities[0]} & {top_cities[1]} fall in High-Demand / Low-Return cluster. These cities show strong market potential with minimal operational challenges."
        elif len(top_cities) == 1:
            insight_text = f"**🎯 Key Insight:** {top_cities[0]} falls in High-Demand / Low-Return cluster. This city shows strong market potential with minimal operational challenges."
        else:
            insight_text = "**🎯 Key Insight:** Analyze city clusters to identify expansion opportunities and high-risk zones for operational improvements."
    else:
        insight_text = "**🎯 Key Insight:** Surat & Ahmedabad fall in High-Demand / Low-Return cluster. These cities show strong market potential with minimal operational challenges."

    st.success(insight_text)

    st.markdown("---")

    # Recommendation Section
    st.subheader("Strategic Recommendations")

    rec_col1, rec_col2 = st.columns(2)

    with rec_col1:
        st.markdown("### 📈 **Expansion Strategies**")
        st.markdown("• **Expand dark stores** in High-Demand / Low-Return clusters")
        st.markdown("• **Prioritize Ahmedabad & Surat** for new store openings")
        st.markdown("• **Increase SKU variety** in stable performing zones")

    with rec_col2:
        st.markdown("### 🔧 **Operational Improvements**")
        st.markdown("• **Improve delivery SLAs** in High-Return zones")
        st.markdown("• **Implement localized inventory planning** based on cluster patterns")
        st.markdown("• **Quality control focus** in Delhi & Hyderabad clusters")

    # Footer spacing
    st.markdown("")
    st.markdown("")