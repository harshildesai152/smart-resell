import streamlit as st
import dashboard
import manual
import ingestion
import geospatial
import weather
import weatherProduct
import demand
import ChannelAn
import generateLabel
import smartForecast

import segmentation
import productLifecycle
import priceSensitivity

# Page Configuration
st.set_page_config(layout="wide", page_title="Sell Best - Inventory Intelligence", initial_sidebar_state="expanded")

# styling
st.markdown("""
<style>
    /* Global CSS adjustments */
    .stApp {
        background-color: #0d1117; /* Very dark blue/black */
    }
    
    /* Metrics styling */
    div[data-testid="metric-container"] {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
        color: white;
    }
    
    div[data-testid="metric-container"] > label {
        font-size: 12px;
        color: #8b949e;
    }
    
    div[data-testid="metric-container"] > div:nth-child(2) {
        font-size: 24px;
        font-weight: bold;
    }

    /* Remove padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Sidebar adjustments */
    section[data-testid="stSidebar"] {
        background-color: #010409;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⬢ Sell Best")
    st.markdown("AI Inventory Intelligence")
    st.markdown("---")

    # All navigation options in a single flat list
    all_options = [
        "Dashboard",
        "Manual Check",
        "Ingest Data",
        "Geo & Demand",
        "Weather Trends",
        "Weather x Product",
        "Demand Matching",
        "Channel Analysis",
        "Smart Forecast",
        "Customer & Location Segmentation",
        "Product Lifecycle Analysis",
        "Price Sensitivity & Discount Simulator"
    ]

    selected_option = st.radio("Navigation", all_options, index=0, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("Device: **Active**")
    st.caption("Admin User")

# Routing Logic
if selected_option == "Dashboard":
    dashboard.show()
elif selected_option == "Manual Check":
    manual.show()
elif selected_option == "Ingest Data":
    ingestion.show()
elif selected_option == "Geo & Demand":
    geospatial.show()
elif selected_option == "Weather Trends":
    weather.show()
elif selected_option == "Weather x Product":
    weatherProduct.show()
elif selected_option == "Demand Matching":
    demand.show()
elif selected_option == "Channel Analysis":
    ChannelAn.show()
elif selected_option == "Smart Forecast":
    smartForecast.show()
elif selected_option == "Customer & Location Segmentation":
    segmentation.show()
elif selected_option == "Product Lifecycle Analysis":
    productLifecycle.show()
elif selected_option == "Price Sensitivity & Discount Simulator":
    priceSensitivity.show()
else:
    st.info("Module under development")


