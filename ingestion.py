import streamlit as st

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
            st.file_uploader("Upload Returns", label_visibility="collapsed", key="u1")

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
            st.file_uploader("Upload Sales", label_visibility="collapsed", key="u2")


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
            st.toast("Pipeline Started!")

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
