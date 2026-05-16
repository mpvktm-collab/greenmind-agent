# app.py - Final Version with Fixed Sustainability Tips Routing
import streamlit as st
import requests
import re
import os

from datetime import datetime

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="GreenMind - Environmental Advisor", layout="wide")

# ---------------- CSS ----------------
st.markdown(
    """
    <style>
    header[data-testid="stHeader"] {
        display: none;
    }
    .main-header {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #4CAF50 100%);
        padding: 0.8rem;
        border-radius: 0 0 15px 15px;
        color: white;
        text-align: center;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        width: 100%;
    }
    .main-header h1 {
        font-size: 1.6rem;
        margin-bottom: 0.2rem;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header h3 {
        font-size: 0.75rem;
        font-weight: 400;
        font-style: italic;
        margin-bottom: 0;
        background-color: rgba(0,0,0,0.25);
        display: inline-block;
        padding: 0.2rem 1rem;
        border-radius: 30px;
        color: #FFFFFF;
    }
    .main-content {
        margin-top: 90px;
        padding: 0 1rem;
    }
    .stChatMessage {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 10px;
        margin: 8px 0;
        border: 1px solid #e0e0e0;
    }
    .stChatInput textarea {
        font-size: 1rem !important;
        min-height: 60px !important;
        border-radius: 20px !important;
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
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 15px;
        text-align: center;
        border-left: 6px solid #2E7D32;
    }
    .quote-text {
        font-size: 1rem;
        font-style: italic;
        color: #1B5E20;
    }
    .quote-author {
        font-size: 0.75rem;
        color: #2E7D32;
        text-align: right;
        margin-top: 0.3rem;
    }
    .carbon-result {
        font-size: 0.95rem !important;
        line-height: 1.7;
    }
    .carbon-result h1, .carbon-result h2, .carbon-result h3 {
        font-size: 1rem !important;
        font-weight: bold;
        margin: 0.4rem 0;
    }
    .tips-result {
        font-size: 0.95rem;
        line-height: 1.8;
    }
    .tips-result .tips-heading {
        font-size: 1rem;
        font-weight: bold;
        color: #2E7D32;
        margin: 0.6rem 0 0.3rem 0;
        border-bottom: 1px solid #c8e6c9;
        padding-bottom: 0.2rem;
    }
    [data-testid="stSidebar"] {
        margin-top: 80px;
    }
    .comparison-container {
        text-align: center;
        margin: 20px 0;
    }
    .comparison-title {
        color: #2E7D32;
        margin-bottom: 20px;
        font-size: 1.5rem;
        font-weight: bold;
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
        padding: 15px;
        margin: 10px;
        width: 200px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        text-align: center;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- MCP CONFIG ----------------
# This will use the environment variable if set, otherwise use localhost for testing
MCP_URL = os.getenv("MCP_URL", "http://127.0.0.1:8000")


def call_tool(tool_name, input_text):
    try:
        payload = {"tool": tool_name, "input": input_text}
        response = requests.post(f"{MCP_URL}/call_tool", json=payload, timeout=90)
        if response.status_code == 200:
            return response.json().get("result", "")
        return None
    except:
        return None


def test_connection():
    try:
        r = requests.get(f"{MCP_URL}/tools", timeout=10)
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
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("==="):
            line = re.sub(r"^#+\s*(.*?)$", r"<strong>\1</strong>", line)
            cleaned_lines.append(line)
    inner_html = "<br>".join(cleaned_lines)
    return '<div class="carbon-result" style="font-size:0.95rem; line-height:1.7;">' + inner_html + "</div>"


def format_sustainability_response(text):
    """
    Converts the raw tool output into controlled HTML so that
    headings never render at browser h1/h2/h3 size.
    - Lines starting with # / ## / ### become small bold green labels.
    - Bullet lines (* or -) become list items.
    - Plain lines become paragraphs.
    """
    if not text:
        return text
    lines = text.split("\n")
    html_parts = ['<div class="tips-result">']
    in_list = False
    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            continue
        # Heading lines - render as small bold label, never as h1/h2/h3
        if re.match(r"^#{1,3}\s+", line):
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            heading_text = re.sub(r"^#+\s+", "", line)
            html_parts.append('<div class="tips-heading">' + heading_text + "</div>")
        # Bullet lines
        elif re.match(r"^[\*\-]\s+", line):
            if not in_list:
                html_parts.append('<ul style="margin:0.3rem 0 0.3rem 1.2rem;padding:0;">')
                in_list = True
            item_text = re.sub(r"^[\*\-]\s+", "", line)
            html_parts.append('<li style="margin-bottom:0.3rem;">' + item_text + "</li>")
        # Plain text
        else:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append('<p style="margin:0.3rem 0;">' + line + "</p>")
    if in_list:
        html_parts.append("</ul>")
    html_parts.append("</div>")
    return "".join(html_parts)


def format_pollution_response(text):
    if not text:
        return text
    aqi_match = re.search(r"AQI:\s*(\d+)", text)
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
        pm25_match = re.search(r"PM2\.5:\s*(\d+)", text)
        pm10_match = re.search(r"PM10:\s*(\d+)", text)
        result = "**Air Quality Index**\n\n| Metric | Value |\n|--------|-------|\n"
        result += "| AQI | " + str(aqi) + " (" + aqi_category + ") |\n"
        if pm25_match:
            result += "| PM2.5 | " + pm25_match.group(1) + " microg/m^3 |\n"
        if pm10_match:
            result += "| PM10 | " + pm10_match.group(1) + " microg/m^3 |\n"
        result += (
            "\n**Visual Indicator**\n\n"
            '<div style="background-color:#e0e0e0; border-radius:10px; height:10px; width:100%; margin:10px 0;">'
            '<div style="background-color:' + bar_color + '; width:' + str(fill_percent) + '%; height:10px; border-radius:10px;"></div>'
            "</div>\n\n"
            "**AQI Reference:** 0-50 Good | 51-100 Moderate | 101-150 Sensitive | 151-200 Unhealthy | 201-300 Very Unhealthy | 300+ Hazardous\n"
        )
        return result
    return text


# ---------------- CARD BUILDERS ----------------
def build_carbon_card(city, data):
    if not data:
        return (
            '<div class="comparison-card">'
            '<h3 style="margin:0;color:#333;font-size:1rem;">' + city.upper() + "</h3>"
            '<div style="color:#666;">Carbon data not available</div>'
            "</div>"
        )
    carbon_match = re.search(r"(\d+\.?\d*)\s*tons", data)
    if not carbon_match:
        return (
            '<div class="comparison-card">'
            '<h3 style="margin:0;color:#333;font-size:1rem;">' + city.upper() + "</h3>"
            '<div style="color:#666;">Carbon data not available</div>'
            "</div>"
        )
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
    return (
        '<div class="comparison-card" style="border-top:5px solid ' + bg_color + ';">'
        '<h3 style="margin:0;color:#333;font-size:1rem;">' + city.upper() + "</h3>"
        '<div style="font-size:1.5rem;font-weight:bold;color:' + bg_color + ';">' + str(carbon_value) + "</div>"
        '<div style="font-size:0.85rem;color:#666;">tons CO2/year</div>'
        '<div style="background-color:' + bg_color + ';color:white;padding:5px;border-radius:20px;margin-top:10px;font-size:0.8rem;">' + label + "</div>"
        '<div style="margin-top:10px;font-size:0.7rem;color:#666;">Low less than 2 | Moderate 2 to 5 | High greater than 5</div>'
        "</div>"
    )


def build_aqi_card(city, data):
    if not data:
        return (
            '<div class="comparison-card">'
            '<h3 style="margin:0;color:#333;font-size:1rem;">' + city.upper() + "</h3>"
            '<div style="color:#666;">AQI data not available</div>'
            "</div>"
        )
    aqi_match = re.search(r"AQI:\s*(\d+)", data)
    if not aqi_match:
        return (
            '<div class="comparison-card">'
            '<h3 style="margin:0;color:#333;font-size:1rem;">' + city.upper() + "</h3>"
            '<div style="color:#666;">AQI data not available</div>'
            "</div>"
        )
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
    return (
        '<div class="comparison-card" style="border-top:5px solid ' + bg_color + ';">'
        '<h3 style="margin:0;color:#333;font-size:1rem;">' + city.upper() + "</h3>"
        '<div style="font-size:1.5rem;font-weight:bold;color:' + bg_color + ';">' + str(aqi) + "</div>"
        '<div style="background-color:' + bg_color + ";color:" + text_color + ';padding:5px;border-radius:20px;margin-top:10px;font-size:0.8rem;">' + label + "</div>"
        '<div style="margin-top:10px;font-size:0.7rem;color:#666;">0-50 Good | 51-100 Moderate | 101-150 Sensitive | 151-200 Unhealthy | 201-300 Very Unhealthy | 300+ Hazardous</div>'
        "</div>"
    )


# ---------------- KEYWORD MATCHING ----------------
EXACT_SUSTAINABILITY = [
    "tip", "advice", "sustainable", "recycle", "home", "house",
    "transport", "transportation", "travel", "commute", "bicycle", "bike",
    "cycling", "walk", "bus", "train", "metro", "carpool", "flight", "aviation",
    "eco", "eco-friendly", "zero waste", "energy", "solar", "renewable",
    "plastic", "reduce", "reuse", "compost", "sustainable living",
    "electric vehicle"
]

PHRASE_SUSTAINABILITY = [
    "water saving", "public transit", "how can i reduce", "how to reduce",
    "reduce my carbon", "lower my carbon", "carbon footprint reduction",
    "ways to reduce", "tips to reduce", "how can i lower", "reduce my footprint"
]

KNOWN_CITIES = [
    "delhi", "mumbai", "chennai", "kolkata",
    "london", "new york", "tokyo", "beijing", "paris"
]

# Maps detected intent phrases to explicit tool queries so the MCP tool
# receives a clear, unambiguous request and returns the right category.
SUSTAINABILITY_QUERY_MAP = [
    (["how can i reduce", "how to reduce", "reduce my carbon",
      "lower my carbon", "reduce my footprint", "ways to reduce",
      "tips to reduce", "carbon footprint reduction"],
     "general tips to reduce carbon footprint at home and daily life"),
    (["recycle", "zero waste", "reuse", "compost", "plastic"],
     "tips for recycling and reducing waste at home"),
    (["solar", "renewable", "energy"],
     "tips for using renewable energy and saving electricity at home"),
    (["water saving"],
     "tips for saving water at home"),
]


def resolve_sustainability_query(q, original_query):
    """
    Returns a clean, explicit query string to send to the Sustainability_Tips tool.
    If the query matches a known intent, returns a rewritten query.
    Otherwise returns the original query unchanged.
    """
    for triggers, rewritten in SUSTAINABILITY_QUERY_MAP:
        for trigger in triggers:
            if trigger in q:
                return rewritten
    return original_query


def is_sustainability_query(q):
    for phrase in PHRASE_SUSTAINABILITY:
        if phrase in q:
            return True
    for word in EXACT_SUSTAINABILITY:
        if re.search(r"\b" + re.escape(word) + r"\b", q):
            return True
    return False


# ---------------- ROUTER ----------------
def route_query(query):
    q = query.lower()

    # 1. HEALTH EFFECTS
    if any(word in q for word in ["health", "effect", "disease", "respiratory", "cancer", "asthma", "toxic", "pm2.5"]):
        result = call_tool("Environmental_Effects_RAG", query)
        if result:
            return result
        return "No health effects information found in the knowledge base."

    # 2. DETECT MULTI-CITY EARLY
    cities_found = list(dict.fromkeys([city for city in KNOWN_CITIES if city in q]))
    is_multi_city = len(cities_found) >= 2

    # 3. COMPARISON - before sustainability to prevent misrouting
    if "compare" in q or " vs " in q or is_multi_city:
        is_carbon = any(word in q for word in ["carbon", "footprint", "co2", "emission"])
        found = cities_found[:2]

        if len(found) < 2:
            return (
                "Please specify two cities to compare. Found: "
                + (", ".join(found) if found else "none")
                + ". Try 'compare carbon footprint of Delhi and Mumbai'."
            )

        title = "Carbon Footprint Comparison" if is_carbon else "Air Quality Comparison"
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
                '<div class="comparison-container">'
                '<div class="comparison-title">' + title + "</div>"
                '<div class="comparison-wrapper">'
                + cards_html
                + "</div></div>"
            )

        return "No comparison data available for " + ", ".join(found).upper() + "."

    # 4. SUSTAINABILITY TIPS
    #    Rewrites the query before calling the tool so the tool returns
    #    the correct category. Formats the response to suppress big headings.
    if is_sustainability_query(q):
        clean_query = resolve_sustainability_query(q, query)
        result = call_tool("Sustainability_Tips", clean_query)
        if result:
            return format_sustainability_response(result)
        return "No sustainability tips found."

    # 5. CARBON FOOTPRINT (single city only)
    if any(word in q for word in ["carbon", "footprint", "co2", "emission"]):
        result = call_tool("Carbon_Footprint_Calculator", query)
        if result:
            return format_carbon_response(result)
        return "No carbon footprint data found for the specified location."

    # 6. POLLUTION / AQI
    if any(word in q for word in ["pollution", "aqi", "air quality", "pollution index"]):
        result = call_tool("Pollution_Health_Index", query)
        if result:
            return format_pollution_response(result)
        return "No pollution data found for the specified location."

    # 7. POLICIES
    if any(word in q for word in ["policy", "act", "law", "treaty", "agreement", "regulation", "protocol"]):
        result = call_tool("Environmental_Policies_RAG", query)
        if result and len(result) > 50:
            return result
        return "No policy information found in the knowledge base."

    # 8. WEB SEARCH FALLBACK
    result = call_tool("Web_Search", query)
    if result:
        return result
    return "No information found. Please try a different query."


# ---------------- UI ----------------
st.markdown(
    '<div class="main-header"><h1>GreenMind</h1><h3>Your Environmental Sustainability Advisor</h3></div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="main-content">', unsafe_allow_html=True)

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
        st.markdown(
            '<div class="status-box connected">MCP Server Connected</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-box disconnected">MCP Server Disconnected</div>',
            unsafe_allow_html=True,
        )
    st.markdown("---")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

if not st.session_state.messages:
    quotes = [
        {"text": "The earth is what we all have in common.", "author": "Wendell Berry"},
        {"text": "We borrow the earth from our children.", "author": "Native American Proverb"},
        {"text": "The greatest threat is believing someone else will save it.", "author": "Robert Swan"},
    ]
    today_quote = quotes[datetime.now().day % len(quotes)]
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": (
                '<div class="elegant-quote">'
                '<div class="quote-text">"' + today_quote["text"] + '"</div>'
                '<div class="quote-author">- ' + today_quote["author"] + "</div>"
                "</div>\n\nHello! I'm GreenMind.\n\nHow can I help protect our planet today?"
            ),
        }
    )

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

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="footer">GreenMind - Every small action counts towards a greener planet</div>',
    unsafe_allow_html=True,
)