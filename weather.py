import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import generateLabel

def show():
    # Check if data has been processed
    if not st.session_state.get('weather_processed', False):
        st.warning("⚠️ Please upload both returns and sales data first using the 'Ingest Data' page to see weather analysis.")
        st.info("Go to 'Ingest Data' → Upload your returns and sales data → Click 'Run Preprocessing & Predict'")
        return

    weather_data = st.session_state.get('weather_data', {})
    # Header
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("Weather Impact Assessment")
    with col2:
        st.success("● System Active")
        
    # Initialize Drawer
    if "detail_drawer_open" not in st.session_state:
        st.session_state.detail_drawer_open = False
        
    # Global Layout Split
    if st.session_state.detail_drawer_open:
        main_col, side_col = st.columns([3, 1.2], gap="medium")
    else:
        main_col = st.container()
        side_col = None
        
    # Main Content
    with main_col:
        # 1. Weather Distribution Chart (Weather vs Sales Count)
        fig = go.Figure()

        # Get weather vs sales count data
        page2_graph = weather_data.get('page2_graph')
        if page2_graph is not None and not page2_graph.empty:
            weather_types = page2_graph['weather'].tolist()
            counts = page2_graph['sales_count'].tolist()
            colors = ['#536DFE', '#00E676', '#FFAB00', '#FF5252', '#9C27B0']
        else:
            # Fallback static data
            weather_types = ['Sunny', 'Rainy', 'Windy', 'Cloudy']
            counts = [32, 32, 52, 34]
            colors = ['#536DFE', '#00E676', '#FFAB00', '#FF5252']

        fig.add_trace(go.Bar(
            x=weather_types,
            y=counts,
            marker_color=colors[:len(weather_types)],
            hovertemplate="<b>%{x}</b><br>Sales Count: %{y}<extra></extra>"
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8b949e'),
            margin=dict(t=20, b=20, l=40, r=20),
            height=300,
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor='#30363d', zeroline=False),
            hoverlabel=dict(bgcolor='#161b22', font_size=14)
        )
        
        st.markdown('<div style="background-color: #0d1117; border: 1px solid #30363d; border-radius: 10px; padding: 20px;">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. Strategy Cards
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div style="background-color: #0b1828; border: 1px solid #1c2e4a; padding: 20px; border-radius: 8px;">
                <div style="color: #388bfd; font-weight: bold; margin-bottom: 8px; font-size: 14px;">
                     🌧️ Rainy Day Strategy
                </div>
                <div style="color: #388bfd; font-size: 12px; opacity: 0.8; line-height: 1.5;">
                    Sales spike by 15% during rainy days for Grocery and Home categories. Ensure instant delivery availability.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown("""
            <div style="background-color: #1f1208; border: 1px solid #3e1f0e; padding: 20px; border-radius: 8px;">
                <div style="color: #fb8c00; font-weight: bold; margin-bottom: 8px; font-size: 14px;">
                     🌤️ Sunny Day Trend
                </div>
                <div style="color: #fb8c00; font-size: 12px; opacity: 0.8; line-height: 1.5;">
                    Fashion and Electronics perform best on clear days. Consider outdoor promotions.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 3. Weather Statistics Table
        st.markdown("##### Weather Impact Statistics")
        st.markdown("""
        <style>
            .w-table-header { color: #8b949e; font-size: 11px; text-transform: uppercase; font-weight: bold; margin-bottom: 10px; }
            .w-row { border-bottom: 1px solid #21262d; padding: 12px 0; display: flex; align-items: center; }
            .w-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        h1, h2, h3, h4, h5 = st.columns([2, 1.5, 1.5, 1.5, 1])
        h1.markdown('<div class="w-table-header">WEATHER CONDITION</div>', unsafe_allow_html=True)
        h2.markdown('<div class="w-table-header">TOTAL TRANSACTIONS</div>', unsafe_allow_html=True)
        h3.markdown('<div class="w-table-header">MARKET SHARE</div>', unsafe_allow_html=True)
        h4.markdown('<div class="w-table-header">AVG ORDER VALUE</div>', unsafe_allow_html=True)
        h5.markdown('<div class="w-table-header">ACTION</div>', unsafe_allow_html=True)
        st.markdown("<div style='border-bottom: 1px solid #30363d;'></div>", unsafe_allow_html=True)
        
        def render_weather_row(label, color, txns, share, aov, key_id):
            c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 1.5, 1])
            c1.markdown(f'<span class="w-dot" style="background-color: {color};"></span> {label}', unsafe_allow_html=True)
            c2.caption(str(txns))
            c3.caption(share)
            c4.caption(f"₹{aov}")
            
            # Action Button
            if c5.button("...", key=key_id):
                st.session_state.detail_drawer_open = True
                st.session_state.active_weather_filter = label
                st.rerun()
            
            st.markdown("<div style='border-bottom: 1px solid #21262d; margin-bottom: 8px; opacity: 0.5;'></div>", unsafe_allow_html=True)

        # Get weather impact table data
        weather_impact_table = weather_data.get('weather_impact_table')

        if weather_impact_table is not None and not weather_impact_table.empty:
            color_map = {
                "Sunny": "#536DFE",
                "Rainy": "#00E676",
                "Windy": "#FFAB00",
                "Cloudy": "#FF5252",
                "Winter": "#9C27B0"
            }

            for _, row in weather_impact_table.iterrows():
                weather_name = row['weather']
                color = color_map.get(weather_name, "#808080")
                txns = int(row['total_transactions'])
                share = f"{row['market_share']}%"
                aov = int(row['avg_order_value']) if not pd.isna(row['avg_order_value']) else 0

                render_weather_row(weather_name, color, txns, share, aov, f"btn_{weather_name.lower()}")
        else:
            # Fallback static data
            render_weather_row("Sunny", "#536DFE", 32, "21.3%", 807, "btn_sunny")
            render_weather_row("Rainy", "#00E676", 32, "21.3%", 301, "btn_rainy")
            render_weather_row("Windy", "#FFAB00", 52, "34.7%", 397, "btn_windy")
            render_weather_row("Cloudy", "#FF5252", 34, "22.7%", 242, "btn_cloudy")
        
        
    # Sidebar Drawer
    if st.session_state.detail_drawer_open and side_col:
        with side_col:
            # We'll assume "Sunny" is the active filter for the demo since that's what's in the image
            # Or use the stored session state if flexible
            filter_name = st.session_state.get('active_weather_filter', 'Sunny')
            generateLabel.show(
                title=f"Sales during {filter_name} Weather", 
                subtitle="32 records found", 
                mode="sales"
            )
