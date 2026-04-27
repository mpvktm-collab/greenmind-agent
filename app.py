# app.py - Version 2026-04-27-v4 (FINAL FIX)
import streamlit as st
import sys
import os
import asyncio
import requests
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.mcp.client.mcp_client import MCPClient

# ---------------- CONNECTIVITY TEST ----------------
backend_url = "https://greenmind-agent.onrender.com"
try:
    test_response = requests.get(f"{backend_url}/tools", timeout=30)
    backend_status = f"Reachable (status {test_response.status_code})"
except Exception as e:
    backend_status = f"Unreachable: {str(e)}"

# ---------------- SESSION ----------------
if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = None
if "mcp_connected" not in st.session_state:
    st.session_state.mcp_connected = False
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="GreenMind - Environmental Advisor", layout="wide")

# ---------------- FONT NORMALIZATION CSS ----------------
st.markdown("""
<style>
/* Normalize all heading sizes inside all outputs */
.stChatMessage h1, .stChatMessage h2, .stChatMessage h3,
.stChatMessage h4, .stChatMessage h5, .stChatMessage h6 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    margin: 0.4rem 0 0.2rem 0 !important;
}
.stChatMessage pre, .stChatMessage code { font-size: 0.85rem !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- VERSION MARKER ----------------
st.sidebar.write("**Version:** 2026-04-27-v4")

# ---------------- SIDEBAR DEBUG ----------------
st.sidebar.write("**Debug Info**")
st.sidebar.write(f"Backend URL: {backend_url}")
st.sidebar.write(f"Backend Status: {backend_status}")
st.sidebar.write(f"MCP Connected: {st.session_state.mcp_connected}")
st.sidebar.write("---")

# ---------------- MCP CLIENT ----------------
async def get_client():
    if not st.session_state.mcp_client:
        client = MCPClient(host="greenmind-agent.onrender.com")
        if await client.connect():
            st.session_state.mcp_client = client
            st.session_state.mcp_connected = True
    return st.session_state.mcp_client

async def call_tool(tool_name, query):
    client = await get_client()
    if not client:
        return None, "error"
    try:
        result = await asyncio.wait_for(
            client.call_tool(tool_name, input=query),
            timeout=90
        )
        if result and isinstance(result, str):
            low = result.lower()
            if "no results" in low or "not found" in low:
                return None, "no_data"
        return result, "success"
    except Exception as e:
        return None, f"error: {str(e)}"

# ---------------- RESPONSE WRAPPER ----------------
def clean_heading(text: str) -> str:
    """Remove markdown headings to prevent giant fonts"""
    if not text:
        return text
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith('#'):
            # Remove the # symbols and make bold instead
            content = stripped.lstrip('#').strip()
            cleaned.append(f"**{content}**")
        else:
            cleaned.append(line)
    return '\n'.join(cleaned)

# ---------------- DIRECT ANSWERS ----------------
def get_direct_answer(query):
    q = query.lower()
    if "paris agreement" in q:
        return """**Paris Agreement** — Legally binding international treaty on climate change.

**Key points:**
- Adopted by 196 parties at COP 21 in Paris on 12 December 2015
- Entered into force on 4 November 2016
- Goal: Limit global warming to well below 2°C, preferably to 1.5°C
- Requires countries to submit Nationally Determined Contributions (NDCs)"""
    return None

# ---------------- HEALTH EFFECTS FALLBACKS ----------------
HEALTH_FALLBACKS = {
    'plastic': """**Health Effects of Plastic Pollution**

**Microplastics & Ingestion**
- Microplastics detected in drinking water, seafood, salt, and human blood
- Particles accumulate in organs, causing inflammation and oxidative stress

**Chemical Leaching**
- BPA and phthalates leach from plastics, acting as endocrine disruptors
- Linked to hormonal imbalances, reproductive issues, and developmental problems

**Prevention Tips**
- Reduce single-use plastics, use glass or stainless steel containers
- Never heat food in plastic containers""",

    'air': """**Health Effects of Air Pollution**

**Respiratory System**
- Short-term: Coughing, wheezing, throat irritation
- Long-term: Asthma, bronchitis, COPD, reduced lung function

**Cardiovascular System**
- Fine particles (PM2.5) increase risk of heart attack and stroke

**Vulnerable Groups**
- Children, elderly, pregnant women, and those with pre-existing conditions face highest risk""",

    'water': """**Health Effects of Water Pollution**

**Microbial Contamination**
- Bacteria, viruses, and parasites cause acute gastrointestinal illness

**Chemical Pollutants**
- Heavy metals (lead, mercury, arsenic): neurotoxic and carcinogenic
- Nitrates cause methemoglobinemia in infants"""
}

def get_health_fallback(q):
    q_lower = q.lower()
    for keyword, response in HEALTH_FALLBACKS.items():
        if keyword in q_lower:
            return response
    return None

# ---------------- QUERY PROCESSING ----------------
async def process(query):
    q = query.lower()
    
    # ============================================================
    # PRIORITY 1: HEALTH EFFECTS - CHECK FIRST, BEFORE ANYTHING ELSE
    # ============================================================
    # This MUST be the very first check to prevent "health effects of plastic pollution"
    # from being routed to the pollution tool.
    if 'health' in q or 'effect' in q or 'disease' in q or 'respiratory' in q:
        # First try the RAG tool
        res, status = await call_tool("Environmental_Effects_RAG", query)
        if res and len(res) > 100:
            return clean_heading(res)
        # Fallback to curated answers
        fallback = get_health_fallback(query)
        if fallback:
            return fallback
        # Last resort: web search
        res_web, _ = await call_tool("Web_Search", query)
        if res_web and len(res_web) > 50:
            return clean_heading(res_web)
        return "Health effects information is currently unavailable."
    
    # ============================================================
    # PRIORITY 2: SUSTAINABILITY TIPS
    # ============================================================
    tip_keywords = ['tip', 'tips', 'advice', 'home', 'garden', 'energy saving', 'water saving', 'recycle']
    if any(k in q for k in tip_keywords):
        res, status = await call_tool("Sustainability_Tips", query)
        if res:
            return clean_heading(res)
        return "**Sustainability Tip:** Reduce, reuse, recycle!"

    # ============================================================
    # PRIORITY 3: DIRECT ANSWERS
    # ============================================================
    direct = get_direct_answer(query)
    if direct:
        return direct

    # ============================================================
    # PRIORITY 4: COMPARISON
    # ============================================================
    if 'compare' in q or ' vs ' in q:
        cities = ['delhi', 'mumbai', 'chennai', 'london', 'new york', 'tokyo']
        found_cities = [c for c in cities if c in q]
        if not found_cities:
            found_cities = ["delhi", "mumbai"]
        parts = []
        for city in found_cities[:3]:
            pol, _ = await call_tool("Pollution_Health_Index", city)
            if pol:
                parts.append(clean_heading(pol))
            carb, _ = await call_tool("Carbon_Footprint_Calculator", city)
            if carb:
                parts.append(clean_heading(carb))
        if parts:
            return "\n\n---\n\n".join(parts)
        return "Unable to compare locations."

    # ============================================================
    # PRIORITY 5: POLLUTION / AQI (only if no health keywords)
    # ============================================================
    pollution_keywords = ['aqi', 'air quality', 'pollution index', 'pollution level']
    if any(k in q for k in pollution_keywords):
        res, _ = await call_tool("Pollution_Health_Index", query)
        if res:
            return clean_heading(res)
        return "Pollution data unavailable for that location."

    # ============================================================
    # PRIORITY 6: CARBON FOOTPRINT
    # ============================================================
    carbon_keywords = ['carbon', 'footprint', 'co2', 'emission']
    if any(k in q for k in carbon_keywords):
        res, _ = await call_tool("Carbon_Footprint_Calculator", query)
        if res:
            return clean_heading(res)
        return "Carbon footprint data unavailable."

    # ============================================================
    # PRIORITY 7: POLICIES
    # ============================================================
    policy_keywords = ['policy', 'act', 'regulation', 'law', 'treaty', 'agreement']
    if any(k in q for k in policy_keywords):
        res, _ = await call_tool("Environmental_Policies_RAG", query)
        if res and len(res) > 50:
            return clean_heading(res)
        res_web, _ = await call_tool("Web_Search", query)
        if res_web:
            return clean_heading(res_web)
        return "Policy information not available."

    # ============================================================
    # PRIORITY 8: WEB SEARCH
    # ============================================================
    res_web, _ = await call_tool("Web_Search", query)
    if res_web:
        return clean_heading(res_web)

    return "I couldn't find information on that topic. Please try rephrasing your question."

def run(query):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(process(query))
    loop.close()
    return result

# ---------------- UI ----------------
st.title("🌿 GreenMind — Environmental Advisor")

if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! I'm **GreenMind**, your environmental advisor.\n\nAsk me about pollution levels, health effects, carbon footprints, policies, or sustainability tips."
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask GreenMind about the environment...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run(prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()