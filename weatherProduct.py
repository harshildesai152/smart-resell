import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import generateLabel

def show():
    # Header
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("Product Performance by Weather")
    with col2:
        st.success("● System Active")
        
    # Initialize Drawer
    if "detail_drawer_open_product" not in st.session_state:
        st.session_state.detail_drawer_open_product = False
        
    # Global Layout Split
    if st.session_state.detail_drawer_open_product:
        main_col, side_col = st.columns([3, 1.2], gap="medium")
    else:
        main_col = st.container()
        side_col = None
        
    with main_col:
        # Header Control Row
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown("#### Top Products by Weather")
        with c2:
            st.selectbox("Select Condition:", ["Sunny", "Rainy", "Cloudy", "Windy"], key="wp_condition", label_visibility="collapsed")
            
        # 1. Horizontal Bar Chart (Best Selling Categories)
        
        st.markdown(f'<div style="background-color: #0d1117; border: 1px solid #30363d; border-radius: 10px; padding: 20px;">', unsafe_allow_html=True)
        st.markdown('<div style="color: #c9d1d9; font-size: 13px; margin-bottom: 10px;">Best Selling Categories during <span style="color: #651FFF; font-weight: bold;">Sunny</span> weather</div>', unsafe_allow_html=True)
        
        fig = go.Figure()
        
        categories = ['Grocery', 'Home', 'Fashion', 'Beauty', 'Electronics']
        values = [4, 5, 6, 7, 10]
        
        fig.add_trace(go.Bar(
            y=categories,
            x=values,
            orientation='h',
            marker_color='#536DFE',
            hovertemplate="<b>%{y}</b><br>value : %{x}<extra></extra>"
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8b949e', size=11),
            margin=dict(t=10, b=10, l=10, r=10),
            height=300,
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', range=[0, 12]),
            yaxis=dict(autorange="reversed"),
            hoverlabel=dict(bgcolor='#161b22', font_size=14)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. Category Performance Table
        
        st.markdown("##### Category Performance: Sunny")
        
        st.markdown("""
        <style>
            .wp-header { color: #8b949e; font-size: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }
            .wp-cell { font-size: 13px; color: #e6edf3; padding: 12px 0; }
            .trend-positive { color: #00E676; font-weight: bold; font-size: 12px; }
            .stock-tag { color: #8b949e; font-size: 12px; }
            .action-link { color: #536DFE; font-size: 12px; font-weight: bold; cursor: pointer; text-decoration: none; }
            .action-link:hover { text-decoration: underline; color: #7C4DFF; }
        </style>
        """, unsafe_allow_html=True)
        
        # Table Header
        h1, h2, h3, h4, h5 = st.columns([2, 1.5, 1.5, 2, 1.5])
        h1.markdown('<div class="wp-header">PRODUCT CATEGORY</div>', unsafe_allow_html=True)
        h2.markdown('<div class="wp-header">SALES COUNT</div>', unsafe_allow_html=True)
        h3.markdown('<div class="wp-header">TREND VS AVG</div>', unsafe_allow_html=True)
        h4.markdown('<div class="wp-header">RECOMMENDED STOCK</div>', unsafe_allow_html=True)
        h5.markdown('<div class="wp-header">ACTION</div>', unsafe_allow_html=True)
        st.markdown("<div style='border-bottom: 1px solid #30363d; margin-top: 5px;'></div>", unsafe_allow_html=True)
        
        def render_product_row(cat, count, trend, stock, key_id):
            c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 2, 1.5])
            
            c1.markdown(f'<div class="wp-cell" style="font-weight: 600;">{cat}</div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="wp-cell">{count}</div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="wp-cell trend-positive">📈 +{trend}%</div>', unsafe_allow_html=True)
            c4.markdown(f'<div class="wp-cell stock-tag">{stock}</div>', unsafe_allow_html=True)
            
            if c5.button("View Products", key=key_id):
                 st.session_state.detail_drawer_open_product = True
                 st.session_state.product_cat_filter = cat
                 st.rerun()
            
            st.markdown("<div style='border-bottom: 1px solid #21262d; opacity: 0.5;'></div>", unsafe_allow_html=True)

        render_product_row("Electronics", 10, 7.8, "High Priority", "btn_elec")
        render_product_row("Beauty", 7, 2.3, "High Priority", "btn_beauty")
        render_product_row("Fashion", 6, 1.5, "High Priority", "btn_fash")
        render_product_row("Home", 5, 16.3, "High Priority", "btn_home")
        render_product_row("Grocery", 4, 1.5, "High Priority", "btn_groc")
        
        
    # Sidebar
    if st.session_state.detail_drawer_open_product and side_col:
        with side_col:
            cat = st.session_state.get("product_cat_filter", "Electronics")
            generateLabel.show(
                title=f"{cat} Sales in Sunny",
                subtitle="10 records found",
                mode="sales"
            )
