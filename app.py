# app.py - FINAL WORKING VERSION - HEALTH FIRST
import streamlit as st
import sys
import os
import asyncio
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.mcp.client.mcp_client import MCPClient

# ---------- SESSION ----------
if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = None
if "mcp_connected" not in st.session_state:
    st.session_state.mcp_connected = False
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="GreenMind", layout="wide")

# ---------- FIX FONT SIZE ----------
st.markdown("""
<style>
    /* Force all headings to normal size */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
    .stChatMessage h1, .stChatMessage h2, .stChatMessage h3,
    h1, h2, h3, h4, h5, h6 {
        font-size: 1rem !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.write("**Version:** HEALTH-FIRST")

# ---------- MCP CLIENT ----------
async def get_client():
    if st.session_state.mcp_client is None:
        client = MCPClient(host="greenmind-agent.onrender.com")
        await client.connect()
        st.session_state.mcp_client = client
        st.session_state.mcp_connected = True
    return st.session_state.mcp_client

async def call_tool(tool_name, query):
    client = await get_client()
    try:
        result = await asyncio.wait_for(
            client.call_tool(tool_name, input=query),
            timeout=60
        )
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

# ---------- DIRECT ANSWER ----------
def get_direct_answer(query):
    q = query.lower()
    if "paris agreement" in q:
        return """**Paris Agreement** - Legally binding international treaty on climate change adopted in 2015. Aims to limit global warming to well below 2°C, preferably to 1.5°C."""
    return None

# ---------- HEALTH FALLBACKS ----------
def get_health_fallback(query):
    q = query.lower()
    if "plastic" in q:
        return """**Health Effects of Plastic Pollution**

**Microplastics:**
- Found in drinking water, seafood, and human blood
- Can accumulate in organs and cause inflammation

**Chemical Leaching:**
- BPA and phthalates disrupt hormones
- Linked to reproductive issues and developmental problems

**Prevention:**
- Reduce single-use plastics
- Use glass or stainless steel containers
- Never microwave plastic containers"""
    
    if "air" in q:
        return """**Health Effects of Air Pollution**

**Respiratory:**
- Asthma, bronchitis, COPD
- Reduced lung function

**Cardiovascular:**
- Heart attacks and stroke
- High blood pressure

**Vulnerable groups:** Children, elderly, pregnant women"""
    
    return None

# ---------- ROUTING FUNCTIONS ----------
def is_health_query(q):
    # This MUST be checked FIRST
    health_words = ['health', 'disease', 'respiratory', 'cancer', 'asthma', 'effect', 'effects']
    return any(word in q for word in health_words)

def is_tip_query(q):
    tip_words = ['tip', 'advice', 'home', 'garden', 'kitchen']
    return any(word in q for word in tip_words)

def is_compare_query(q):
    return 'compare' in q or ' vs ' in q

def is_pollution_query(q):
    # Only check if NOT a health query
    pollution_words = ['aqi', 'air quality', 'pollution index', 'pollution level']
    return any(word in q for word in pollution_words)

def is_carbon_query(q):
    carbon_words = ['carbon', 'footprint', 'co2', 'emission']
    return any(word in q for word in carbon_words)

def is_policy_query(q):
    policy_words = ['policy', 'act', 'law', 'treaty', 'agreement']
    return any(word in q for word in policy_words)

# ---------- MAIN PROCESSING - ORDER IS CRITICAL ----------
async def process(query):
    q = query.lower()
    
    # PRIORITY 1: HEALTH - MUST BE ABSOLUTELY FIRST
    if is_health_query(q):
        result = await call_tool("Environmental_Effects_RAG", query)
        if result and len(result) > 50:
            return result
        fallback = get_health_fallback(query)
        if fallback:
            return fallback
        return "Health effects information is currently unavailable."
    
    # PRIORITY 2: TIPS
    if is_tip_query(q):
        result = await call_tool("Sustainability_Tips", query)
        if result:
            return result
        return "Reduce, reuse, recycle!"
    
    # PRIORITY 3: DIRECT ANSWER
    direct = get_direct_answer(query)
    if direct:
        return direct
    
    # PRIORITY 4: COMPARE
    if is_compare_query(q):
        cities = ['delhi', 'mumbai', 'chennai', 'london']
        found = [c for c in cities if c in q]
        if not found:
            found = ['delhi', 'mumbai']
        results = []
        for city in found:
            pol = await call_tool("Pollution_Health_Index", city)
            if pol:
                results.append(f"--- {city.upper()} ---\n{pol}")
        if results:
            return "\n\n".join(results)
        return "Comparison data unavailable."
    
    # PRIORITY 5: POLLUTION
    if is_pollution_query(q):
        result = await call_tool("Pollution_Health_Index", query)
        if result:
            return result
        return "Pollution data unavailable."
    
    # PRIORITY 6: CARBON
    if is_carbon_query(q):
        result = await call_tool("Carbon_Footprint_Calculator", query)
        if result:
            return result
        return "Carbon footprint data unavailable."
    
    # PRIORITY 7: POLICIES
    if is_policy_query(q):
        result = await call_tool("Environmental_Policies_RAG", query)
        if result:
            return result
        web = await call_tool("Web_Search", query)
        if web:
            return web
        return "Policy information not available."
    
    # PRIORITY 8: WEB SEARCH
    web = await call_tool("Web_Search", query)
    if web:
        return web
    
    return "Ask me about pollution, carbon footprint, health effects, policies, or sustainability tips."

def run(query):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(process(query))
    loop.close()
    return result

# ---------- UI ----------
st.title("GreenMind - Environmental Advisor")

if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! Ask me about:\n• Health effects of pollution\n• Pollution levels (AQI)\n• Carbon footprint\n• Environmental policies\n• Sustainability tips"
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask a question...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run(prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()