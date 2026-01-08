import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

def show():
    # Page Header
    st.title("Price Sensitivity & Discount Simulator")
    st.markdown("*Understand discount impact on demand and profitability*")
    st.markdown("---")

    # Price Slider (Static Display)
    st.subheader("Discount Simulator")

    # Create a visual slider representation (static)
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        st.markdown("**Discount Percentage**")
        st.markdown("*Drag slider to simulate different discount levels*")

    with col2:
        # Static slider display
        st.slider(
            "Discount %",
            min_value=0,
            max_value=50,
            value=15,
            step=5,
            disabled=True,
            help="Current simulation: 15% discount"
        )
        st.markdown("**Current: 15%**")

    with col3:
        st.markdown("**Impact Preview**")
        st.info("📈 **Demand Impact:** +18%\n💰 **Revenue Impact:** -2%\n📊 **Profit Impact:** +12%")

    st.markdown("---")

    # Demand Curve Chart
    st.subheader("Price vs Demand Relationship")

    # Create dummy data for demand curve
    discount_levels = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    demand_impact = [100, 108, 118, 131, 147, 165, 185, 208, 233, 261, 292]  # Elastic demand curve
    revenue_impact = [100, 103, 106, 111, 118, 124, 130, 135, 139, 142, 143]  # Revenue optimization
    profit_impact = [100, 105, 112, 122, 135, 151, 170, 192, 217, 245, 276]  # Profit curve

    # Create line chart
    fig_demand = go.Figure()

    # Demand Impact
    fig_demand.add_trace(go.Scatter(
        x=discount_levels,
        y=demand_impact,
        mode='lines+markers',
        name='Demand Impact (%)',
        line=dict(color='#00E676', width=3),
        marker=dict(size=8),
        hovertemplate='Discount: %{x}%<br>Demand: %{y:.0f}%<extra></extra>'
    ))

    # Revenue Impact
    fig_demand.add_trace(go.Scatter(
        x=discount_levels,
        y=revenue_impact,
        mode='lines+markers',
        name='Revenue Impact (%)',
        line=dict(color='#7C4DFF', width=3),
        marker=dict(size=8),
        hovertemplate='Discount: %{x}%<br>Revenue: %{y:.0f}%<extra></extra>'
    ))

    # Profit Impact
    fig_demand.add_trace(go.Scatter(
        x=discount_levels,
        y=profit_impact,
        mode='lines+markers',
        name='Profit Impact (%)',
        line=dict(color='#FFB74D', width=3),
        marker=dict(size=8),
        hovertemplate='Discount: %{x}%<br>Profit: %{y:.0f}%<extra></extra>'
    ))

    # Add vertical line at current discount (15%)
    fig_demand.add_vline(x=15, line_width=2, line_dash="dash", line_color="#FF5252",
                        annotation_text="Current: 15% Discount", annotation_position="top")

    # Add annotations for optimal points
    fig_demand.add_annotation(
        x=20, y=135,
        text="Revenue Optimum",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#7C4DFF",
        font=dict(size=12, color="#7C4DFF"),
        bgcolor="rgba(0,0,0,0.8)",
        bordercolor="#7C4DFF",
        borderwidth=1,
        borderpad=4
    )

    fig_demand.add_annotation(
        x=25, y=151,
        text="Profit Optimum",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#FFB74D",
        font=dict(size=12, color="#FFB74D"),
        bgcolor="rgba(0,0,0,0.8)",
        bordercolor="#FFB74D",
        borderwidth=1,
        borderpad=4
    )

    fig_demand.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(t=20, b=20, l=20, r=20),
        height=400,
        xaxis=dict(
            title="Discount Percentage (%)",
            showgrid=True,
            gridcolor='#30363d',
            tickmode='array',
            tickvals=[0, 10, 20, 30, 40, 50]
        ),
        yaxis=dict(
            title="Impact Percentage (Base = 100%)",
            showgrid=True,
            gridcolor='#30363d'
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

    st.plotly_chart(fig_demand, use_container_width=True)
    st.caption("*Demand shows elastic behavior while revenue and profit have optimal discount points*")

    st.markdown("---")

    # Profit Impact Section - KPI Cards
    st.subheader("Profit Impact Analysis (15% Discount)")

    impact_col1, impact_col2, impact_col3, impact_col4 = st.columns(4)

    with impact_col1:
        st.metric(
            label="Base Demand",
            value="1,000 units",
            delta="Baseline reference"
        )

    with impact_col1:
        st.metric(
            label="Expected Demand",
            value="1,180 units",
            delta="+18% increase"
        )

    with impact_col2:
        st.metric(
            label="Revenue Impact",
            value="₹2,45,000",
            delta="-2% decrease"
        )

    with impact_col3:
        st.metric(
            label="Profit Change",
            value="₹78,500",
            delta="+12% increase"
        )

    with impact_col4:
        st.metric(
            label="Break-even Point",
            value="22% discount",
            delta="Profit threshold"
        )

    st.markdown("---")

    # Seasonal Insight Box
    st.warning("**🌧️ Seasonal Insight:** 10% discount increases demand by 22% in Rainy season. Leverage weather-based pricing for maximum impact.")

    st.markdown("---")

    # Business Recommendation Section
    st.subheader("Discount Strategy Recommendations")

    rec_col1, rec_col2 = st.columns(2)

    with rec_col1:
        st.markdown("### ✅ **When to Apply Discounts**")
        st.markdown("""
        **High-Impact Scenarios:**
        • **Rainy Season** (+22% demand boost)
        • **New Product Launch** (Build market share)
        • **Clearance Sales** (Move old inventory)
        • **Competitor Pressure** (Maintain market position)
        • **Economic Downturn** (Stimulate demand)

        **Optimal Range:** 10-20% discount for best profit impact
        """)

    with rec_col2:
        st.markdown("### ❌ **When to Avoid Discounts**")
        st.markdown("""
        **Low-Impact Scenarios:**
        • **Peak Season** (Already high demand)
        • **Premium Products** (Price = quality perception)
        • **Limited Stock** (May cause stockouts)
        • **High Competition** (Price wars hurt margins)
        • **Economic Boom** (Customers willing to pay full price)

        **Risk Zone:** Above 25% discount reduces profitability
        """)

    # Additional insights
    st.markdown("### 📊 **Key Takeaways**")
    insight_col1, insight_col2 = st.columns(2)

    with insight_col1:
        st.markdown("""
        **💡 Profit Optimization:**
        • 15-20% discount maximizes profit
        • Revenue peaks at 20% discount
        • Demand elasticity: High (18% at 15%)
        """)

    with insight_col2:
        st.markdown("""
        **🎯 Strategic Pricing:**
        • Weather-based discounts effective
        • Seasonal timing critical for success
        • Monitor competitor responses
        """)

    # Footer spacing
    st.markdown("")
    st.markdown("")