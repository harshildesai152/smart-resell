import streamlit as st

def show():
    # Check if data has been processed and viability models trained
    if not st.session_state.get('viability_trained', False):
        st.warning("⚠️ Please upload sales data first using the 'Ingest Data' page to train the viability models.")
        st.info("Go to 'Ingest Data' → Upload your sales data → Click 'Run Preprocessing & Predict'")
        return
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
            
            product_name = st.text_input("Product Name / Description", value="I phone", key="product_name_input")

            row1_1, row1_2 = st.columns(2)
            with row1_1:
                category = st.selectbox("Category", ["Electronics", "Fashion", "Home", "Smart Phone"], index=0, key="category_input")
            with row1_2:
                condition = st.selectbox("Condition", ["New", "Used - Good", "Refurbished"], index=0, key="condition_input")

            row2_1, row2_2, row2_3 = st.columns(3)
            with row2_1:
                original_price = st.number_input("Original Price (₹)", value=25000, key="price_input")
            with row2_2:
                source_platform = st.selectbox("Source Platform", ["Amazon", "Flipkart", "Myntra"], index=0, key="source_input")
            with row2_3:
                weather = st.selectbox("Weather", ["Winter", "Summer", "Rainy", "Cloudy"], index=0, key="weather_input")

            city = st.selectbox("Your Location (City)", ["Ahmedabad", "Bangalore", "Delhi", "Mumbai"], index=0, key="city_input")
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
                # Get the trained processor
                viability_processor = st.session_state.get('manual_viability_processor')
                if viability_processor:
                    # Collect input data
                    product_details = {
                        "product_name": st.session_state.get("product_name_input", "Unknown Product"),
                        "category": st.session_state.get("category_input", ""),
                        "original_price": st.session_state.get("price_input", 1000),
                        "weather": st.session_state.get("weather_input", ""),
                        "city": st.session_state.get("city_input", ""),
                        "condition": st.session_state.get("condition_input", ""),
                        "source_platform": st.session_state.get("source_input", "")
                    }

                    # Analyze the product
                    result = viability_processor.analyze_product(product_details)

                    if "error" in result:
                        st.error(f"Analysis failed: {result['error']}")
                    else:
                        # Store result for display in the right panel
                        st.session_state.viability_result = result
                        st.toast("Analysis Complete!")
                        st.rerun()
                else:
                    st.error("Viability processor not available. Please re-upload your sales data.")

    # RIGHT COLUMN: Results Card
    with c2:
        # Get analysis result from session state
        result = st.session_state.get('viability_result', {})

        if result:
            # Determine badge based on sell probability
            sell_prob_value = float(result['sell_probability'].rstrip('%'))
            if sell_prob_value >= 70:
                badge_text = "High Demand"
                badge_color = "#3fb950"
                badge_bg = "rgba(46, 160, 67, 0.15)"
                badge_border = "rgba(46, 160, 67, 0.4)"
            elif sell_prob_value >= 40:
                badge_text = "Medium Demand"
                badge_color = "#d29922"
                badge_bg = "rgba(210, 153, 34, 0.15)"
                badge_border = "rgba(210, 153, 34, 0.4)"
            else:
                badge_text = "Low Demand"
                badge_color = "#f85149"
                badge_bg = "rgba(248, 81, 73, 0.15)"
                badge_border = "rgba(248, 81, 73, 0.4)"

            card_html = f"""
<style>
.result-card {{ background-color: #161b22; border: 1px solid #30363d; border-radius: 15px; padding: 25px; }}
.card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }}
.product-title {{ font-size: 24px; font-weight: bold; margin: 0; color: white; }}
.product-sub {{ color: #8b949e; font-size: 14px; margin-top: 5px; }}
.badge {{ background-color: {badge_bg}; color: {badge_color}; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; border: 1px solid {badge_border}; }}
.metrics-row {{ display: flex; gap: 15px; margin-bottom: 25px; }}
.metric-box {{ flex: 1; background-color: #0d1117; border-radius: 8px; padding: 20px; text-align: center; border: 1px solid #21262d; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }}
.metric-label {{ color: #8b949e; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-weight: 600; }}
.metric-value-green {{ color: #00E676; font-size: 32px; font-weight: 700; }}
.metric-value-purple {{ color: #b388ff; font-size: 32px; font-weight: 700; }}
.strategy-section {{ border-top: 1px solid #30363d; padding-top: 25px; }}
.rec-box {{ background-color: #1f242d; border: 1px solid #30363d; border-radius: 10px; padding: 15px; display: flex; gap: 15px; align-items: center; margin-bottom: 20px; }}
.icon-box {{ width: 48px; height: 48px; background-color: #2e245a; display: flex; align-items: center; justify-content: center; border-radius: 10px; font-size: 24px; }}
.check-list {{ list-style: none; padding: 0; color: #8b949e; font-size: 14px; }}
.check-list li {{ margin-bottom: 12px; display: flex; align-items: flex-start; gap: 12px; line-height: 1.5; }}
.check-list li:last-child {{ margin-bottom: 0; }}
.green-tick {{ color: #00E676; font-weight: bold; margin-top: 1px; }}
</style>
<div class="result-card">
<div class="card-header">
<div>
<h2 class="product-title">{result['product_name']}</h2>
<div class="product-sub">{st.session_state.get('city_input', 'Unknown City')} • {st.session_state.get('condition_input', 'Unknown')}</div>
</div>
<div class="badge">{badge_text}</div>
</div>
<div class="metrics-row">
<div class="metric-box">
<div class="metric-label">SELL PROBABILITY</div>
<div class="metric-value-green">{result['sell_probability']}</div>
</div>
<div class="metric-box">
<div class="metric-label">EST. PROFIT</div>
<div class="metric-value-purple">{result['est_profit']}</div>
</div>
</div>
<div class="strategy-section">
<h4 style="margin-top:0; margin-bottom:15px; color: white; font-size: 16px;">Analysis Results</h4>
<div style="background-color: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px;">
        <div><span style="color: #8b949e;">Recommended App:</span> <span style="color: white; font-weight: bold;">{result['recommended_app']}</span></div>
        <div><span style="color: #8b949e;">Weather Impact:</span> <span style="color: white;">{result['weather_impact']}</span></div>
        <div><span style="color: #8b949e;">Market Price:</span> <span style="color: white;">{result['predicted_market_price']}</span></div>
        <div><span style="color: #8b949e;">Price OK:</span> <span style="color: white;">{result['price_acceptable']}</span></div>
    </div>
</div>
<div class="rec-box">
<div class="icon-box">📱</div>
<div>
<div style="font-weight:bold; color:white; font-size: 16px;">{result['recommended_app']}</div>
<div style="font-size:13px; color:#8b949e;">Best performing platform for this product category.</div>
</div>
</div>
<ul class="check-list">
<li><span class="green-tick">✓</span> Analysis completed using historical sales data.</li>
<li><span class="green-tick">✓</span> ML models trained on uploaded dataset.</li>
<li><span class="green-tick">✓</span> Results based on real market patterns.</li>
</ul>
</div>
</div>
"""
            st.markdown(card_html, unsafe_allow_html=True)
        else:
            # Show placeholder when no analysis has been run
            st.markdown("""
            <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 15px; padding: 25px; text-align: center;">
                <div style="color: #8b949e; font-size: 16px;">Enter product details and click "Analyze Viability" to see results</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Action Buttons below the HTML card to keep them interactive Streamlit buttons
        st.markdown("")
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            st.button("Save to List", type="secondary", use_container_width=True)
        with b_col2:
            st.button("List Now", type="primary", use_container_width=True)
