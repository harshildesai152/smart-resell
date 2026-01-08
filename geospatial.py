import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import pandas as pd
import generateLabel

def show():
    # Header
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("Geospatial Demand Analysis")
    with col2:
        st.success("● System Active")

    # Initialize Drawer State
    if "detail_drawer_open" not in st.session_state:
        st.session_state.detail_drawer_open = False

    # Main Layout Logic (Global Split)
    if st.session_state.detail_drawer_open:
        # Split: Content (75%) | Sidebar (25%) -> Adjusted ratios for better look
        content_container, sidebar_container = st.columns([3, 1.2], gap="medium")
    else:
        content_container = st.container()
        sidebar_container = None

    # Render Content in the Left/Main Container
    with content_container:
        # Top Row (Map + Right Panel)
        # Note: We are nesting columns here which is allowed (1 level deep)
        # Ratio inside content container: Map (2) | Stats (1)
        r1_col1, r1_col2 = st.columns([2, 1], gap="medium")
    
        with r1_col1:
            # Map Section (Title + controls)
            # Header with Controls
            c_title, c_mode, c_filter = st.columns([2, 1.5, 2], gap="small")
            
            with c_title:
                 st.markdown('<h3 style="margin:0; padding-top: 10px;">Spatial Demand Clustering</h3>', unsafe_allow_html=True)
            
            with c_mode:
                mode = st.radio("Mode", ["Returns", "Sales"], horizontal=True, label_visibility="collapsed", key="geo_mode")
                
            with c_filter:
                if mode == "Sales":
                     weather = st.radio("Weather", ["ALL", "☀️", "🌧️", "☁️", "💨"], horizontal=True, label_visibility="collapsed", key="geo_weather")
                else:
                    st.write("") 
    
            # CSS for toggle (re-injected here to ensure it applies inside this container scope if needed, though global style works)
            st.markdown("""
            <style>
                div[data-testid="stRadio"] > div { display: flex; flex-direction: row; gap: 5px; background-color: transparent; }
                div[data-testid="stRadio"] label { background-color: #0d1117; border: 1px solid #30363d; padding: 5px 15px; border-radius: 8px; cursor: pointer; transition: all 0.2s; font-size: 14px; color: #8b949e; }
                div[data-testid="stRadio"] input { display: none; }
                div[data-testid="stRadio"] label[data-checked="true"] { font-weight: bold; border: 1px solid transparent; color: white; background-color: #238636; }
            </style>
            """, unsafe_allow_html=True)
            
            st.caption("Geospatial view of returns vs. historical sales hotspots.")
    
            # Folium Map
            m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles='CartoDB dark_matter')
    
            # Marker 1: Hyderabad
            popup_html = """
            <div style="font-family: sans-serif; width: 200px; background-color: #161b22; color: white; border-radius: 8px; overflow: hidden;">
                <div style="background-color: #21262d; padding: 8px 12px; border-bottom: 1px solid #30363d; font-size: 10px; font-weight: bold; color: #fb8c00; display: flex; align-items: center; gap: 5px;">
                    <span>●</span> RETURN REQUEST
                </div>
                <div style="padding: 12px;">
                    <div style="font-size: 14px; font-weight: bold; margin-bottom: 4px;">Product 47 - Grocery</div>
                    <div style="font-size: 11px; color: #8b949e; margin-bottom: 12px;">Hyderabad • Open Box</div>
                    
                    <div style="background-color: #0d1117; padding: 8px; border-radius: 4px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; font-size: 10px; margin-bottom: 4px;">
                            <span style="color: #8b949e;">REC. CHANNEL</span>
                            <span style="color: #fb8c00; font-weight: bold;">BlinkIt</span>
                        </div>
                         <div style="display: flex; justify-content: space-between; font-size: 10px;">
                            <span style="color: #8b949e;">EST. PROFIT</span>
                            <span style="color: #00E676; font-weight: bold;">₹1100</span>
                        </div>
                    </div>
                    <button style="width: 100%; background: linear-gradient(90deg, #536DFE, #7C4DFF); border: none; padding: 8px; border-radius: 4px; color: white; font-size: 11px; font-weight: bold; cursor: pointer;">View Analysis</button>
                </div>
            </div>
            """
            folium.Marker([17.3850, 78.4867], popup=folium.Popup(popup_html, max_width=250), icon=folium.Icon(color="orange", icon="info-sign", prefix='fa')).add_to(m)
            # Circles
            folium.CircleMarker([28.7041, 77.1025], radius=8, color='#FF5252', fill=True, fill_color='#FF5252', fill_opacity=0.7).add_to(m)
            folium.CircleMarker([19.0760, 72.8777], radius=10, color='#00E676', fill=True, fill_color='#00E676', fill_opacity=0.5).add_to(m)
            folium.CircleMarker([12.9716, 77.5946], radius=12, color='#00E676', fill=True, fill_color='#00E676', fill_opacity=0.5).add_to(m)
            folium.CircleMarker([13.0827, 80.2707], radius=8, color='#FF5252', fill=True, fill_color='#FF5252', fill_opacity=0.7).add_to(m)
    
            st_folium(m, height=400, width="100%", use_container_width=True)
            
            st.markdown("""
            <div style="display: flex; justify-content: center; gap: 20px; font-size: 12px; color: #8b949e; margin-top: 10px;">
                <div style="display: flex; align-items: center; gap: 5px;"><span style="color: #FF5252;">●</span> Return Item (Size ~ Profit)</div>
                <div style="display: flex; align-items: center; gap: 5px;"><span style="color: #00E676;">●</span> Fast Sale (Density)</div>
                <div style="display: flex; align-items: center; gap: 5px;"><span style="color: #fb8c00;">●</span> Blinkit</div>
                <div style="display: flex; align-items: center; gap: 5px;"><span style="color: #3d5afe;">●</span> Zepto</div>
                 <div style="display: flex; align-items: center; gap: 5px;"><span style="color: #ff7043;">●</span> Swiggy</div>
            </div>
            """, unsafe_allow_html=True)
    
        with r1_col2:
            st.markdown('<div style="background-color: #0d1117; border: 1px solid #30363d; border-radius: 10px; padding: 15px; height: 100%;">', unsafe_allow_html=True)
            st.markdown("##### Regional Sales vs Returns")
            cities = ['Mumbai', 'Pune', 'Bangalore', 'Gurgaon', 'Chennai', 'Hyderabad', 'Delhi']
            sales_vol = [22, 18, 25, 15, 12, 20, 15]
            returns_vol = [5, 6, 8, 5, 6, 10, 8]
            fig = go.Figure()
            fig.add_trace(go.Bar(y=cities, x=returns_vol, name='Returns', orientation='h', marker_color='#FF5252', hovertemplate="<span style='color:#FF5252'>Returns : %{x}</span><extra></extra>"))
            fig.add_trace(go.Bar(y=cities, x=sales_vol, name='Sales', orientation='h', marker_color='#00E676', hovertemplate="<span style='color:#00E676'>Sales : %{x}</span><extra></extra>"))
            fig.update_layout(barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white', size=10), margin=dict(t=10, b=10, l=10, r=10), height=250, showlegend=False, xaxis=dict(showticklabels=False, showgrid=False), yaxis=dict(autorange="reversed"), hovermode="y unified", hoverlabel=dict(bgcolor="#161b22", font_size=14, font_family="sans-serif"))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="background-color: #121d2f; border: 1px solid #1c2e4a; border-left: 4px solid #3d5afe; border-radius: 8px; padding: 15px;">
                <div style="color: #3d5afe; font-weight: bold; font-size: 13px; margin-bottom: 5px;">⚡ Optimization Tip</div>
                <div style="color: #c9d1d9; font-size: 12px; line-height: 1.5;">Consolidate returns from <span style="color: #FF5252;">Delhi</span> and route to <span style="color: #00E676;">Gurgaon</span> for faster Blinkit resale. Demand density is 3.5x higher.</div>
            </div>
            """, unsafe_allow_html=True)
    
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("#### Inventory Re-routing Plan (Return Origin → Resale Destination)")
        
        # Helper function for rendering tags
        def render_row(origin, platform, vol, cat, dest, app, demand, key_id):
            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([2, 1, 0.8, 1.2, 2, 1, 1, 1.5])
            c1.markdown(f"<span style='color:#FF5252;'>📍</span> {origin}", unsafe_allow_html=True)
            c2.write(platform)
            c3.write(str(vol))
            if cat == "Beauty": c4.markdown("<span style='background-color: rgba(56, 139, 253, 0.15); color: #388bfd; border: 1px solid rgba(56, 139, 253, 0.4); padding: 2px 8px; border-radius: 12px; font-size: 11px;'>Beauty</span>", unsafe_allow_html=True)
            elif cat == "Home": c4.markdown("<span style='background-color: rgba(235, 87, 87, 0.15); color: #eb5757; border: 1px solid rgba(235, 87, 87, 0.4); padding: 2px 8px; border-radius: 12px; font-size: 11px;'>Home</span>", unsafe_allow_html=True)
            elif cat == "Electronics": c4.markdown("<span style='background-color: rgba(242, 201, 76, 0.15); color: #f2c94c; border: 1px solid rgba(242, 201, 76, 0.4); padding: 2px 8px; border-radius: 12px; font-size: 11px;'>Electronics</span>", unsafe_allow_html=True)
            c5.markdown(f"<span style='color: #00E676; font-weight: bold;'>↗ {dest}</span>", unsafe_allow_html=True)
            if app == "Blinkit": c6.markdown("<span style='color: #f2c94c; font-weight: bold;'>Blinkit</span>", unsafe_allow_html=True)
            else: c6.markdown("<span style='color: #00E676; font-weight: bold;'>BB Now</span>", unsafe_allow_html=True)
            c7.caption(demand)
            if c8.button("Generate Label", key=key_id):
                st.session_state.detail_drawer_open = True
                st.rerun()
            st.markdown("<hr style='margin: 5px 0; border-color: #30363d; opacity: 0.3;'>", unsafe_allow_html=True)
    
        h1, h2, h3, h4, h5, h6, h7, h8 = st.columns([2, 1, 0.8, 1.2, 2, 1, 1, 1.5])
        h1.caption("RETURN ORIGIN (SOURCE)")
        h2.caption("PLATFORM")
        h3.caption("QTY")
        h4.caption("CATEGORY")
        h5.caption("BEST RESALE DESTINATION")
        h6.caption("TARGET APP")
        h7.caption("EST. DEMAND")
        h8.caption("ACTION")
        st.markdown("<hr style='margin: 0 0 10px 0; border-color: #30363d;'>", unsafe_allow_html=True)
        render_row("Delhi, Delhi", "Myntra", 9, "Beauty", "Mumbai, Maharashtra", "Blinkit", "21 units/mo", "btn_delhi")
        render_row("Hyderabad, Telangana", "Flipkart", 11, "Home", "Mumbai, Maharashtra", "Blinkit", "21 units/mo", "btn_hyd")
        render_row("Chennai, Tamil Nadu", "Flipkart", 8, "Home", "Mumbai, Maharashtra", "Blinkit", "21 units/mo", "btn_chn")
        render_row("Gurgaon, Haryana", "Amazon", 6, "Electronics", "Bangalore, Karnataka", "BB Now", "23 units/mo", "btn_gur")

    # Render Sidebar / Drawer in the specific column if open
    if st.session_state.detail_drawer_open and sidebar_container:
        with sidebar_container:
             generateLabel.show()
