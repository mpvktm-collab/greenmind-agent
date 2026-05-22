# app.py - GreenMind for Render deployment
 
import streamlit as st
import requests
import re
import os
from datetime import datetime
 
# ── Session ──────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
 
st.set_page_config(page_title="GreenMind - Environmental Advisor", layout="wide")
 
# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    header[data-testid="stHeader"] { display: none; }
 
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@300;400&display=swap');
 
    .main-header {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #4CAF50 100%);
        padding: 1rem 1rem 0.9rem 1rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        position: sticky;
        top: 0;
        z-index: 999;
        box-shadow: 0 4px 16px rgba(0,0,0,0.18);
    }
    .main-header .brand {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.4rem;
        margin-bottom: 0.2rem;
    }
    .main-header .leaf { font-size: 1.7rem; line-height: 1; }
    .main-header h1 {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        margin: 0;
        color: #ffffff;
        text-shadow: 1px 2px 8px rgba(0,0,0,0.25);
    }
    .main-header .tagline {
        font-family: 'Lato', sans-serif;
        font-size: 0.75rem;
        font-weight: 300;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: rgba(255,255,255,0.80);
        margin: 0;
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
    .connected    { background-color: #d4edda; color: #155724; }
    .disconnected { background-color: #f8d7da; color: #721c24; }
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
    .quote-text   { font-size: 1.1rem; font-style: italic; color: #1B5E20; }
    .quote-author { font-size: 0.8rem; color: #2E7D32; text-align: right; margin-top: 0.5rem; }
 
    .carbon-result { font-size: 0.95rem !important; line-height: 1.6; }
    .carbon-result h1, .carbon-result h2, .carbon-result h3 {
        font-size: 1rem !important; font-weight: bold; margin: 0.4rem 0;
    }
    .tips-result { font-size: 0.95rem; line-height: 1.8; }
    .tips-result .tips-heading {
        font-size: 1rem; font-weight: bold; color: #2E7D32;
        margin: 0.6rem 0 0.3rem 0;
        border-bottom: 1px solid #c8e6c9;
        padding-bottom: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)
 
# ── MCP config ────────────────────────────────────────────────────────────────
MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000")
DEBUG   = os.getenv("GREENMIND_DEBUG", "false").lower() == "true"
 
 
def call_tool(tool_name, input_text):
    if DEBUG:
        print(f"[GreenMind] tool={tool_name!r} input={input_text!r}")
    try:
        payload  = {"tool": tool_name, "input": input_text}
        response = requests.post(f"{MCP_URL}/call_tool", json=payload, timeout=90)
        if DEBUG:
            print(f"[GreenMind] HTTP {response.status_code}")
        if response.status_code == 200:
            return response.json().get("result", "")
        return None
    except Exception as exc:
        if DEBUG:
            print(f"[GreenMind] Error: {exc}")
        return None
 
 
def test_connection():
    try:
        r = requests.get(f"{MCP_URL}/tools", timeout=10)
        return r.status_code == 200
    except Exception:
        return False
 
 
# ── Helpers ───────────────────────────────────────────────────────────────────
def get_aqi_text(aqi):
    if aqi <= 50:  return "Good"
    if aqi <= 100: return "Moderate"
    if aqi <= 150: return "Unhealthy for Sensitive Groups"
    if aqi <= 200: return "Unhealthy"
    if aqi <= 300: return "Very Unhealthy"
    return "Hazardous"
 
 
# ── Formatters ────────────────────────────────────────────────────────────────
def format_carbon_response(text):
    if not text:
        return text
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('==='):
            line = re.sub(r'^#+\s*(.*?)$', r'<strong>\1</strong>', line)
            cleaned.append(line)
    inner = '<br>'.join(cleaned)
    return f'<div class="carbon-result" style="font-size:0.95rem; line-height:1.7;">{inner}</div>'
 
 
def format_sustainability_response(text):
    if not text:
        return text
    lines = text.split("\n")
    parts  = ['<div class="tips-result">']
    in_list = False
    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                parts.append("</ul>")
                in_list = False
            continue
        if re.match(r"^#{1,3}\s+", line):
            if in_list:
                parts.append("</ul>")
                in_list = False
            heading = re.sub(r"^#+\s+", "", line)
            parts.append(f'<div class="tips-heading">{heading}</div>')
        elif re.match(r"^[\*\-]\s+", line):
            if not in_list:
                parts.append('<ul style="margin:0.3rem 0 0.3rem 1.2rem;padding:0;">')
                in_list = True
            item = re.sub(r"^[\*\-]\s+", "", line)
            parts.append(f'<li style="margin-bottom:0.3rem;">{item}</li>')
        else:
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append(f'<p style="margin:0.3rem 0;">{line}</p>')
    if in_list:
        parts.append("</ul>")
    parts.append("</div>")
    return "".join(parts)
 
 
def format_pollution_response(text):
    if not text:
        return text
    aqi_match = re.search(r'AQI:\s*(\d+)', text)
    if aqi_match:
        aqi          = int(aqi_match.group(1))
        aqi_category = get_aqi_text(aqi)
        if aqi <= 50:   bar_color = "#4CAF50"
        elif aqi <= 100: bar_color = "#FFC107"
        elif aqi <= 150: bar_color = "#FF9800"
        elif aqi <= 200: bar_color = "#F44336"
        elif aqi <= 300: bar_color = "#9C27B0"
        else:            bar_color = "#000000"
        fill_percent = min(100, (aqi / 300) * 100)
        pm25_match   = re.search(r'PM2\.5:\s*(\d+)', text)
        pm10_match   = re.search(r'PM10:\s*(\d+)',   text)
        result  = f"**Air Quality Index**\n\n| Metric | Value |\n|--------|-------|\n"
        result += f"| AQI | {aqi} ({aqi_category}) |\n"
        if pm25_match:
            result += f"| PM2.5 | {pm25_match.group(1)} μg/m³ |\n"
        if pm10_match:
            result += f"| PM10  | {pm10_match.group(1)} μg/m³ |\n"
        result += (
            "\n**Visual Indicator**\n\n"
            f'<div style="background-color:#e0e0e0;border-radius:10px;height:10px;width:100%;margin:10px 0;">'
            f'<div style="background-color:{bar_color};width:{fill_percent}%;height:10px;border-radius:10px;"></div>'
            f'</div>\n\n'
            "**AQI Reference:** 0-50 Good (Green) | 51-100 Moderate (Yellow) | "
            "101-150 Sensitive (Orange) | 151-200 Unhealthy (Red) | "
            "201-300 Very Unhealthy (Purple) | 300+ Hazardous (Black)\n"
        )
        return result
    return text
 
 
# ── Comparison card builders (v1 style — inline HTML that Streamlit renders reliably) ──
def _aqi_color(aqi):
    if aqi <= 50:   return "#4CAF50", "white",  "Good"
    if aqi <= 100:  return "#FFC107", "black",  "Moderate"
    if aqi <= 150:  return "#FF9800", "white",  "Unhealthy for Sensitive Groups"
    if aqi <= 200:  return "#F44336", "white",  "Unhealthy"
    if aqi <= 300:  return "#9C27B0", "white",  "Very Unhealthy"
    return "#000000", "white", "Hazardous"
 
 
def build_aqi_card(city, data):
    """Returns a self-contained inline-styled card exactly like v1."""
    aqi_match = re.search(r'AQI:\s*(\d+)', data) if data else None
    if not aqi_match:
        return (
            f'<div style="background:white;border-radius:10px;padding:15px;margin:10px;'
            f'width:200px;box-shadow:0 2px 5px rgba(0,0,0,0.1);text-align:center;'
            f'border-top:5px solid #9e9e9e;display:inline-block;">'
            f'<h3 style="margin:0 0 10px 0;color:#333;font-size:1rem;">{city.upper()}</h3>'
            f'<div style="color:#666;font-size:0.85rem;">Data unavailable</div>'
            f'</div>'
        )
    aqi = int(aqi_match.group(1))
    bg_color, text_color, label = _aqi_color(aqi)
    return (
        f'<div style="background:white;border-radius:10px;padding:15px;margin:10px;'
        f'width:200px;box-shadow:0 2px 5px rgba(0,0,0,0.1);text-align:center;'
        f'border-top:5px solid {bg_color};display:inline-block;">'
        f'<h3 style="margin:0 0 10px 0;color:#333;font-size:1rem;">{city.upper()}</h3>'
        f'<div style="font-size:1.5rem;font-weight:bold;color:{bg_color};">{aqi}</div>'
        f'<div style="background-color:{bg_color};color:{text_color};padding:5px;'
        f'border-radius:20px;margin-top:10px;font-size:0.8rem;">{label}</div>'
        f'<div style="margin-top:10px;font-size:0.7rem;color:#666;">'
        f'AQI: 0-50 Good | 51-100 Moderate | 101-150 Sensitive<br>'
        f'151-200 Unhealthy | 201-300 Very Unhealthy | 300+ Hazardous'
        f'</div>'
        f'</div>'
    )
 
 
def build_carbon_card(city, data):
    """Returns a self-contained inline-styled card exactly like v1."""
    carbon_match = re.search(r'(\d+\.?\d*)\s*tons', data) if data else None
    if not carbon_match:
        return (
            f'<div style="background:white;border-radius:10px;padding:15px;margin:10px;'
            f'width:200px;box-shadow:0 2px 5px rgba(0,0,0,0.1);text-align:center;'
            f'border-top:5px solid #9e9e9e;display:inline-block;">'
            f'<h3 style="margin:0 0 10px 0;color:#333;font-size:1rem;">{city.upper()}</h3>'
            f'<div style="color:#666;font-size:0.85rem;">Data unavailable</div>'
            f'</div>'
        )
    carbon_value = float(carbon_match.group(1))
    if carbon_value <= 2.0:
        bg_color, label = "#4CAF50", "Low Impact"
    elif carbon_value <= 5.0:
        bg_color, label = "#FFC107", "Moderate Impact"
    else:
        bg_color, label = "#F44336", "High Impact"
    return (
        f'<div style="background:white;border-radius:10px;padding:15px;margin:10px;'
        f'width:200px;box-shadow:0 2px 5px rgba(0,0,0,0.1);text-align:center;'
        f'border-top:5px solid {bg_color};display:inline-block;">'
        f'<h3 style="margin:0 0 10px 0;color:#333;font-size:1rem;">{city.upper()}</h3>'
        f'<div style="font-size:1.5rem;font-weight:bold;color:{bg_color};">{carbon_value}</div>'
        f'<div style="font-size:0.85rem;color:#666;">tons CO2/year</div>'
        f'<div style="background-color:{bg_color};color:white;padding:5px;border-radius:20px;'
        f'margin-top:10px;font-size:0.8rem;">{label}</div>'
        f'<div style="margin-top:10px;font-size:0.7rem;color:#666;">'
        f'Low &lt;2.0 | Moderate 2-5 | High &gt;5 tons CO2/year'
        f'</div>'
        f'</div>'
    )
 
 
# ── Sustainability keyword lists ───────────────────────────────────────────────
KNOWN_CITIES = [
    "delhi", "mumbai", "chennai", "kolkata",
    "london", "new york", "tokyo", "beijing", "paris",
]
 
SUSTAINABILITY_WORDS = [
    "tip", "advice", "sustainable", "recycle", "home", "house",
    "transport", "transportation", "travel", "commute", "bicycle", "bike",
    "cycling", "walk", "bus", "train", "metro", "carpool", "flight", "aviation",
    "eco", "eco-friendly", "zero waste", "energy", "solar", "renewable",
    "plastic", "reduce", "reuse", "compost", "sustainable living", "electric vehicle",
]
 
SUSTAINABILITY_PHRASES = [
    "water saving", "public transit", "how can i reduce", "how to reduce",
    "reduce my carbon", "lower my carbon", "carbon footprint reduction",
    "ways to reduce", "tips to reduce", "how can i lower", "reduce my footprint",
]
 
SUSTAINABILITY_QUERY_MAP = [
    (
        ["how can i reduce", "how to reduce", "reduce my carbon",
         "lower my carbon", "reduce my footprint", "ways to reduce",
         "tips to reduce", "carbon footprint reduction"],
        "general tips to reduce carbon footprint at home and daily life",
    ),
    (["recycle", "zero waste", "reuse", "compost", "plastic"],
     "tips for recycling and reducing waste at home"),
    (["solar", "renewable", "energy"],
     "tips for using renewable energy and saving electricity at home"),
    (["water saving"],
     "tips for saving water at home"),
]
 
 
def is_sustainability_query(q):
    for phrase in SUSTAINABILITY_PHRASES:
        if phrase in q:
            return True
    for word in SUSTAINABILITY_WORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", q):
            return True
    return False
 
 
def resolve_sustainability_query(q, original):
    for triggers, rewritten in SUSTAINABILITY_QUERY_MAP:
        for trigger in triggers:
            if trigger in q:
                return rewritten
    return original
 
 
# ── Router ────────────────────────────────────────────────────────────────────
def route_query(query):
    q = query.lower()
 
    # 1. HEALTH EFFECTS
    if any(w in q for w in ["health", "effect", "disease", "respiratory",
                             "cancer", "asthma", "toxic", "pm2.5"]):
        result = call_tool("Environmental_Effects_RAG", query)
        return result if result else "No health effects information found."
 
    # 2. Detect cities
    cities_found  = list(dict.fromkeys(c for c in KNOWN_CITIES if c in q))
    is_multi_city = len(cities_found) >= 2
 
    # 3. COMPARISON
    if "compare" in q or " vs " in q or is_multi_city:
        is_carbon = any(w in q for w in ["carbon", "footprint", "co2", "emission"])
        found     = cities_found[:2]
 
        if len(found) < 2:
            listed = ", ".join(found) if found else "none"
            return (
                f"Please specify two cities to compare. Detected: {listed}. "
                "Try: 'compare pollution index of Delhi and Mumbai'."
            )
 
        title      = "Carbon Footprint Comparison" if is_carbon else "Air Quality Comparison"
        cards_html = ""
        for city in found:
            if is_carbon:
                data = call_tool("Carbon_Footprint_Calculator", city)
                cards_html += build_carbon_card(city, data)
            else:
                data = call_tool("Pollution_Health_Index", city)
                cards_html += build_aqi_card(city, data)
 
        if cards_html:
            return (
                f'<div style="text-align:center;margin:20px 0;font-family:sans-serif;">'
                f'<div style="color:#2E7D32;margin-bottom:16px;font-size:1rem;'
                f'font-weight:700;letter-spacing:0.03em;">{title}</div>'
                f'<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:10px;">'
                f'{cards_html}'
                f'</div>'
                f'</div>'
            )
        return f"No comparison data available for {', '.join(found).upper()}."
 
    # 4. SUSTAINABILITY TIPS
    if is_sustainability_query(q):
        clean_q = resolve_sustainability_query(q, query)
        result  = call_tool("Sustainability_Tips", clean_q)
        return format_sustainability_response(result) if result else "No sustainability tips found."
 
    # 5. CARBON FOOTPRINT (single city)
    if any(w in q for w in ["carbon", "footprint", "co2", "emission"]):
        result = call_tool("Carbon_Footprint_Calculator", query)
        return format_carbon_response(result) if result else "No carbon footprint data found."
 
    # 6. POLLUTION / AQI
    if any(w in q for w in ["pollution", "aqi", "air quality", "pollution index"]):
        result = call_tool("Pollution_Health_Index", query)
        return format_pollution_response(result) if result else "No pollution data found."
 
    # 7. POLICIES
    if any(w in q for w in ["policy", "act", "law", "treaty",
                             "agreement", "regulation", "protocol"]):
        result = call_tool("Environmental_Policies_RAG", query)
        return result if (result and len(result) > 50) else "No policy information found."
 
    # 8. WEB SEARCH FALLBACK
    result = call_tool("Web_Search", query)
    return result if result else "No information found. Please try a different query."
 
 
# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div class="brand">
        <span class="leaf">🌿</span>
        <h1>GreenMind</h1>
    </div>
    <p class="tagline">Your Environmental Sustainability Advisor</p>
</div>
""", unsafe_allow_html=True)
 
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
        st.markdown('<div class="status-box connected">MCP Server Connected</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box disconnected">MCP Server Disconnected</div>',
                    unsafe_allow_html=True)
    st.markdown("---")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
 
if not st.session_state.messages:
    quotes = [
        {"text": "The earth is what we all have in common.",              "author": "Wendell Berry"},
        {"text": "We borrow the earth from our children.",                "author": "Native American Proverb"},
        {"text": "The greatest threat is believing someone else will save it.", "author": "Robert Swan"},
    ]
    today_quote = quotes[datetime.now().day % len(quotes)]
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            f'<div class="elegant-quote">'
            f'<div class="quote-text">"{today_quote["text"]}"</div>'
            f'<div class="quote-author">— {today_quote["author"]}</div>'
            f'</div>\n\n'
            "Hello! I'm **GreenMind** 🌍 — how can I help protect our planet today?"
        ),
    })
 
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)
 
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
 
st.markdown("""
<div class="footer">
    GreenMind - Every small action counts towards a greener planet
</div>
""", unsafe_allow_html=True)