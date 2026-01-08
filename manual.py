import streamlit as st

def show():
    # Header
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("Viability Check")
    with col2:
        st.success("● System Active")

    st.markdown("### Manual Viability Check")
    st.markdown("Enter a single item's details to see if it will sell near your location.")
    
    st.markdown("---")

    # Main Layout: 2 Columns
    c1, c2 = st.columns([1, 1], gap="large")

    # LEFT COLUMN: Input Form
    with c1:
        # Container specifically for the form styling
        with st.container():
            st.markdown("""
            <div style="background-color: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d;">
                <h4 style="margin-top:0; color:white;">📦 Product Details</h4>
            </div>
            """, unsafe_allow_html=True) 
            
            # Use columns inside c1 for grid layout of inputs
            # To make it look integrated, we naturally place inputs below the header
            
            st.text_input("Product Name / Description", value="sony")
            
            row1_1, row1_2 = st.columns(2)
            with row1_1:
                st.selectbox("Category", ["Electronics", "Fashion", "Home"], index=0)
            with row1_2:
                st.selectbox("Condition", ["New", "Used - Good", "Refurbished"], index=0)
                
            row2_1, row2_2, row2_3 = st.columns(3)
            with row2_1:
                st.number_input("Original Price (₹)", value=1200)
            with row2_2:
                st.selectbox("Source Platform", ["Amazon", "Flipkart", "Myntra"], index=0)
            with row2_3:
                st.selectbox("wather", ["sunny", "rainy", "cloudy"], index=0)

            st.selectbox("Your Location (City)", ["Bangalore", "Delhi", "Mumbai"], index=0)
            st.caption("We will check demand within 10km of Bangalore center.")
            
            st.markdown(" ")
            
            # Custom styled button
            st.markdown("""
            <style>
            div.stButton > button:first-child {
                width: 100%;
                background: linear-gradient(90deg, #7C4DFF 0%, #536DFE 100%);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            div.stButton > button:hover {
                background: linear-gradient(90deg, #651FFF 0%, #3D5AFE 100%);
                color: white;
                border: none;
            }
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("Analyze Viability"):
                st.toast("Analyzing...")

    # RIGHT COLUMN: Results Card
    with c2:
        # We will build this card visually using HTML for the complicated parts
        # and standard Streamlit metrics if possible, or full custom HTML.
        # Given the layout (Badge, Metrics side-by-side, Strategy box), custom HTML with Fstrings is easiest for the 'Static' look of dashboard.
        
        card_html = """
<style>
.result-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 15px; padding: 25px; }
.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.product-title { font-size: 24px; font-weight: bold; margin: 0; color: white; }
.product-sub { color: #8b949e; font-size: 14px; margin-top: 5px; }
.badge { background-color: rgba(46, 160, 67, 0.15); color: #3fb950; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; border: 1px solid rgba(46, 160, 67, 0.4); }
.metrics-row { display: flex; gap: 15px; margin-bottom: 25px; }
.metric-box { flex: 1; background-color: #0d1117; border-radius: 8px; padding: 20px; text-align: center; border: 1px solid #21262d; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }
.metric-label { color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 600; }
.metric-value-green { color: #00E676; font-size: 32px; font-weight: 700; }
.metric-value-purple { color: #b388ff; font-size: 32px; font-weight: 700; }
.strategy-section { border-top: 1px solid #30363d; padding-top: 25px; }
.rec-box { background-color: #1f242d; border: 1px solid #30363d; border-radius: 10px; padding: 15px; display: flex; gap: 15px; align-items: center; margin-bottom: 20px; }
.icon-box { width: 48px; height: 48px; background-color: #2e245a; display: flex; align-items: center; justify-content: center; border-radius: 10px; font-size: 24px; }
.check-list { list-style: none; padding: 0; color: #8b949e; font-size: 14px; }
.check-list li { margin-bottom: 12px; display: flex; align-items: flex-start; gap: 12px; line-height: 1.5; }
.check-list li:last-child { margin-bottom: 0; }
.green-tick { color: #00E676; font-weight: bold; margin-top: 1px; }
</style>
<div class="result-card">
<div class="card-header">
<div>
<h2 class="product-title">sony</h2>
<div class="product-sub">Bangalore • New</div>
</div>
<div class="badge">High Demand</div>
</div>
<div class="metrics-row">
<div class="metric-box">
<div class="metric-label">SELL PROBABILITY</div>
<div class="metric-value-green">99%</div>
</div>
<div class="metric-box">
<div class="metric-label">EST. PROFIT</div>
<div class="metric-value-purple">₹1069</div>
</div>
</div>
<div class="strategy-section">
<h4 style="margin-top:0; margin-bottom:15px; color: white; font-size: 16px;">Recommended Strategy</h4>
<div class="rec-box">
<div class="icon-box">📱</div>
<div>
<div style="font-weight:bold; color:white; font-size: 16px;">Blinkit</div>
<div style="font-size:13px; color:#8b949e;">Best channel for Electronics in this area.</div>
</div>
</div>
<ul class="check-list">
<li><span class="green-tick">✓</span> High local demand detected.</li>
<li><span class="green-tick">✓</span> Proximity to fulfillment center reduces logistics cost.</li>
<li><span class="green-tick">✓</span> Item in pristine condition.</li>
</ul>
</div>
</div>
"""
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Action Buttons below the HTML card to keep them interactive Streamlit buttons
        st.markdown("")
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            st.button("Save to List", type="secondary", use_container_width=True)
        with b_col2:
            st.button("List Now", type="primary", use_container_width=True)
