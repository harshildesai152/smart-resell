import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

def show():
    # Page Header
    st.title("Product Lifecycle Analysis")
    st.markdown("*Track product maturity & demand trends*")
    st.markdown("---")

    # KPI Cards (4 columns)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.metric(
            label="Total Products",
            value="1,247",
            delta="+89 this month"
        )

    with kpi2:
        st.metric(
            label="New Products",
            value="156",
            delta="12.5% of total"
        )

    with kpi3:
        st.metric(
            label="Mature Products",
            value="892",
            delta="71.5% of total"
        )

    with kpi4:
        st.metric(
            label="Declining Products",
            value="199",
            delta="16% of total"
        )

    st.markdown("---")

    # Product Trend Chart
    st.subheader("Product Demand Trends")

    # Create dummy data for product trends
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    # Sample product trend data
    smart_watch_trend = [45, 52, 48, 55, 62, 58, 51, 47, 42, 38, 35, 32]
    laptop_trend = [78, 82, 85, 88, 91, 89, 87, 85, 83, 81, 79, 77]
    headphones_trend = [65, 68, 72, 75, 78, 76, 74, 73, 71, 69, 67, 65]
    phone_case_trend = [92, 95, 98, 96, 94, 91, 89, 87, 85, 82, 80, 78]

    # Create line chart
    fig_trends = go.Figure()

    # Smart Watch (Declining)
    fig_trends.add_trace(go.Scatter(
        x=months,
        y=smart_watch_trend,
        mode='lines+markers',
        name='Smart Watch',
        line=dict(color='#FF5252', width=3),
        marker=dict(size=6),
        hovertemplate='<b>Smart Watch</b><br>Month: %{x}<br>Demand: %{y}<extra></extra>'
    ))

    # Laptop (Mature)
    fig_trends.add_trace(go.Scatter(
        x=months,
        y=laptop_trend,
        mode='lines+markers',
        name='Gaming Laptop',
        line=dict(color='#00E676', width=3),
        marker=dict(size=6),
        hovertemplate='<b>Gaming Laptop</b><br>Month: %{x}<br>Demand: %{y}<extra></extra>'
    ))

    # Headphones (Growing)
    fig_trends.add_trace(go.Scatter(
        x=months,
        y=headphones_trend,
        mode='lines+markers',
        name='Wireless Headphones',
        line=dict(color='#7C4DFF', width=3),
        marker=dict(size=6),
        hovertemplate='<b>Wireless Headphones</b><br>Month: %{x}<br>Demand: %{y}<extra></extra>'
    ))

    # Phone Case (Stable/Mature)
    fig_trends.add_trace(go.Scatter(
        x=months,
        y=phone_case_trend,
        mode='lines+markers',
        name='Phone Case',
        line=dict(color='#FFB74D', width=3),
        marker=dict(size=6),
        hovertemplate='<b>Phone Case</b><br>Month: %{x}<br>Demand: %{y}<extra></extra>'
    ))

    fig_trends.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(t=20, b=20, l=20, r=20),
        height=400,
        xaxis=dict(
            showgrid=True,
            gridcolor='#30363d',
            title="Months"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#30363d',
            title="Demand Index"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='white',
            borderwidth=1
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#161b22",
            font_size=14,
            font_family="sans-serif"
        )
    )

    st.plotly_chart(fig_trends, use_container_width=True)
    st.caption("*Demand trends showing product lifecycle patterns over 12 months*")

    st.markdown("---")

    # Lifecycle Classification Table
    st.subheader("Product Lifecycle Classification")

    # Create table data
    lifecycle_data = [
        {"Product Name": "Smart Watch Series X", "Demand Trend": "📉 Declining", "Lifecycle Stage": "🔴 Declining", "Action Recommendation": "Reduce procurement by 40%"},
        {"Product Name": "Gaming Laptop Pro", "Demand Trend": "➡️ Stable", "Lifecycle Stage": "🟢 Mature", "Action Recommendation": "Maintain current stock levels"},
        {"Product Name": "Wireless Headphones", "Demand Trend": "📈 Growing", "Lifecycle Stage": "🟡 New", "Action Recommendation": "Increase inventory by 25%"},
        {"Product Name": "Phone Case Premium", "Demand Trend": "➡️ Stable", "Lifecycle Stage": "🟢 Mature", "Action Recommendation": "Monitor demand closely"},
        {"Product Name": "Bluetooth Speaker", "Demand Trend": "📉 Declining", "Lifecycle Stage": "🔴 Declining", "Action Recommendation": "Phase out within 3 months"},
        {"Product Name": "Tablet Cover", "Demand Trend": "📈 Growing", "Lifecycle Stage": "🟡 New", "Action Recommendation": "Expand product variants"},
        {"Product Name": "Power Bank 10000mAh", "Demand Trend": "➡️ Stable", "Lifecycle Stage": "🟢 Mature", "Action Recommendation": "Optimize supplier contracts"},
        {"Product Name": "USB-C Cable", "Demand Trend": "📉 Declining", "Lifecycle Stage": "🔴 Declining", "Action Recommendation": "Clear existing inventory"}
    ]

    lifecycle_df = pd.DataFrame(lifecycle_data)

    # Display as styled dataframe
    st.dataframe(
        lifecycle_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Product Name": st.column_config.TextColumn(
                "Product Name",
                width="medium",
            ),
            "Demand Trend": st.column_config.TextColumn(
                "Demand Trend",
                width="small",
            ),
            "Lifecycle Stage": st.column_config.TextColumn(
                "Lifecycle Stage",
                width="small",
            ),
            "Action Recommendation": st.column_config.TextColumn(
                "Action Recommendation",
                width="large",
            )
        }
    )

    st.markdown("---")

    # Insight Highlight Box
    st.error("**📉 Critical Insight:** Smart Watches show declining trend → reduce procurement by 40% to avoid inventory buildup.")

    st.markdown("---")

    # Procurement Recommendation Section
    st.subheader("Procurement Strategy Recommendations")

    rec_col1, rec_col2, rec_col3 = st.columns(3)

    with rec_col1:
        st.markdown("### 📈 **Increase Inventory**")
        st.markdown("• **Wireless Headphones** (+25% growth)")
        st.markdown("• **Tablet Covers** (New category potential)")
        st.markdown("• **Portable Chargers** (Emerging demand)")
        st.markdown("---")

    with rec_col2:
        st.markdown("### ➡️ **Maintain Stock Levels**")
        st.markdown("• **Gaming Laptops** (Stable demand)")
        st.markdown("• **Phone Cases** (Core product)")
        st.markdown("• **Power Banks** (Consistent sales)")
        st.markdown("---")

    with rec_col3:
        st.markdown("### 📉 **Reduce Procurement**")
        st.markdown("• **Smart Watches** (-30% decline)")
        st.markdown("• **Bluetooth Speakers** (-25% decline)")
        st.markdown("• **USB Cables** (Market saturation)")
        st.markdown("---")

    # Footer spacing
    st.markdown("")
    st.markdown("")