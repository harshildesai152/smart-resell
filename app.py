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
    
    st.caption("MAIN")
    # Using radio for list-like navigation as requested
    selected_page = st.radio("Navigation", ["Dashboard", "Manual Check", "Ingest Data"], index=0, label_visibility="collapsed")
    
    selected_module = "Overview" # Default
    
    if selected_page == "Dashboard":
        st.markdown(" ")
        st.caption("ANALYTICS MODULES")
        analytics_options = [
            "Overview", "Geo & Demand", "Weather Trends", "Weather x Product",
            "Demand Matching", "Channel Analysis", "Smart Forecast",
            "Customer & Location Segmentation", "Product Lifecycle Analysis", "Price Sensitivity & Discount Simulator"
        ]
        selected_module = st.radio("Modules", analytics_options, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("Device: **Active**")
    st.caption("Admin User")

# Routing Logic
if selected_page == "Dashboard":
    if selected_module == "Overview":
        dashboard.show()
    elif selected_module == "Geo & Demand":
        geospatial.show()
    elif selected_module == "Weather Trends":
        weather.show()
    elif selected_module == "Weather x Product":
        weatherProduct.show()
    elif selected_module == "Demand Matching":
        demand.show()
    elif selected_module == "Channel Analysis":
        ChannelAn.show()
    elif selected_module == "Smart Forecast":
        smartForecast.show()
   
    elif selected_module == "Customer & Location Segmentation":
        segmentation.show()
    elif selected_module == "Product Lifecycle Analysis":
        productLifecycle.show()
    elif selected_module == "Price Sensitivity & Discount Simulator":
        priceSensitivity.show()
    else:
        st.info("Module under development")
elif selected_page == "Manual Check":
    manual.show()
elif selected_page == "Ingest Data":
    ingestion.show()


