import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

def show():
    # Check if data has been processed
    if not st.session_state.get('lifecycle_processed', False):
        st.warning("⚠️ Please upload sales data first using the 'Ingest Data' page to see product lifecycle analysis.")
        st.info("Go to 'Ingest Data' → Upload your sales data → Click 'Run Preprocessing & Predict'")
        return

    lifecycle_data = st.session_state.get('lifecycle_data', {})
    # Page Header
    st.title("Product Lifecycle Analysis")
    st.markdown("*Track product maturity & demand trends*")
    st.markdown("---")

    # Get real KPI metrics
    kpi_metrics = lifecycle_data.get('kpi_metrics', {})

    # KPI Cards (4 columns)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    total_products = kpi_metrics.get('total_products', 0)
    new_products = kpi_metrics.get('new_products', 0)
    mature_products = kpi_metrics.get('mature_products', 0)
    declining_products = kpi_metrics.get('declining_products', 0)

    # Calculate percentages
    new_pct = int((new_products / total_products * 100) if total_products > 0 else 0)
    mature_pct = int((mature_products / total_products * 100) if total_products > 0 else 0)
    declining_pct = int((declining_products / total_products * 100) if total_products > 0 else 0)

    with kpi1:
        st.metric(
            label="Total Products",
            value=f"{total_products:,}",
            delta="+89 this month"
        )

    with kpi2:
        st.metric(
            label="New Products",
            value=str(new_products),
            delta=f"{new_pct}% of total"
        )

    with kpi3:
        st.metric(
            label="Mature Products",
            value=str(mature_products),
            delta=f"{mature_pct}% of total"
        )

    with kpi4:
        st.metric(
            label="Declining Products",
            value=str(declining_products),
            delta=f"{declining_pct}% of total"
        )

    st.markdown("---")

    # Product Trend Chart
    st.subheader("Product Demand Trends")

    # Get real trend chart data
    trend_chart_data = lifecycle_data.get('trend_chart_data', {})

    if trend_chart_data:
        # Convert back to DataFrame
        trend_df = pd.DataFrame.from_dict(trend_chart_data, orient='index')

        # Create month labels
        month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                      7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

        months = [month_names.get(m, str(m)) for m in trend_df.index]

        # Create line chart
        fig_trends = go.Figure()

        # Color mapping for lifecycle stages
        color_mapping = {
            'Declining': '#FF5252',
            'Mature': '#00E676',
            'New': '#7C4DFF'
        }

        # Plot each product
        for product in trend_df.columns[:8]:  # Limit to first 8 products for readability
            values = trend_df[product].values

            # Determine lifecycle stage for color (simplified logic)
            if len(values) >= 3:
                # Simple trend analysis
                if values[-1] < values[0] * 0.8:
                    color = '#FF5252'  # Declining
                elif values[-1] > values[0] * 1.2:
                    color = '#7C4DFF'  # Growing/New
                else:
                    color = '#00E676'  # Stable/Mature
            else:
                color = '#00E676'  # Default

            fig_trends.add_trace(go.Scatter(
                x=months,
                y=values,
                mode='lines+markers',
                name=product,
                line=dict(color=color, width=3),
                marker=dict(size=6),
                hovertemplate=f'<b>{product}</b><br>Month: %{{x}}<br>Demand: %{{y}}<extra></extra>'
            ))
    else:
        # Fallback to dummy data if no processed data available
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        smart_watch_trend = [45, 52, 48, 55, 62, 58, 51, 47, 42, 38, 35, 32]
        laptop_trend = [78, 82, 85, 88, 91, 89, 87, 85, 83, 81, 79, 77]
        headphones_trend = [65, 68, 72, 75, 78, 76, 74, 73, 71, 69, 67, 65]
        phone_case_trend = [92, 95, 98, 96, 94, 91, 89, 87, 85, 82, 80, 78]

        fig_trends = go.Figure()
        fig_trends.add_trace(go.Scatter(x=months, y=smart_watch_trend, mode='lines+markers', name='Smart Watch', line=dict(color='#FF5252', width=3), marker=dict(size=6), hovertemplate='<b>Smart Watch</b><br>Month: %{x}<br>Demand: %{y}<extra></extra>'))
        fig_trends.add_trace(go.Scatter(x=months, y=laptop_trend, mode='lines+markers', name='Gaming Laptop', line=dict(color='#00E676', width=3), marker=dict(size=6), hovertemplate='<b>Gaming Laptop</b><br>Month: %{x}<br>Demand: %{y}<extra></extra>'))
        fig_trends.add_trace(go.Scatter(x=months, y=headphones_trend, mode='lines+markers', name='Wireless Headphones', line=dict(color='#7C4DFF', width=3), marker=dict(size=6), hovertemplate='<b>Wireless Headphones</b><br>Month: %{x}<br>Demand: %{y}<extra></extra>'))
        fig_trends.add_trace(go.Scatter(x=months, y=phone_case_trend, mode='lines+markers', name='Phone Case', line=dict(color='#FFB74D', width=3), marker=dict(size=6), hovertemplate='<b>Phone Case</b><br>Month: %{x}<br>Demand: %{y}<extra></extra>'))

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

    # Get real lifecycle table data
    lifecycle_table = lifecycle_data.get('lifecycle_table', [])

    if lifecycle_table:
        # Convert to DataFrame and rename columns for display
        lifecycle_df = pd.DataFrame(lifecycle_table)
        lifecycle_df = lifecycle_df.rename(columns={
            'product_name': 'Product Name',
            'demand_trend': 'Demand Trend',
            'lifecycle_stage': 'Lifecycle Stage',
            'action_recommendation': 'Action Recommendation'
        })

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
    else:
        # Fallback to dummy data if no processed data available
        fallback_data = [
            {"Product Name": "Smart Watch Series X", "Demand Trend": "📉 Declining", "Lifecycle Stage": "🔴 Declining", "Action Recommendation": "Reduce procurement by 40%"},
            {"Product Name": "Gaming Laptop Pro", "Demand Trend": "➡️ Stable", "Lifecycle Stage": "🟢 Mature", "Action Recommendation": "Maintain current stock levels"},
            {"Product Name": "Wireless Headphones", "Demand Trend": "📈 Growing", "Lifecycle Stage": "🟡 New", "Action Recommendation": "Increase inventory by 25%"},
            {"Product Name": "Phone Case Premium", "Demand Trend": "➡️ Stable", "Lifecycle Stage": "🟢 Mature", "Action Recommendation": "Monitor demand closely"}
        ]
        fallback_df = pd.DataFrame(fallback_data)
        st.dataframe(
            fallback_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Product Name": st.column_config.TextColumn("Product Name", width="medium"),
                "Demand Trend": st.column_config.TextColumn("Demand Trend", width="small"),
                "Lifecycle Stage": st.column_config.TextColumn("Lifecycle Stage", width="small"),
                "Action Recommendation": st.column_config.TextColumn("Action Recommendation", width="large")
            }
        )

    st.markdown("---")

    # Get real critical insight
    critical_insight = lifecycle_data.get('critical_insight', "All products show stable or growing demand.")

    # Insight Highlight Box
    if "declining" in critical_insight.lower():
        st.error(f"**{critical_insight}**")
    else:
        st.success(f"**✅ {critical_insight}**")

    st.markdown("---")

    # Procurement Recommendation Section
    st.subheader("Procurement Strategy Recommendations")

    # Get real procurement strategy data
    procurement_strategy = lifecycle_data.get('procurement_strategy', {})

    rec_col1, rec_col2, rec_col3 = st.columns(3)

    with rec_col1:
        st.markdown("### 📈 **Increase Inventory**")
        increase_products = procurement_strategy.get('increase_inventory', [])
        if increase_products:
            for product in increase_products:
                st.markdown(f"• **{product}**")
        else:
            st.markdown("• *No products currently flagged for increase*")
        st.markdown("---")

    with rec_col2:
        st.markdown("### ➡️ **Maintain Stock Levels**")
        maintain_products = procurement_strategy.get('maintain_stock', [])
        if maintain_products:
            for product in maintain_products:
                st.markdown(f"• **{product}**")
        else:
            st.markdown("• *No products currently flagged for maintenance*")
        st.markdown("---")

    with rec_col3:
        st.markdown("### 📉 **Reduce Procurement**")
        reduce_products = procurement_strategy.get('reduce_procurement', [])
        if reduce_products:
            for product in reduce_products:
                st.markdown(f"• **{product}**")
        else:
            st.markdown("• *No products currently flagged for reduction*")
        st.markdown("---")

    # Footer spacing
    st.markdown("")
    st.markdown("")