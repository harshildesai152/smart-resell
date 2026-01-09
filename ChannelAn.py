import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def show():
    # Check if data has been processed
    if not st.session_state.get('channel_processed', False):
        st.warning("⚠️ Please upload both returns and sales data first using the 'Ingest Data' page to see channel performance analytics.")
        st.info("Go to 'Ingest Data' → Upload your returns and sales data → Click 'Run Preprocessing & Predict'")
        return

    channel_data = st.session_state.get('channel_data', {})
    # Header
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("Channel Performance Analytics")
    with col2:
        st.success("● System Active")

    # KPI Layout
    k1, k2, k3, k4 = st.columns(4)
    
    # Helper for KPI Card
    def kpi_card(title, value, delta, color):
        st.markdown(f"""
        <div style="background-color: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 15px;">
            <div style="color: #8b949e; font-size: 12px; margin-bottom: 5px; text-transform: uppercase; font-weight: 600;">{title}</div>
            <div style="color: white; font-size: 24px; font-weight: bold;">{value}</div>
            <div style="color: {color}; font-size: 12px; margin-top: 5px; font-weight: 500;">{delta}</div>
        </div>
        """, unsafe_allow_html=True)

    header_metrics = channel_data.get('header_metrics', {})

    # Format total revenue
    total_revenue = header_metrics.get('total_revenue', 0)
    revenue_display = f"₹{total_revenue/1000000:.1f}M" if total_revenue >= 1000000 else f"₹{total_revenue/1000:.0f}K"

    # Format return rate with color logic
    return_rate = header_metrics.get('return_rate_percent', 0)
    return_color = "#FF5252" if return_rate > 5 else "#00E676"  # Red for high return rate, green for low

    with k1: kpi_card("Total Revenue", revenue_display, "▲ 12% vs last month", "#00E676")
    with k2: kpi_card("Top Channel", header_metrics.get('top_channel', 'N/A'), f"{header_metrics.get('market_share', 0):.1f}% Market Share", "#F4C430")
    with k3: kpi_card("Avg Commission", f"{header_metrics.get('avg_commission_percent', 0):.1f}%", "▼ 1.2% saved", "#00E676")
    with k4: kpi_card("Return Rate", f"{return_rate:.1f}%", "▲ 0.3% alert", return_color)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Section
    c1, c2 = st.columns([2, 1], gap="medium")
    
    with c1:
        st.markdown('<div style="background-color: #0d1117; border: 1px solid #30363d; border-radius: 10px; padding: 20px; height: 100%;">', unsafe_allow_html=True)
        st.markdown("### Revenue by Channel (Trend)")

        # Get real revenue trend data
        revenue_trend = channel_data.get('revenue_trend')
        if revenue_trend is not None and not revenue_trend.empty:
            # Pivot data for plotting
            revenue_pivot = revenue_trend.pivot(index='month', columns='platform', values='revenue').fillna(0)

            # Create month labels
            month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                          7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

            months = [month_names.get(m, str(m)) for m in revenue_pivot.index]

            # Platform colors
            platform_colors = {
                'Blinkit': '#F4C430',
                'Swiggy Instamart': '#FF5252',
                'Zepto': '#7C4DFF',
                'BB Now': '#00E676'
            }

            fig_trend = go.Figure()

            for platform in revenue_pivot.columns:
                values = revenue_pivot[platform].values / 1000  # Convert to thousands
                color = platform_colors.get(platform, '#8b949e')
                fig_trend.add_trace(go.Scatter(
                    x=months,
                    y=values,
                    mode='lines+markers',
                    name=platform,
                    line=dict(color=color, width=3)
                ))
        else:
            # Fallback to mock data if no data available
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            blinkit = [120, 132, 145, 150, 170, 190]
            swiggy = [100, 105, 110, 115, 120, 125]
            zepto = [80, 85, 95, 110, 130, 145]

            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=months, y=blinkit, mode='lines+markers', name='Blinkit', line=dict(color='#F4C430', width=3)))
            fig_trend.add_trace(go.Scatter(x=months, y=swiggy, mode='lines+markers', name='Swiggy Instamart', line=dict(color='#FF5252', width=3)))
            fig_trend.add_trace(go.Scatter(x=months, y=zepto, mode='lines+markers', name='Zepto', line=dict(color='#7C4DFF', width=3))) 
        
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8b949e'),
            height=320,
            hovermode="x unified",
            xaxis=dict(gridcolor='#30363d'),
            yaxis=dict(gridcolor='#30363d'),
            margin=dict(l=0, r=0, t=20, b=0),
            legend=dict(orientation="h", y=1.1, font=dict(color='white'))
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div style="background-color: #0d1117; border: 1px solid #30363d; border-radius: 10px; padding: 20px; height: 100%;">', unsafe_allow_html=True)
        st.markdown("### Market Share")

        # Get real market share data
        market_share = channel_data.get('market_share')
        if market_share is not None and not market_share.empty:
            labels = market_share['platform'].tolist()
            values = market_share['market_share'].tolist()
            # Platform colors
            platform_colors = {
                'Blinkit': '#F4C430',
                'Swiggy Instamart': '#FF5252',
                'Zepto': '#7C4DFF',
                'BB Now': '#00E676'
            }
            colors = [platform_colors.get(platform, '#8b949e') for platform in labels]
        else:
            # Fallback to mock data
            labels = ['Blinkit', 'Swiggy', 'Zepto', 'BB Now']
            values = [42, 28, 20, 10]
            colors = ['#F4C430', '#FF5252', '#7C4DFF', '#00E676']
        
        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6)])
        fig_pie.update_traces(marker=dict(colors=colors))
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8b949e'),
            height=320,
            margin=dict(l=0, r=0, t=20, b=0),
            showlegend=True,
            legend=dict(orientation="h", y=-0.2, font=dict(color='white'))
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Detailed Comparison Table metrics
    st.markdown("### 📊 Platform Performance Metrics")
    
    st.markdown("""
    <style>
        .ch-header { color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; }
        .ch-row { border-bottom: 1px solid #21262d; padding: 15px 0; display: flex; align-items: center; color: #c9d1d9; font-size: 13px; }
        .ch-badge { padding: 4px 8px; border-radius: 12px; font-size: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
    
    # Headers
    h1, h2, h3, h4, h5 = st.columns([2, 1.5, 1.5, 1.5, 1.5])
    h1.markdown('<div class="ch-header">PLATFORM</div>', unsafe_allow_html=True)
    h2.markdown('<div class="ch-header">DELIVERY SPEED</div>', unsafe_allow_html=True)
    h3.markdown('<div class="ch-header">CONVERSION</div>', unsafe_allow_html=True)
    h4.markdown('<div class="ch-header">RTN RATE</div>', unsafe_allow_html=True)
    h5.markdown('<div class="ch-header">RATING</div>', unsafe_allow_html=True)
    st.markdown("<div style='border-bottom: 1px solid #30363d; margin-top: 5px;'></div>", unsafe_allow_html=True)

    def render_row(name, speed, conv, rtn, rating, color):
        c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 1.5, 1.5])
        c1.markdown(f'<div class="ch-row" style="border:none;"><span style="color:{color}; font-weight:bold;">{name}</span></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="ch-row" style="border:none;">{speed} mins</div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="ch-row" style="border:none;">{conv}%</div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="ch-row" style="border:none;">{rtn}%</div>', unsafe_allow_html=True)
        c5.markdown(f'<div class="ch-row" style="border:none;">⭐ {rating}</div>', unsafe_allow_html=True)
        st.markdown("<div style='border-bottom: 1px solid #21262d; opacity: 0.5;'></div>", unsafe_allow_html=True)

    # Get real platform metrics data
    platform_metrics = channel_data.get('platform_metrics')
    if platform_metrics is not None and not platform_metrics.empty:
        # Platform colors
        platform_colors = {
            'Blinkit': '#F4C430',
            'Swiggy Instamart': '#FF5252',
            'Zepto': '#7C4DFF',
            'BB Now': '#00E676'
        }

        for _, row in platform_metrics.iterrows():
            platform_name = row['platform']
            delivery_speed = int(row['delivery_speed'])
            conversion = row['conversion']
            rtn_rate = row['rtn_rate']
            rating = row['rating']
            color = platform_colors.get(platform_name, '#8b949e')

            render_row(platform_name, delivery_speed, conversion, rtn_rate, rating, color)
    else:
        # Fallback to mock data
        render_row("Blinkit", 12, 18.2, 3.1, 4.8, "#F4C430")
        render_row("Swiggy Instamart", 16, 15.5, 4.0, 4.6, "#FF5252")
        render_row("Zepto", 11, 14.8, 3.8, 4.7, "#7C4DFF")
        render_row("BB Now", 25, 10.2, 5.5, 4.2, "#00E676")
