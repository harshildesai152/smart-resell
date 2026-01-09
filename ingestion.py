import streamlit as st
import pandas as pd
import os
import sys

# Add analytics engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'analytics_engine'))
from geospatial_processor import GeospatialProcessor
from manual_viability_processor import ManualViabilityProcessor
from weather_processor import WeatherProcessor
from demand_processor import DemandProcessor
from channel_processor import ChannelProcessor
from smart_forecast_processor import SmartForecastProcessor
from segmentation_processor import SegmentationProcessor

def show():
    # Header
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("Data Ingestion Pipeline")
    with col2:
        st.success("● System Active")

    # Center Title
    st.markdown("""
        <div style="text-align: center; margin-bottom: 40px;">
            <h2 style="margin-bottom: 10px;">Data Ingestion Pipeline</h2>
            <p style="color: #8b949e; font-size: 16px;">Upload CSV files to retrain models and update the dashboard.</p>
        </div>
    """, unsafe_allow_html=True)

    # Custom CSS for Upload Cards and Button
    st.markdown("""
    <style>
        .upload-card-container {
            background-color: #0d1117;
            border-radius: 15px;
            padding: 40px 20px;
            text-align: center;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            border: 2px dashed #30363d; /* Default Grey Border (same as Historical Sales previously) */
            transition: all 0.3s ease;
        }
        
        .upload-card-container:hover {
            border: 2px dashed #2979FF; /* Blue border on hover */
            background-color: rgba(41, 121, 255, 0.05); /* Slight blue tint */
        }
        
        .icon-large {
            font-size: 40px;
            margin-bottom: 15px;
            color: #8b949e;
        }
        .card-title {
            font-size: 18px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        }
        .card-sub {
            font-size: 14px;
            color: #8b949e;
            margin-bottom: 20px;
            max-width: 80%;
            margin-left: auto;
            margin-right: auto;
        }
        
        .big-button {
            width: 100%;
            display: flex;
            justify-content: center;
            margin-top: 30px;
        }
        
        /* Info Footer */
        .info-box {
            background-color: rgba(13, 17, 23, 0.5); 
            border: 1px solid #1f2937;
            border-left: 4px solid #3b82f6; /* Blue accent */
            border-radius: 8px;
            padding: 20px;
            margin-top: 40px;
            color: #8b949e;
            font-size: 14px;
        }
        .info-title {
            color: #3b82f6; 
            font-weight: bold; 
            margin-bottom: 5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Main Upload Area - 2 Columns
    c1, c2 = st.columns(2, gap="large")
    
    with c1:
        with st.container():
            # Returns Inventory Card
            st.markdown("""
            <div class="upload-card-container">
                <div class="icon-large">☁️</div>
                <div class="card-title">Returns Inventory</div>
                <div class="card-sub">Drag & drop your CSV file here, or click to browse files</div>
            </div>
            """, unsafe_allow_html=True)
            returns_file = st.file_uploader("Upload Returns", label_visibility="collapsed", key="u1", type=["xlsx", "csv"])

    with c2:
        with st.container():
            # Historical Sales Card
            st.markdown("""
            <div class="upload-card-container">
                <div class="icon-large">☁️</div>
                <div class="card-title">Historical Sales</div>
                <div class="card-sub">Drag & drop your CSV file here, or click to browse files</div>
            </div>
            """, unsafe_allow_html=True)
            sales_file = st.file_uploader("Upload Sales", label_visibility="collapsed", key="u2", type=["xlsx", "csv"])


    # Centered 'Run' Button
    st.markdown("<br>", unsafe_allow_html=True)
    b_col1, b_col2, b_col3 = st.columns([1, 2, 1])
    with b_col2:
        # Custom css for this button to match the image (purple gradient, large)
        st.markdown("""
        <style>
        div.stButton > button {
            width: 100%;
            background: linear-gradient(90deg, #5e35b1 0%, #7C4DFF 100%);
            border: 1px solid #7C4DFF;
            padding-top: 15px;
            padding-bottom: 15px;
            font-size: 18px;
        }
        </style>
        """, unsafe_allow_html=True)
        if st.button("✨ Run Preprocessing & Predict"):
            if returns_file is None and sales_file is None:
                st.error("Please upload at least one file (Returns or Sales)")
                return

            # Initialize geospatial processor
            processor = GeospatialProcessor()

            # Save uploaded files temporarily
            returns_path = None
            sales_path = None

            if returns_file is not None:
                returns_path = os.path.join("temp_returns.xlsx")
                with open(returns_path, "wb") as f:
                    f.write(returns_file.getbuffer())

            if sales_file is not None:
                sales_path = os.path.join("temp_sales.xlsx")
                with open(sales_path, "wb") as f:
                    f.write(sales_file.getbuffer())

            # Process data
            if processor.load_and_process_data(returns_path, sales_path):
                # Store geospatial results in session state
                st.session_state.geospatial_data = processor.processed_data

                # Process weather analysis if both files are available
                if returns_path and sales_path:
                    weather_processor = WeatherProcessor()
                    if weather_processor.load_and_process_data(returns_path, sales_path):
                        st.session_state.weather_data = weather_processor.processed_data
                        st.session_state.weather_processed = True

                # Process demand matching if both files are available
                if returns_path and sales_path:
                    demand_processor = DemandProcessor()
                    if demand_processor.load_and_process_data(returns_path, sales_path):
                        st.session_state.demand_data = demand_processor.processed_data
                        st.session_state.demand_processed = True

                # Process channel analysis if both files are available
                if returns_path and sales_path:
                    channel_processor = ChannelProcessor()
                    if channel_processor.load_and_process_data(returns_path, sales_path):
                        st.session_state.channel_data = channel_processor.processed_data
                        st.session_state.channel_processed = True

                # Process smart forecast if both files are available
                if returns_path and sales_path:
                    forecast_processor = SmartForecastProcessor()
                    if forecast_processor.load_and_process_data(returns_path, sales_path):
                        st.session_state.forecast_data = forecast_processor.processed_data
                        st.session_state.forecast_processed = True

                # Process segmentation if both files are available
                if returns_path and sales_path:
                    segmentation_processor = SegmentationProcessor()
                    if segmentation_processor.load_and_process_data(returns_path, sales_path):
                        st.session_state.segmentation_data = segmentation_processor.processed_data
                        st.session_state.segmentation_processed = True

                # Train manual viability processor if sales data is available
                if sales_path:
                    viability_processor = ManualViabilityProcessor()
                    if viability_processor.load_and_train_models(pd.read_excel(sales_path) if sales_path.endswith('.xlsx') else pd.read_csv(sales_path)):
                        st.session_state.manual_viability_processor = viability_processor
                        st.session_state.viability_trained = True

                st.session_state.data_processed = True

                success_msg = "✅ Data processing complete! "
                features = []
                if True:  # geospatial always processed
                    features.append("Geospatial analysis")
                if sales_path and st.session_state.get('viability_trained', False):
                    features.append("manual viability check models")
                if returns_path and sales_path and st.session_state.get('weather_processed', False):
                    features.append("weather trends analysis")
                if returns_path and sales_path and st.session_state.get('demand_processed', False):
                    features.append("demand matching analysis")
                if returns_path and sales_path and st.session_state.get('channel_processed', False):
                    features.append("channel performance analysis")
                if returns_path and sales_path and st.session_state.get('forecast_processed', False):
                    features.append("smart forecast analysis")
                if returns_path and sales_path and st.session_state.get('segmentation_processed', False):
                    features.append("customer & location segmentation")

                if features:
                    success_msg += f"{' and '.join(features)} are now available."
                else:
                    success_msg += "Geospatial analysis results are now available in the Geospatial Demand Analysis page."

                st.success(success_msg)

                # Clean up temporary files
                if returns_path and os.path.exists(returns_path):
                    os.remove(returns_path)
                if sales_path and os.path.exists(sales_path):
                    os.remove(sales_path)

                st.toast("Pipeline Completed Successfully!")
            else:
                st.error("Failed to process data. Please check file formats and column names.")

    # Footer Info
    st.markdown("""
    <div class="info-box">
        <div class="info-title">
            <span>🔵</span> Supported Formats: CSV, XLSX, JSON
        </div>
        <div>
            Ensure your CSV contains required columns: <code>sku</code>, <code>city</code>, <code>return_reason</code>, <code>condition</code> for returns; and <code>sku</code>, <code>app</code>, <code>city</code>, <code>sale_date</code> for sales.
        </div>
    </div>
    """, unsafe_allow_html=True)
