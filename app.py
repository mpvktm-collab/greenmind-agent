# app.py - GreenMind Final Merged Version
# Combines the best of both versions:
#   - Fixed sticky/fixed header from v2
#   - Debug logging from v2 (can be toggled off in production)
#   - Cleaner card builders (separate functions) from v2
#   - format_sustainability_response from v2
#   - Smart sustainability keyword routing from v2
#   - format_pollution_response and format_carbon_response from v1/v2
#   - Robust router ordering from v2
#   - MCP_URL via env var from v2
#   - All CSS improvements merged
 
import streamlit as st
import requests
import re
import os
from datetime import datetime
 
# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
 
st.set_page_config(page_title="GreenMind - Environmental Advisor", layout="wide")
 
# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Hide default Streamlit header */
    header[data-testid="stHeader"] { display: none; }
 
    /* ── Fixed top banner ── */
    .main-header {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #4CAF50 100%);
        padding: 0.8rem;
        border-radius: 0 0 15px 15px;
        color: white;
        text-align: center;
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 999;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        width: 100%;
    }
    .main-header h1 {
        font-size: 1.8rem;
        margin-bottom: 0.2rem;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header h3 {
        font-size: 0.8rem;
        font-weight: 400;
        font-style: italic;
        margin-bottom: 0;
        background-color: rgba(0,0,0,0.25);
        display: inline-block;
        padding: 0.2rem 1rem;
        border-radius: 30px;
        color: #FFFFFF;
    }
 
    /* Push content below fixed header */
    .main-content { margin-top: 95px; padding: 0 1rem; }
 
    /* Sidebar offset */
    [data-testid="stSidebar"] { margin-top: 80px; }
 
    /* Chat bubbles */
    .stChatMessage {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 10px;
        margin: 8px 0;
        border: 1px solid #e0e0e0;
    }
 
    /* Chat input */
    .stChatInput textarea {
        font-size: 1rem !important;
        min-height: 60px !important;
        border-radius: 20px !important;
    }
 
    /* Status badges */
    .status-box {
        padding: 0.5rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        text-align: center;
        font-size: 0.85rem;
    }
    .connected    { background-color: #d4edda; color: #155724; }
    .disconnected { background-color: #f8d7da; color: #721c24; }
 
    /* Quote card */
    .elegant-quote {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 15px;
        text-align: center;
        border-left: 6px solid #2E7D32;
    }
    .quote-text   { font-size: 1rem;   font-style: italic; color: #1B5E20; }
    .quote-author { font-size: 0.75rem; color: #2E7D32; text-align: right; margin-top: 0.3rem; }
 
    /* Carbon output */
    .carbon-result { font-size: 0.95rem !important; line-height: 1.7; }
    .carbon-result h1,
    .carbon-result h2,
    .carbon-result h3 { font-size: 1rem !important; font-weight: bold; margin: 0.4rem 0; }
 
    /* Sustainability tips output */
    .tips-result { font-size: 0.95rem; line-height: 1.8; }
    .tips-result .tips-heading {
        font-size: 1rem;
        font-weight: bold;
        color: #2E7D32;
        margin: 0.6rem 0 0.3rem 0;
        border-bottom: 1px solid #c8e6c9;
        padding-bottom: 0.2rem;
    }
 
    /* Comparison cards */
    .comparison-container { text-align: center; margin: 16px 0; }
    .comparison-title {
        color: #2E7D32;
        margin-bottom: 14px;
        font-size: 0.95rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    .comparison-wrapper {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
    }
    .comparison-card {
        background: white;
        border-radius: 10px;
        padding: 12px 14px;
        width: 160px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        text-align: center;
        display: inline-block;
        font-size: 0.82rem;
    }
 
    /* Footer */
    .footer {
        text-align: center;
        color: #666;
        padding: 0.5rem;
        margin-top: 1rem;
        font-size: 0.7rem;
        border-top: 1px solid #e0e0e0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
 
# ─────────────────────────────────────────────
# MCP CONFIG
# ─────────────────────────────────────────────
MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000")
 
# Set DEBUG=True during development; False in production
DEBUG = os.getenv("GREENMIND_DEBUG", "false").lower() == "true"
 
 
def call_tool(tool_name: str, input_text: str):
    """POST a tool call to the MCP server and return the result string, or None on error."""
    if DEBUG:
        print(f"[GreenMind] call_tool → tool={tool_name!r}  input={input_text!r}")
    try:
        payload = {"tool": tool_name, "input": input_text}
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
 
 
def test_connection() -> bool:
    try:
        r = requests.get(f"{MCP_URL}/tools", timeout=10)
        return r.status_code == 200
    except Exception:
        return False
 
 
# ─────────────────────────────────────────────
# AQI HELPERS
# ─────────────────────────────────────────────
def get_aqi_label(aqi: int) -> str:
    if aqi <= 50:   return "Good"
    if aqi <= 100:  return "Moderate"
    if aqi <= 150:  return "Unhealthy for Sensitive Groups"
    if aqi <= 200:  return "Unhealthy"
    if aqi <= 300:  return "Very Unhealthy"
    return "Hazardous"
 
 
def get_aqi_color(aqi: int) -> str:
    if aqi <= 50:   return "#4CAF50"
    if aqi <= 100:  return "#FFC107"
    if aqi <= 150:  return "#FF9800"
    if aqi <= 200:  return "#F44336"
    if aqi <= 300:  return "#9C27B0"
    return "#000000"
 
 
# ─────────────────────────────────────────────
# FORMATTERS
# ─────────────────────────────────────────────
def format_carbon_response(text: str) -> str:
    """Render carbon tool output at a controlled font size (no giant h1/h2/h3)."""
    if not text:
        return text
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("==="):
            line = re.sub(r"^#+\s*(.*?)$", r"<strong>\1</strong>", line)
            cleaned.append(line)
    inner = "<br>".join(cleaned)
    return f'<div class="carbon-result" style="font-size:0.95rem;line-height:1.7;">{inner}</div>'
 
 
def format_sustainability_response(text: str) -> str:
    """
    Convert raw Markdown from the Sustainability_Tips tool into controlled HTML.
    Headings → small bold green labels; bullets → <ul>; plain text → <p>.
    """
    if not text:
        return text
    lines = text.split("\n")
    parts = ['<div class="tips-result">']
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
 
 
def format_pollution_response(text: str) -> str:
    """Format AQI tool output with a table and color-coded progress bar."""
    if not text:
        return text
    aqi_match = re.search(r"AQI:\s*(\d+)", text)
    if not aqi_match:
        return text
    aqi        = int(aqi_match.group(1))
    label      = get_aqi_label(aqi)
    bar_color  = get_aqi_color(aqi)
    fill_pct   = min(100, (aqi / 300) * 100)
    pm25_match = re.search(r"PM2\.5:\s*(\d+)", text)
    pm10_match = re.search(r"PM10:\s*(\d+)", text)
 
    result  = f"**Air Quality Index**\n\n| Metric | Value |\n|--------|-------|\n"
    result += f"| AQI | {aqi} ({label}) |\n"
    if pm25_match:
        result += f"| PM2.5 | {pm25_match.group(1)} μg/m³ |\n"
    if pm10_match:
        result += f"| PM10  | {pm10_match.group(1)} μg/m³ |\n"
    result += (
        "\n**Visual Indicator**\n\n"
        f'<div style="background-color:#e0e0e0;border-radius:10px;height:12px;width:100%;margin:10px 0;">'
        f'<div style="background-color:{bar_color};width:{fill_pct:.1f}%;height:12px;border-radius:10px;"></div>'
        f'</div>\n\n'
        "**AQI Reference:** "
        "0–50 Good (🟢) | 51–100 Moderate (🟡) | 101–150 Sensitive (🟠) | "
        "151–200 Unhealthy (🔴) | 201–300 Very Unhealthy (🟣) | 300+ Hazardous (⚫)\n"
    )
    return result
 
 
# ─────────────────────────────────────────────
# COMPARISON CARD BUILDERS
# All styles are 100% inline — no CSS classes — so Streamlit markdown
# rendering cannot override font sizes or layout.
# ─────────────────────────────────────────────
 
CARD_STYLE = (
    "display:inline-block;"
    "vertical-align:top;"
    "width:170px;"
    "background:#ffffff;"
    "border-radius:12px;"
    "padding:14px 12px 12px 12px;"
    "margin:6px;"
    "box-shadow:0 1px 6px rgba(0,0,0,0.10);"
    "text-align:center;"
    "font-family:sans-serif;"
    "font-size:12px;"          # base for everything inside the card
    "line-height:1.4;"
)
 
def _unavailable_card(city: str) -> str:
    return (
        f'<div style="{CARD_STYLE}border-top:4px solid #9e9e9e;">'
        f'<div style="font-size:11px;font-weight:700;letter-spacing:0.07em;'
        f'color:#777;text-transform:uppercase;margin-bottom:8px;">{city}</div>'
        f'<div style="color:#999;font-size:11px;">Data unavailable</div>'
        f'</div>'
    )
 
 
def build_carbon_card(city: str, data) -> str:
    if not data:
        return _unavailable_card(city)
    m = re.search(r"(\d+\.?\d*)\s*tons", data)
    if not m:
        return _unavailable_card(city)
 
    val = float(m.group(1))
    if val <= 2.0:
        color, label = "#4CAF50", "Low Impact"
    elif val <= 5.0:
        color, label = "#FFC107", "Moderate Impact"
    else:
        color, label = "#F44336", "High Impact"
    badge_text = "white" if label != "Moderate Impact" else "#333"
 
    return (
        f'<div style="{CARD_STYLE}border-top:4px solid {color};">'
        # city name
        f'<div style="font-size:11px;font-weight:700;letter-spacing:0.07em;'
        f'color:#555;text-transform:uppercase;margin-bottom:8px;">{city}</div>'
        # big number
        f'<div style="font-size:22px;font-weight:700;color:{color};'
        f'line-height:1.1;margin-bottom:2px;">{val}</div>'
        # unit
        f'<div style="font-size:10px;color:#999;margin-bottom:8px;">tons CO&#8322;/year</div>'
        # colour badge
        f'<div style="display:inline-block;background:{color};color:{badge_text};'
        f'font-size:10px;font-weight:600;padding:3px 10px;border-radius:20px;'
        f'margin-bottom:8px;">{label}</div>'
        # legend
        f'<div style="font-size:9px;color:#bbb;line-height:1.5;margin-top:4px;">'
        f'Low &lt;2 &nbsp;|&nbsp; Moderate 2–5 &nbsp;|&nbsp; High &gt;5 tons/yr</div>'
        f'</div>'
    )
 
 
def build_aqi_card(city: str, data) -> str:
    if not data:
        return _unavailable_card(city)
    # Accept "AQI: 123" or "AQI : 123" or plain integer on same line
    m = re.search(r"AQI\s*:\s*(\d+)", data, re.IGNORECASE)
    if not m:
        # fallback: grab first standalone number if tool returns bare value
        m = re.search(r"\b(\d{2,3})\b", data)
    if not m:
        return _unavailable_card(city)
 
    aqi        = int(m.group(1))
    color      = get_aqi_color(aqi)
    label      = get_aqi_label(aqi)
    badge_text = "black" if aqi <= 100 else "white"
 
    # optional PM values
    pm25_m = re.search(r"PM2\.5\s*:\s*(\d+\.?\d*)", data, re.IGNORECASE)
    pm10_m = re.search(r"PM10\s*:\s*(\d+\.?\d*)",  data, re.IGNORECASE)
    pm_rows = ""
    if pm25_m:
        pm_rows += (
            f'<div style="display:flex;justify-content:space-between;'
            f'font-size:10px;color:#777;padding:2px 0;border-bottom:1px solid #f0f0f0;">'
            f'<span>PM2.5</span><span style="font-weight:600;">{pm25_m.group(1)} µg/m³</span></div>'
        )
    if pm10_m:
        pm_rows += (
            f'<div style="display:flex;justify-content:space-between;'
            f'font-size:10px;color:#777;padding:2px 0;">'
            f'<span>PM10</span><span style="font-weight:600;">{pm10_m.group(1)} µg/m³</span></div>'
        )
    pm_section = (
        f'<div style="margin:6px 0 8px 0;text-align:left;">{pm_rows}</div>'
        if pm_rows else ""
    )
 
    # mini progress bar
    fill_pct = min(100, round(aqi / 300 * 100, 1))
    bar = (
        f'<div style="background:#eee;border-radius:6px;height:5px;width:100%;margin:6px 0 8px 0;">'
        f'<div style="background:{color};width:{fill_pct}%;height:5px;border-radius:6px;"></div>'
        f'</div>'
    )
 
    return (
        f'<div style="{CARD_STYLE}border-top:4px solid {color};">'
        # city name
        f'<div style="font-size:11px;font-weight:700;letter-spacing:0.07em;'
        f'color:#555;text-transform:uppercase;margin-bottom:8px;">{city}</div>'
        # AQI number
        f'<div style="font-size:28px;font-weight:700;color:{color};'
        f'line-height:1.1;margin-bottom:2px;">{aqi}</div>'
        f'<div style="font-size:10px;color:#999;margin-bottom:6px;">AQI</div>'
        # badge
        f'<div style="display:inline-block;background:{color};color:{badge_text};'
        f'font-size:10px;font-weight:600;padding:3px 10px;border-radius:20px;'
        f'margin-bottom:6px;">{label}</div>'
        # progress bar
        f'{bar}'
        # PM rows (if available)
        f'{pm_section}'
        # legend
        f'<div style="font-size:9px;color:#bbb;line-height:1.6;">'
        f'0–50 Good &nbsp;|&nbsp; 51–100 Moderate<br>'
        f'101–150 Sensitive &nbsp;|&nbsp; 151–200 Unhealthy<br>'
        f'201–300 Very Unhealthy &nbsp;|&nbsp; 300+ Hazardous'
        f'</div>'
        f'</div>'
    )
 
 
# ─────────────────────────────────────────────
# SUSTAINABILITY KEYWORD LISTS
# ─────────────────────────────────────────────
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
 
# Intent → rewritten query mapping for the Sustainability_Tips tool
SUSTAINABILITY_QUERY_MAP = [
    (
        ["how can i reduce", "how to reduce", "reduce my carbon",
         "lower my carbon", "reduce my footprint", "ways to reduce",
         "tips to reduce", "carbon footprint reduction"],
        "general tips to reduce carbon footprint at home and daily life",
    ),
    (
        ["recycle", "zero waste", "reuse", "compost", "plastic"],
        "tips for recycling and reducing waste at home",
    ),
    (
        ["solar", "renewable", "energy"],
        "tips for using renewable energy and saving electricity at home",
    ),
    (
        ["water saving"],
        "tips for saving water at home",
    ),
]
 
 
def is_sustainability_query(q: str) -> bool:
    for phrase in SUSTAINABILITY_PHRASES:
        if phrase in q:
            return True
    for word in SUSTAINABILITY_WORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", q):
            return True
    return False
 
 
def resolve_sustainability_query(q: str, original: str) -> str:
    """Return a clean explicit query for the Sustainability_Tips tool."""
    for triggers, rewritten in SUSTAINABILITY_QUERY_MAP:
        for trigger in triggers:
            if trigger in q:
                return rewritten
    return original
 
 
# ─────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────
def route_query(query: str) -> str:
    q = query.lower()
 
    # 1. HEALTH EFFECTS  (highest priority – check before anything else)
    if any(w in q for w in ["health", "effect", "disease", "respiratory",
                             "cancer", "asthma", "toxic", "pm2.5"]):
        result = call_tool("Environmental_Effects_RAG", query)
        return result if result else "No health effects information found in the knowledge base."
 
    # 2. DETECT MULTI-CITY (order-preserving, deduped)
    cities_found = list(dict.fromkeys(c for c in KNOWN_CITIES if c in q))
    is_multi_city = len(cities_found) >= 2
 
    # 3. COMPARISON  (before sustainability to avoid misrouting)
    if "compare" in q or " vs " in q or is_multi_city:
        is_carbon = any(w in q for w in ["carbon", "footprint", "co2", "emission"])
        found = cities_found[:2]
 
        if len(found) < 2:
            listed = ", ".join(found) if found else "none"
            return (
                f"Please specify two cities to compare. Detected: {listed}. "
                "Try: 'compare AQI of Delhi and Mumbai'."
            )
 
        title     = "Carbon Footprint Comparison" if is_carbon else "Air Quality Comparison"
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
                '<div style="text-align:center;margin:12px 0;font-family:sans-serif;">'
                f'<div style="font-size:11px;font-weight:700;letter-spacing:0.08em;'
                f'text-transform:uppercase;color:#2E7D32;margin-bottom:12px;">{title}</div>'
                '<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:4px;">'
                f'{cards_html}'
                '</div></div>'
            )
        return f"No comparison data available for {', '.join(found).upper()}."
 
    # 4. SUSTAINABILITY TIPS
    if is_sustainability_query(q):
        clean_q = resolve_sustainability_query(q, query)
        result  = call_tool("Sustainability_Tips", clean_q)
        return format_sustainability_response(result) if result else "No sustainability tips found."
 
    # 5. CARBON FOOTPRINT  (single city)
    if any(w in q for w in ["carbon", "footprint", "co2", "emission"]):
        result = call_tool("Carbon_Footprint_Calculator", query)
        return format_carbon_response(result) if result else "No carbon footprint data found."
 
    # 6. POLLUTION / AQI
    if any(w in q for w in ["pollution", "aqi", "air quality", "pollution index"]):
        result = call_tool("Pollution_Health_Index", query)
        return format_pollution_response(result) if result else "No pollution data found."
 
    # 7. POLICIES & REGULATIONS
    if any(w in q for w in ["policy", "act", "law", "treaty",
                             "agreement", "regulation", "protocol"]):
        result = call_tool("Environmental_Policies_RAG", query)
        return result if (result and len(result) > 50) else "No policy information found."
 
    # 8. WEB SEARCH FALLBACK
    result = call_tool("Web_Search", query)
    return result if result else "No information found. Please try a different query."
 
 
# ─────────────────────────────────────────────
# UI — HEADER
# ─────────────────────────────────────────────
st.markdown(
    '<div class="main-header">'
    '<h1>🌿 GreenMind</h1>'
    '<h3>Your Environmental Sustainability Advisor</h3>'
    '</div>',
    unsafe_allow_html=True,
)
 
st.markdown('<div class="main-content">', unsafe_allow_html=True)
 
# ─────────────────────────────────────────────
# UI — SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("About GreenMind")
    st.markdown(
        "Environmental sustainability advisor for:\n"
        "- Policies & Regulations\n"
        "- Pollution Index (AQI)\n"
        "- Carbon Footprint\n"
        "- Health Effects\n"
        "- Climate Impacts\n"
        "- City Comparisons\n"
        "- Sustainability Tips\n"
    )
    st.markdown("---")
    st.subheader("MCP Server Status")
    if test_connection():
        st.markdown(
            '<div class="status-box connected">✅ MCP Server Connected</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-box disconnected">❌ MCP Server Disconnected</div>',
            unsafe_allow_html=True,
        )
    st.markdown("---")
    st.markdown("**Example queries:**")
    st.markdown(
        "- *What is the AQI of Delhi?*\n"
        "- *Carbon footprint of Mumbai*\n"
        "- *Health effects of plastic pollution*\n"
        "- *Compare air quality Delhi vs London*\n"
        "- *Paris Agreement*\n"
        "- *Tips to reduce my carbon footprint*\n"
    )
    st.markdown("---")
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
 
# ─────────────────────────────────────────────
# UI — WELCOME MESSAGE
# ─────────────────────────────────────────────
if not st.session_state.messages:
    quotes = [
        {"text": "The earth is what we all have in common.", "author": "Wendell Berry"},
        {"text": "We borrow the earth from our children.", "author": "Native American Proverb"},
        {"text": "The greatest threat is believing someone else will save it.", "author": "Robert Swan"},
    ]
    q = quotes[datetime.now().day % len(quotes)]
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": (
                '<div class="elegant-quote">'
                f'<div class="quote-text">"{q["text"]}"</div>'
                f'<div class="quote-author">— {q["author"]}</div>'
                "</div>\n\n"
                "Hello! I'm **GreenMind** 🌍\n\n"
                "Ask me about **AQI**, **carbon footprint**, **health effects**, "
                "**environmental policies**, **city comparisons**, or **sustainability tips**.\n\n"
                "How can I help protect our planet today?"
            ),
        }
    )
 
# ─────────────────────────────────────────────
# UI — CHAT HISTORY
# ─────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)
 
# ─────────────────────────────────────────────
# UI — CHAT INPUT
# ─────────────────────────────────────────────
prompt = st.chat_input("Ask me about environmental sustainability...")
 
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("GreenMind is thinking…"):
            response = route_query(prompt)
            st.markdown(response, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
 
st.markdown("</div>", unsafe_allow_html=True)
 
# ─────────────────────────────────────────────
# UI — FOOTER
# ─────────────────────────────────────────────
st.markdown(
    '<div class="footer">🌱 GreenMind — Every small action counts towards a greener planet</div>',
    unsafe_allow_html=True,
)
 