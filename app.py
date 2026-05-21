# app.py - Final Working Version (Based on First Working Version)
import streamlit as st
import requests
import re
from datetime import datetime

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="GreenMind - Environmental Advisor", layout="wide")

# ---------------- CSS FOR STICKY HEADER AND CARDS ----------------
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #4CAF50 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        position: sticky;
        top: 0;
        z-index: 999;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        font-size: 2rem;
        margin-bottom: 0.2rem;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header h3 {
        font-size: 0.85rem;
        font-weight: 400;
        font-style: italic;
        margin-bottom: 0;
        background-color: rgba(0,0,0,0.25);
        display: inline-block;
        padding: 0.2rem 1rem;
        border-radius: 30px;
        color: #FFFFFF;
    }
    .stChatMessage {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 10px;
        margin: 8px 0;
        border: 1px solid #e0e0e0;
    }
    .status-box {
        padding: 0.5rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        text-align: center;
        font-size: 0.85rem;
    }
    .connected {
        background-color: #d4edda;
        color: #155724;
    }
    .disconnected {
        background-color: #f8d7da;
        color: #721c24;
    }
    .footer {
        text-align: center;
        color: #666;
        padding: 0.5rem;
        margin-top: 1rem;
        font-size: 0.7rem;
        border-top: 1px solid #e0e0e0;
    }
    .elegant-quote {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 15px;
        text-align: center;
        border-left: 6px solid #2E7D32;
    }
    .quote-text {
        font-size: 1.1rem;
        font-style: italic;
        color: #1B5E20;
    }
    .quote-author {
        font-size: 0.8rem;
        color: #2E7D32;
        text-align: right;
        margin-top: 0.5rem;
    }

    /* Force normal font size for carbon footprint output */
    .carbon-result {
        font-size: 0.95rem !important;
        line-height: 1.6;
    }
    .carbon-result h1, .carbon-result h2, .carbon-result h3 {
        font-size: 1rem !important;
        font-weight: bold;
        margin: 0.4rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- MCP CONFIG ----------------
MCP_URL = "http://127.0.0.1:8000"

def call_tool(tool_name, input_text):
    try:
        payload = {"tool": tool_name, "input": input_text}
        response = requests.post(f"{MCP_URL}/call_tool", json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("result", "")
        return f"Error: HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to MCP server. Make sure it's running on port 8000."
    except Exception as e:
        return f"Error: {e}"

def test_connection():
    try:
        r = requests.get(f"{MCP_URL}/tools", timeout=5)
        return r.status_code == 200
    except:
        return False

# ---------------- HELPER FUNCTIONS ----------------
def get_aqi_text(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

def format_carbon_response(text):
    if not text:
        return text
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('==='):
            line = re.sub(r'^#+\s*(.*?)$', r'<strong>\1</strong>', line)
            cleaned_lines.append(line)
    inner_html = '<br>'.join(cleaned_lines)
    return f'<div class="carbon-result" style="font-size:0.95rem; line-height:1.7;">{inner_html}</div>'

def format_pollution_response(text):
    if not text:
        return text
    aqi_match = re.search(r'AQI:\s*(\d+)', text)
    if aqi_match:
        aqi = int(aqi_match.group(1))
        aqi_category = get_aqi_text(aqi)
        if aqi <= 50:
            bar_color = "#4CAF50"
        elif aqi <= 100:
            bar_color = "#FFC107"
        elif aqi <= 150:
            bar_color = "#FF9800"
        elif aqi <= 200:
            bar_color = "#F44336"
        elif aqi <= 300:
            bar_color = "#9C27B0"
        else:
            bar_color = "#000000"
        fill_percent = min(100, (aqi / 300) * 100)
        pm25_match = re.search(r'PM2\.5:\s*(\d+)', text)
        pm10_match = re.search(r'PM10:\s*(\d+)', text)
        result = f"""
**Air Quality Index**

| Metric | Value |
|--------|-------|
| AQI | {aqi} ({aqi_category}) |
"""
        if pm25_match:
            result += f"| PM2.5 | {pm25_match.group(1)} μg/m³ |\n"
        if pm10_match:
            result += f"| PM10 | {pm10_match.group(1)} μg/m³ |\n"
        result += f"""
**Visual Indicator**

<div style="background-color: #e0e0e0; border-radius: 10px; height: 10px; width: 100%; margin: 10px 0;">
    <div style="background-color: {bar_color}; width: {fill_percent}%; height: 10px; border-radius: 10px;"></div>
</div>

**AQI Reference:** 0-50 Good (Green) | 51-100 Moderate (Yellow) | 101-150 Sensitive (Orange) | 151-200 Unhealthy (Red) | 201-300 Very Unhealthy (Purple) | 300+ Hazardous (Black)
"""
        return result
    return text

# ---------------- ROUTER ----------------
def route_query(query):
    q = query.lower()
    
    # 1. HEALTH EFFECTS - MUST BE FIRST
    if any(word in q for word in ['health', 'effect', 'disease', 'respiratory', 'cancer', 'asthma', 'toxic']):
        return call_tool("Environmental_Effects_RAG", query)
    
    # 2. CARBON FOOTPRINT (single city)
    if any(word in q for word in ['carbon', 'footprint', 'co2', 'emission']) and 'compare' not in q:
        result = call_tool("Carbon_Footprint_Calculator", query)
        return format_carbon_response(result)
    
    # 3. COMPARISON (handles both pollution and carbon)
    if 'compare' in q or ' vs ' in q:
        is_carbon = any(word in q for word in ['carbon', 'footprint', 'co2'])
        
        cities = ['delhi', 'mumbai', 'chennai', 'london', 'new york', 'tokyo', 'beijing', 'paris']
        found = [c for c in cities if c in q]
        if len(found) < 2:
            found = ['delhi', 'mumbai']
        
        card_parts = []
        title = "Carbon Footprint Comparison" if is_carbon else "Air Quality Comparison"
        
        for city in found:
            if is_carbon:
                data = call_tool("Carbon_Footprint_Calculator", city)
                if data:
                    carbon_match = re.search(r'(\d+\.?\d*)\s*tons', data)
                    if carbon_match:
                        carbon_value = float(carbon_match.group(1))
                        
                        if carbon_value <= 2.0:
                            bg_color = "#4CAF50"
                            label = "Low Impact"
                        elif carbon_value <= 5.0:
                            bg_color = "#FFC107"
                            label = "Moderate Impact"
                        else:
                            bg_color = "#F44336"
                            label = "High Impact"
                        
                        card_parts.append(f"""
<div style="background:white; border-radius:10px; padding:15px; margin:10px;
     width:200px; box-shadow:0 2px 5px rgba(0,0,0,0.1); text-align:center;
     border-top:5px solid {bg_color}; display:inline-block;">
  <h3 style="margin:0 0 10px 0; color:#333; font-size:1rem;">{city.upper()}</h3>
  <div style="font-size:1.5rem; font-weight:bold; color:{bg_color};">{carbon_value}</div>
  <div style="font-size:0.85rem; color:#666;">tons CO2/year</div>
  <div style="background-color:{bg_color}; color:white; padding:5px; border-radius:20px;
       margin-top:10px; font-size:0.8rem;">{label}</div>
  <div style="margin-top:10px; font-size:0.7rem; color:#666;">
    Carbon Reference: Low &lt;2.0, Moderate 2–5, High &gt;5 tons CO2/year
  </div>
</div>""")
            else:
                data = call_tool("Pollution_Health_Index", city)
                if data:
                    aqi_match = re.search(r'AQI:\s*(\d+)', data)
                    if aqi_match:
                        aqi = int(aqi_match.group(1))
                        
                        if aqi <= 50:
                            bg_color = "#4CAF50"
                            text_color = "white"
                            label = "Good"
                        elif aqi <= 100:
                            bg_color = "#FFC107"
                            text_color = "black"
                            label = "Moderate"
                        elif aqi <= 150:
                            bg_color = "#FF9800"
                            text_color = "white"
                            label = "Unhealthy for Sensitive Groups"
                        elif aqi <= 200:
                            bg_color = "#F44336"
                            text_color = "white"
                            label = "Unhealthy"
                        elif aqi <= 300:
                            bg_color = "#9C27B0"
                            text_color = "white"
                            label = "Very Unhealthy"
                        else:
                            bg_color = "#000000"
                            text_color = "white"
                            label = "Hazardous"
                        
                        card_parts.append(f"""
<div style="background:white; border-radius:10px; padding:15px; margin:10px;
     width:200px; box-shadow:0 2px 5px rgba(0,0,0,0.1); text-align:center;
     border-top:5px solid {bg_color}; display:inline-block;">
  <h3 style="margin:0 0 10px 0; color:#333; font-size:1rem;">{city.upper()}</h3>
  <div style="font-size:1.5rem; font-weight:bold; color:{bg_color};">{aqi}</div>
  <div style="background-color:{bg_color}; color:{text_color}; padding:5px; border-radius:20px;
       margin-top:10px; font-size:0.8rem;">{label}</div>
  <div style="margin-top:10px; font-size:0.7rem; color:#666;">
    AQI Range: 0–50 Good, 51–100 Moderate, 101–150 Sensitive,
    151–200 Unhealthy, 201–300 Very Unhealthy, 300+ Hazardous
  </div>
</div>""")
        
        if card_parts:
            cards_html = "\n".join(card_parts)
            full_html = f"""<div style="text-align:center; margin:20px 0;">
  <h2 style="color:#2E7D32; margin-bottom:20px;">{title}</h2>
  <div style="display:flex; flex-wrap:wrap; justify-content:center; gap:10px;">
    {cards_html}
  </div>
</div>"""
            return full_html
        
        return f"No comparison data available for {', '.join(found).upper()}."
    
    # 4. POLLUTION / AQI
    if any(word in q for word in ['pollution', 'aqi', 'air quality', 'pollution index']):
        result = call_tool("Pollution_Health_Index", query)
        return format_pollution_response(result)
    
    # 5. POLICIES
    if any(word in q for word in ['policy', 'act', 'law', 'treaty', 'agreement']):
        return call_tool("Environmental_Policies_RAG", query)
    
    # 6. SUSTAINABILITY TIPS
    if any(word in q for word in ['tip', 'advice', 'sustainable', 'recycle', 'home']):
        return call_tool("Sustainability_Tips", query)
    
    # 7. WEB SEARCH FALLBACK
    return call_tool("Web_Search", query)

# ---------------- UI ----------------
# Header
st.markdown("""
<div class="main-header">
    <h1>GreenMind</h1>
    <h3>Your Environmental Sustainability Advisor</h3>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("About GreenMind")
    st.markdown("Environmental sustainability advisor for:")
    st.markdown("- Policies and Regulations")
    st.markdown("- Pollution Index (AQI)")
    st.markdown("- Carbon Footprint")
    st.markdown("- Health Effects")
    st.markdown("- Climate Impacts")
    st.markdown("- City Comparisons")
    st.markdown("- Sustainability Tips")
    
    st.markdown("---")
    st.subheader("MCP Server Status")
    
    if test_connection():
        st.markdown('<div class="status-box connected">MCP Server Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box disconnected">MCP Server Disconnected</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Welcome message with quote
if not st.session_state.messages:
    quotes = [
        {"text": "The earth is what we all have in common.", "author": "Wendell Berry"},
        {"text": "We borrow the earth from our children.", "author": "Native American Proverb"},
        {"text": "The greatest threat is believing someone else will save it.", "author": "Robert Swan"}
    ]
    today_quote = quotes[datetime.now().day % len(quotes)]
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"""
<div class="elegant-quote">
    <div class="quote-text">"{today_quote['text']}"</div>
    <div class="quote-author">— {today_quote['author']}</div>
</div>

Hello! I'm GreenMind.

Ask me about:
- **Pollution Index** (AQI) - "what is the pollution index of delhi"
- **Carbon Footprint** - "carbon footprint of mumbai"
- **Health Effects** - "health effects of plastic pollution"
- **Environmental Policies** - "Paris Agreement"
- **Sustainability Tips** - "sustainability tips for home"
- **Comparisons** - "compare pollution in delhi and mumbai"

How can I help protect our planet today?
"""
    })

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# Chat input
prompt = st.chat_input("Ask me about environmental sustainability...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("GreenMind is thinking..."):
            response = route_query(prompt)
            st.markdown(response, unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Footer
st.markdown("""
<div class="footer">
    GreenMind - Every small action counts towards a greener planet
</div>
""", unsafe_allow_html=True)