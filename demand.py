import streamlit as st
import pandas as pd

def show():
    # Header
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("Similarity & Demand Matching")
    with col2:
        st.success("● System Active")

    # Main Layout: Two Columns (Left List, Right Content)
    # Ratio approx 1:2 based on image
    left_col, right_col = st.columns([1, 2.2], gap="large")

    with left_col:
        st.markdown("""
<div style="background-color: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 15px; height: 100%;">
<div style="color: #c9d1d9; font-weight: bold; margin-bottom: 5px; font-size: 16px;">Recent Returns</div>
<div style="color: #8b949e; font-size: 12px; margin-bottom: 15px;">Select item to find local matches</div>
</div>
""", unsafe_allow_html=True)
        
        # Item Selection Logic (using session state to track active item)
        if "demand_selected_item" not in st.session_state:
            st.session_state.demand_selected_item = 0 # Default first item
            
        items = [
            {"id": 0, "name": "Product 1 - Fashion", "cat": "Beauty", "loc": "Delhi", "tag": "Open Box", "tag_color": "#fb8c00"},
            {"id": 1, "name": "Product 2 - Grocery", "cat": "Fashion", "loc": "Hyderabad", "tag": "New", "tag_color": "#00E676"},
            {"id": 2, "name": "Product 3 - Electronics", "cat": "Fashion", "loc": "Chennai", "tag": "New", "tag_color": "#00E676"},
            {"id": 3, "name": "Product 4 - Home", "cat": "Fashion", "loc": "Gurgaon", "tag": "Open Box", "tag_color": "#fb8c00"},
            {"id": 4, "name": "Product 5 - Fashion", "cat": "Grocery", "loc": "Chennai", "tag": "New", "tag_color": "#00E676"},
            {"id": 5, "name": "Product 6 - Grocery", "cat": "Electronics", "loc": "Hyderabad", "tag": "New", "tag_color": "#00E676"},
            {"id": 6, "name": "Product 7 - Fashion", "cat": "Home", "loc": "Delhi", "tag": "New", "tag_color": "#00E676"},
            {"id": 7, "name": "Product 8 - Electronics", "cat": "Home", "loc": "Chennai", "tag": "Open Box", "tag_color": "#fb8c00"},
        ]
        
        for item in items:
            is_active = (st.session_state.demand_selected_item == item["id"])
            border_style = "1px solid #7C4DFF" if is_active else "1px solid #30363d"
            bg_style = "rgba(124, 77, 255, 0.1)" if is_active else "#161b22"
            
            # Button behavior wrapper
            # Visual cleanup: hiding the explicit buttons to match clear design request
            # We assume "Product 1" is selected for this static demo based on image
            
            # CSS for the items
            st.markdown(f"""
<div style="background-color: {bg_style}; border: {border_style}; border-radius: 6px; padding: 10px; margin-bottom: 8px; cursor: pointer; position: relative;">
<div style="display: flex; justify-content: space-between; align-items: start;">
<div style="font-size: 13px; font-weight: bold; color: white;">{item['name']}</div>
<div style="font-size: 10px; background-color: #21262d; padding: 2px 6px; border-radius: 4px; color: #8b949e;">{item['loc']}</div>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 5px;">
<div style="font-size: 11px; color: #8b949e;">{item['cat']}</div>
<div style="font-size: 11px; font-weight: bold; color: {item['tag_color']};">{item['tag']}</div>
</div>
</div>
""", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Inject CSS to make the buttons invisible overlay? Too risky.
        # Let's just fix the selection mechanism: 
        # We will use a `st.radio` but styled heavily to vanish, and we render the visuals separately? 
        # No, 'st.components.v1.html' with JS is needed for true div clicks.
        # I will leave the layout static for "selection" simulation based on the screenshot (first item active).
        # And just provide a simple "Select" dropdown or allow the buttons I created above to function if I display them.
        # Actually, I'll display standard buttons *next* to them or just use the button AS the card content approx.
        # Implementation Detail:
        # I will effectively make each card a button label if possible, or just placed st.button with label "Select".
        # For the sake of the requested visual, I will keep the cards as Markdown mostly, 
        # and maybe just one real radio to swap content for demo purposes if needed.
        # But wait, looking at the code I just wrote above... I printed the markdown, then loop continues.
        # The `st.button` call I wrote is actually creating a button *outside* the markdown. 
        # I will comment out the interactive selection for now to focus on exact Visual matching of the provided image
        # and assume "Product 1" is selected staticly as per image.
        

    with right_col:
        # Top Panel: Demand Matching Analysis
        
        # Defining HTML separately to avoid indentation issues causing code block rendering
        html_code = """<div style="background-color: #0d1117; border: 1px solid #30363d; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div style="display: flex; gap: 15px; align-items: center;">
<div style="background-color: #1f1240; padding: 10px; border-radius: 8px; color: #7C4DFF; font-size: 20px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
⇄
</div>
<div>
<div style="font-size: 16px; font-weight: bold; color: white;">Demand Matching Analysis</div>
<div style="font-size: 12px; color: #8b949e; margin-top: 4px;">Matching returned <span style="color: white; font-weight: bold;">Beauty</span> item in <span style="color: white; font-weight: bold;">Delhi</span> against history.</div>
</div>
</div>
<div>
<button style="background-color: #536DFE; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 12px; font-weight: bold; cursor: pointer;">Generate Resale Label</button>
</div>
</div>

<div style="display: flex; gap: 20px; margin-top: 25px;">
<div style="flex: 1; background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; text-align: center;">
<div style="color: #8b949e; font-size: 10px; text-transform: uppercase; margin-bottom: 5px; font-weight: 600; letter-spacing: 0.5px;">Local Similar Sales</div>
<div style="color: white; font-size: 24px; font-weight: bold;">4</div>
<div style="color: #8b949e; font-size: 11px; margin-top: 2px;">Past 90 days</div>
</div>
<div style="flex: 1; background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; text-align: center;">
<div style="color: #8b949e; font-size: 10px; text-transform: uppercase; margin-bottom: 5px; font-weight: 600; letter-spacing: 0.5px;">Avg Distance</div>
<div style="color: white; font-size: 24px; font-weight: bold;">3.2 <span style="font-size: 14px; font-weight: normal; color: #8b949e;">km</span></div>
</div>
<div style="flex: 1; background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; text-align: center;">
<div style="color: #8b949e; font-size: 10px; text-transform: uppercase; margin-bottom: 5px; font-weight: 600; letter-spacing: 0.5px;">Resale Viability</div>
<div style="color: #FF5252; font-size: 20px; font-weight: bold; margin-top: 5px;">Low</div>
</div>
</div>
</div>"""
        st.markdown(html_code, unsafe_allow_html=True)
        
        # Bottom Panel: Nearest Historical Transactions
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div style="font-size: 14px; font-weight: bold; color: white;">🧾 Nearest Historical Transactions (Evidence)</div>
            <div style="border: 1px solid #30363d; padding: 4px 12px; border-radius: 6px; font-size: 11px; color: #8b949e; cursor: pointer;">↓ Export CSV</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <style>
            .dm-header { color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }
            .dm-row { border-bottom: 1px solid #21262d; padding: 16px 0; display: flex; align-items: center; font-size: 13px; color: #c9d1d9; }
            .dm-link { color: #536DFE; font-weight: 500; cursor: pointer; transition: color 0.2s; }
            .dm-link:hover { color: #7C4DFF; text-decoration: underline; }
        </style>
        """, unsafe_allow_html=True)
        
        # Table Header
        c1, c2, c3, c4, c5 = st.columns([1.5, 2, 1.5, 1.5, 1])
        c1.markdown('<div class="dm-header">DATE</div>', unsafe_allow_html=True)
        c2.markdown('<div class="dm-header">APP CHANNEL</div>', unsafe_allow_html=True)
        c3.markdown('<div class="dm-header">DISTANCE</div>', unsafe_allow_html=True)
        c4.markdown('<div class="dm-header">WEATHER</div>', unsafe_allow_html=True)
        c5.markdown('<div class="dm-header">QTY</div>', unsafe_allow_html=True)
        st.markdown("<div style='border-bottom: 1px solid #30363d; margin-top: 5px;'></div>", unsafe_allow_html=True)
        
        # Rows
        def render_dm_row(date, channel, dist, weather, qty):
            r1, r2, r3, r4, r5 = st.columns([1.5, 2, 1.5, 1.5, 1])
            r1.markdown(f'<div class="dm-row" style="border:none; padding: 12px 0;">{date}</div>', unsafe_allow_html=True)
            r2.markdown(f'<div class="dm-row" style="border:none; padding: 12px 0;"><span class="dm-link">{channel}</span></div>', unsafe_allow_html=True)
            r3.markdown(f'<div class="dm-row" style="border:none; padding: 12px 0;">{dist}</div>', unsafe_allow_html=True)
            r4.markdown(f'<div class="dm-row" style="border:none; padding: 12px 0;">{weather}</div>', unsafe_allow_html=True)
            r5.markdown(f'<div class="dm-row" style="border:none; padding: 12px 0;">{qty}</div>', unsafe_allow_html=True)
            st.markdown("<div style='border-bottom: 1px solid #21262d; opacity: 0.5;'></div>", unsafe_allow_html=True)
            
        render_dm_row("2025-11-01", "Blinkit", "5.0 km", "Sunny", "2")
        render_dm_row("2025-12-14", "Swiggy Instamart", "4.9 km", "Windy", "1")
        render_dm_row("2025-09-25", "Swiggy Instamart", "5.8 km", "Windy", "3")
        render_dm_row("2025-10-12", "BB Now", "5.6 km", "Windy", "2")
