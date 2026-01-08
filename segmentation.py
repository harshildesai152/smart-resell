import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import folium
from folium import plugins
from streamlit.components.v1 import html

def show():
    # Page Header
    st.title("Customer & Location Segmentation")
    st.markdown("*Cluster cities & identify high-risk zones*")
    st.markdown("---")

    # KPI Metrics (4 columns)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.metric(
            label="Total Cities",
            value="28",
            delta="+3 added this quarter"
        )

    with kpi2:
        st.metric(
            label="High-Demand Clusters",
            value="8",
            delta="29% of total cities"
        )

    with kpi3:
        st.metric(
            label="High-Return Zones",
            value="6",
            delta="21% of total cities"
        )

    with kpi4:
        st.metric(
            label="Expansion Opportunities",
            value="12",
            delta="43% of total cities"
        )

    st.markdown("---")

    # City Cluster Map (Using Folium)
    st.subheader("City Cluster Map")

    # Create dummy city data with coordinates and clusters
    cities_data = [
        {"city": "Mumbai", "lat": 19.0760, "lon": 72.8777, "cluster": "High Demand / Low Return", "demand": 95, "returns": 12},
        {"city": "Delhi", "lat": 28.7041, "lon": 77.1025, "cluster": "High Demand / High Return", "demand": 88, "returns": 28},
        {"city": "Bangalore", "lat": 12.9716, "lon": 77.5946, "cluster": "High Demand / Low Return", "demand": 92, "returns": 15},
        {"city": "Chennai", "lat": 13.0827, "lon": 80.2707, "cluster": "Stable Zones", "demand": 75, "returns": 18},
        {"city": "Kolkata", "lat": 22.5726, "lon": 88.3639, "cluster": "Low Demand / High Return", "demand": 45, "returns": 35},
        {"city": "Pune", "lat": 18.5204, "lon": 73.8567, "cluster": "High Demand / Low Return", "demand": 85, "returns": 14},
        {"city": "Ahmedabad", "lat": 23.0225, "lon": 72.5714, "cluster": "High Demand / Low Return", "demand": 78, "returns": 11},
        {"city": "Jaipur", "lat": 26.9124, "lon": 75.7873, "cluster": "Stable Zones", "demand": 68, "returns": 22},
        {"city": "Surat", "lat": 21.1702, "lon": 72.8311, "cluster": "High Demand / Low Return", "demand": 82, "returns": 13},
        {"city": "Hyderabad", "lat": 17.3850, "lon": 78.4867, "cluster": "High Demand / High Return", "demand": 89, "returns": 31},
        {"city": "Lucknow", "lat": 26.8467, "lon": 80.9462, "cluster": "Expansion Opportunities", "demand": 55, "returns": 19},
        {"city": "Kanpur", "lat": 26.4499, "lon": 80.3319, "cluster": "Low Demand / High Return", "demand": 42, "returns": 38},
        {"city": "Nagpur", "lat": 21.1458, "lon": 79.0882, "cluster": "Stable Zones", "demand": 62, "returns": 24},
        {"city": "Indore", "lat": 22.7196, "lon": 75.8577, "cluster": "Expansion Opportunities", "demand": 58, "returns": 21},
        {"city": "Thane", "lat": 19.2183, "lon": 72.9781, "cluster": "High Demand / Low Return", "demand": 91, "returns": 16}
    ]

    # Convert to DataFrame
    df = pd.DataFrame(cities_data)

    # Define cluster colors
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
        # Calculate marker size based on demand (normalized)
        size = max(15, min(40, city['demand'] / 2))

        # Create popup content
        popup_content = f"""
        <div style="font-family: Arial, sans-serif; font-size: 14px;">
            <h4 style="margin: 0; color: {cluster_colors[city['cluster']]};">{city['city']}</h4>
            <p style="margin: 5px 0;"><strong>Cluster:</strong> {city['cluster']}</p>
            <p style="margin: 5px 0;"><strong>Demand Score:</strong> {city['demand']}</p>
            <p style="margin: 5px 0;"><strong>Return Rate:</strong> {city['returns']}%</p>
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

    # Create table data
    risk_data = [
        {"City": "Delhi", "Risk Level": "🔴 Critical", "Return %": "28%", "Demand": "High"},
        {"City": "Hyderabad", "Risk Level": "🔴 Critical", "Return %": "31%", "Demand": "High"},
        {"City": "Kolkata", "Risk Level": "🟡 High", "Return %": "35%", "Demand": "Low"},
        {"City": "Kanpur", "Risk Level": "🟡 High", "Return %": "38%", "Demand": "Low"},
        {"City": "Jaipur", "Risk Level": "🟠 Medium", "Return %": "22%", "Demand": "Medium"},
        {"City": "Nagpur", "Risk Level": "🟠 Medium", "Return %": "24%", "Demand": "Medium"}
    ]

    risk_df = pd.DataFrame(risk_data)

    # Display as table
    st.dataframe(
        risk_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # Business Insight Box
    st.success("**🎯 Key Insight:** Surat & Ahmedabad fall in High-Demand / Low-Return cluster. These cities show strong market potential with minimal operational challenges.")

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