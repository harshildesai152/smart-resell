import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def show():
    # Top Header
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("Executive Overview")
    with col2:
        st.success("● System Active")

    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(label="TOTAL RETURNS", value="50", delta="12.5% vs last month")

    with m2:
        st.metric(label="TOTAL SALES DATA", value="150", delta="12.5% vs last month")

    with m3:
        st.metric(label="AVG PROFIT/ITEM", value="₹245", delta="-2.3% vs last month")

    with m4:
        st.metric(label="PREDICTION ACCURACY", value="88%", delta="12.5% vs last month")

    st.markdown("---")

    # Chart 1: Returns vs Sales Volume (Overview)
    st.subheader("Returns vs Sales Volume (Overview)")

    cities = ['Delhi', 'Hyderabad', 'Chennai', 'Gurgaon', 'Bangalore', 'Pune', 'Mumbai']
    sales = [19, 24, 18, 18, 26, 22, 23]
    returns = [9, 11, 8, 6, 6, 6, 4]

    # Create grouped bar chart
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=cities,
        y=returns,
        name='Returns',
        marker_color='#FF5252',
        hovertemplate="<span style='color:#FF5252'>Returns : %{y}</span><extra></extra>"
    ))
    fig1.add_trace(go.Bar(
        x=cities,
        y=sales,
        name='Sales',
        marker_color='#00E676',
        hovertemplate="<span style='color:#00E676'>Sales : %{y}</span><extra></extra>"
    ))

    fig1.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=300,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#161b22",
            font_size=14,
            font_family="sans-serif"
        )
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Bottom Row: Weather Impact & Top Channel Share
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Weather Impact")
        # Pie chart
        labels = ['Cloudy', 'Rainy', 'Sunny', 'Windy']
        values = [34, 32, 29, 32] # Adjusted to look similar to image
        colors = ['#FF5252', '#00E676', '#7C4DFF', '#FFB74D']
        
        fig2 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.0, marker=dict(colors=colors))])
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=True,
            legend=dict(orientation="h", y=-0.1),
            height=300
        )
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        st.subheader("Top Channel Share")
        # Stacked Bar Chart
        categories = ['Beauty', 'Electronics', 'Home', 'Food', 'Pharma', 'Grocery']
        
        # Zepto (Purple)
        y_zepto = [7, 5, 8, 12, 10, 6]
        # Blinkit (Yellow)
        y_blinkit = [10, 12, 6, 8, 12, 10] 
        # Swiggy (Orange)
        y_swiggy = [5, 8, 12, 10, 8, 12]
        # BB Now (Green)
        y_bbnow = [10, 15, 8, 5, 10, 8]
        
        fig3 = go.Figure()
        
        # Trace 1: Zepto (Purple)
        fig3.add_trace(go.Bar(
            name='Zepto', 
            x=categories, 
            y=y_zepto, 
            marker_color='#5c6bc0', # Purple
            hovertemplate="<span style='color:#5c6bc0'>Zepto : %{y}</span><extra></extra>"
        ))
        
        # Trace 2: Swiggy Instamart (Orange)
        fig3.add_trace(go.Bar(
            name='Swiggy Instamart', 
            x=categories, 
            y=y_swiggy, 
            marker_color='#ff7043', # Orange
            hovertemplate="<span style='color:#ff7043'>Swiggy Instamart : %{y}</span><extra></extra>"
        ))
        
        # Trace 3: Blinkit (Yellow)
        fig3.add_trace(go.Bar(
            name='Blinkit', 
            x=categories, 
            y=y_blinkit, 
            marker_color='#fbc02d', # Yellow
            hovertemplate="<span style='color:#fbc02d'>Blinkit : %{y}</span><extra></extra>"
        ))
        
        # Trace 4: BB Now (Green)
        fig3.add_trace(go.Bar(
            name='BB Now', 
            x=categories, 
            y=y_bbnow, 
            marker_color='#00E676', # Green
            hovertemplate="<span style='color:#00E676'>BB Now : %{y}</span><extra></extra>"
        ))
        
        fig3.update_layout(
            barmode='stack',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=False,
            height=300,
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="#161b22",
                font_size=14,
                font_family="sans-serif"
            )
        )
        st.plotly_chart(fig3, use_container_width=True)
