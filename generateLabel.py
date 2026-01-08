import streamlit as st

def show(title="Items at Delhi, Delhi", subtitle="9 records found", mode="returns"):
    # Styles for this sidebar
    st.markdown("""
    <style>
        .drawer-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #30363d;
        }
        .header-title {
            font-size: 20px;
            font-weight: bold;
            color: white;
            margin: 0;
        }
        .header-subtitle {
            font-size: 13px;
            color: #8b949e;
            margin-top: 5px;
        }
        
        .item-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 3px solid #30363d; 
            transition: transform 0.2s;
        }
        .item-card:hover { border-color: #8b949e; }
        
        /* Mode specific active borders */
        .card-active-returns { border-left: 3px solid #7C4DFF; background-color: rgba(124, 77, 255, 0.03); }
        .card-active-sales { border-left: 3px solid #00E676; background-color: rgba(0, 230, 118, 0.03); }
        
        .item-top-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .item-name { font-size: 14px; font-weight: bold; color: #e6edf3; }
        
        .badge {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-return { background-color: rgba(248, 81, 73, 0.1); color: #f85149; border: 1px solid rgba(248, 81, 73, 0.4); }
        .badge-sale { background-color: rgba(46, 160, 67, 0.1); color: #3fb950; border: 1px solid rgba(46, 160, 67, 0.4); }
        
        .item-category { font-size: 11px; color: #8b949e; margin-bottom: 8px; }
        .item-details { font-size: 12px; color: #c9d1d9; line-height: 1.6; margin-bottom: 12px; }
        .detail-icon { color: #8b949e; margin-right: 6px; }
        
        .tags-row { display: flex; gap: 8px; }
        .tag-pill { display: inline-block; background-color: #21262d; border: 1px solid #30363d; padding: 2px 8px; border-radius: 4px; font-size: 11px; color: #c9d1d9; }
        .tag-orange { color: #fb8c00; border-color: rgba(251, 140, 0, 0.4); background: rgba(251, 140, 0, 0.1); }
        .tag-green { color: #00E676; border-color: rgba(0, 230, 118, 0.4); background: rgba(0, 230, 118, 0.1); }
        
        div.stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #7C4DFF 0%, #651FFF 100%);
            border: none;
            color: white;
            font-weight: 600;
            padding: 10px;
            transition: all 0.3s;
        }
        div.stButton > button[kind="primary"]:hover {
            box-shadow: 0 4px 12px rgba(124, 77, 255, 0.3);
            transform: translateY(-1px);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header Area
    h_col1, h_col2 = st.columns([7, 1])
    with h_col1:
        st.markdown(f"""
        <div>
            <div class="header-title">{title}</div>
            <div class="header-subtitle">{subtitle}</div>
        </div>
        """, unsafe_allow_html=True)
    with h_col2:
        if st.button("✕", key="close_label_drawer"):
            st.session_state.detail_drawer_open = False
            st.rerun()

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    if mode == "returns":
        cards_html = """
        <div class="item-card card-active-returns">
            <div class="item-top-row"><span class="item-name">Product 1 - Fashion</span><span class="badge badge-return">RETURN</span></div>
            <div class="item-category">Beauty</div>
            <div class="item-details">
                <div><span class="detail-icon">📅</span> 2025-12-03 &nbsp; <span class="detail-icon">📍</span> Delhi, Delhi</div>
                <div style="margin-top:4px;"><span class="detail-icon">⚠️</span> Did not fit</div>
            </div>
            <div class="tags-row"><span class="tag-pill tag-orange">Open Box</span><span class="tag-pill">Myntra</span></div>
        </div>
        <div class="item-card">
            <div class="item-top-row"><span class="item-name">Product 7 - Fashion</span><span class="badge badge-return">RETURN</span></div>
            <div class="item-category">Home</div>
            <div class="item-details">
                <div><span class="detail-icon">📅</span> 2025-12-16 &nbsp; <span class="detail-icon">📍</span> Delhi, Delhi</div>
                <div style="margin-top:4px;"><span class="detail-icon">⚠️</span> Wrong Item sent</div>
            </div>
            <div class="tags-row"><span class="tag-pill tag-green">New</span><span class="tag-pill">Ajio</span></div>
        </div>
        <div class="item-card">
            <div class="item-top-row"><span class="item-name">Product 15 - Fashion</span><span class="badge badge-return">RETURN</span></div>
            <div class="item-category">Beauty</div>
            <div class="item-details">
                <div><span class="detail-icon">📅</span> 2025-12-04 &nbsp; <span class="detail-icon">📍</span> Delhi, Delhi</div>
                <div style="margin-top:4px;"><span class="detail-icon">⚠️</span> Defective</div>
            </div>
            <div class="tags-row"><span class="tag-pill tag-green">Refurbished</span></div>
        </div>
        """
    else: # Sales Mode
        cards_html = """
        <div class="item-card card-active-sales">
            <div class="item-top-row"><span class="item-name">SKU-10120</span><span class="badge badge-sale">SALE</span></div>
            <div class="item-category">Fashion</div>
            <div class="item-details">
                <div><span class="detail-icon">📍</span> Mumbai, Maharashtra &nbsp; <span class="detail-icon">📅</span> 2025-10-10</div>
                <div style="margin-top:4px;"><span class="detail-icon">🛒</span> Swiggy Instamart &nbsp; • &nbsp; Qty: 2</div>
                <div style="margin-top:4px;"><span class="detail-icon">☁️</span> Weather: Sunny</div>
            </div>
        </div>
        <div class="item-card">
            <div class="item-top-row"><span class="item-name">SKU-10825</span><span class="badge badge-sale">SALE</span></div>
            <div class="item-category">Beauty</div>
            <div class="item-details">
                <div><span class="detail-icon">📍</span> Hyderabad, Telangana &nbsp; <span class="detail-icon">📅</span> 2025-11-27</div>
                <div style="margin-top:4px;"><span class="detail-icon">🛒</span> Zepto &nbsp; • &nbsp; Qty: 2</div>
                <div style="margin-top:4px;"><span class="detail-icon">☁️</span> Weather: Sunny</div>
            </div>
        </div>
        <div class="item-card">
            <div class="item-top-row"><span class="item-name">SKU-10788</span><span class="badge badge-sale">SALE</span></div>
            <div class="item-category">Electronics</div>
            <div class="item-details">
                <div><span class="detail-icon">📍</span> Hyderabad, Telangana &nbsp; <span class="detail-icon">📅</span> 2025-12-12</div>
                <div style="margin-top:4px;"><span class="detail-icon">🛒</span> Swiggy Instamart &nbsp; • &nbsp; Qty: 3</div>
                <div style="margin-top:4px;"><span class="detail-icon">☁️</span> Weather: Sunny</div>
            </div>
        </div>
        <div class="item-card">
            <div class="item-top-row"><span class="item-name">SKU-10734</span><span class="badge badge-sale">SALE</span></div>
            <div class="item-category">Fashion</div>
            <div class="item-details">
                <div><span class="detail-icon">📍</span> Delhi, Delhi &nbsp; <span class="detail-icon">📅</span> 2025-12-05</div>
                <div style="margin-top:4px;"><span class="detail-icon">🛒</span> BB Now &nbsp; • &nbsp; Qty: 1</div>
                <div style="margin-top:4px;"><span class="detail-icon">☁️</span> Weather: Sunny</div>
            </div>
        </div>
        """

    st.markdown(cards_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("📥 Download List", key="dl_list", type="primary", use_container_width=True)
