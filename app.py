# app.py - COMPLETE REWRITE - HEALTH FIRST
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

st.set_page_config(page_title="GreenMind - Environmental Advisor", layout="wide")

# ---------- FONT FIX ----------
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

st.sidebar.write("**Version:** HEALTH-FIRST-v2")

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
        print(f"Tool error: {e}")
        return None

# ---------- HEALTH ANSWERS (DIRECT, NO TOOL CALL) ----------
def get_health_answer(query):
    q = query.lower()
    
    if "plastic" in q:
        return """**Health Effects of Plastic Pollution**

**Microplastics & Human Health:**
- Microplastics have been found in drinking water, seafood, salt, and human blood
- Particles can accumulate in organs causing inflammation
- Nanoplastics may cross the blood-brain barrier

**Chemical Hazards:**
- BPA and phthalates leach from plastics and disrupt hormones
- Linked to reproductive issues, diabetes, and developmental problems in children
- Some plastic additives are probable carcinogens

**Prevention:**
- Reduce single-use plastics
- Use glass, stainless steel, or ceramic containers
- Never microwave food in plastic containers
- Filter tap water to remove microplastics"""
    
    if "air" in q:
        return """**Health Effects of Air Pollution**

**Respiratory Effects:**
- Asthma attacks and worsening COPD
- Bronchitis and reduced lung function
- Increased respiratory infections

**Cardiovascular Effects:**
- Heart attacks and stroke
- High blood pressure
- Irregular heartbeat

**Who is most vulnerable?**
- Children, elderly, pregnant women
- People with pre-existing heart or lung conditions

**Protection:**
- Check daily AQI before outdoor activities
- Use air purifiers indoors
- Wear N95 masks on high pollution days"""
    
    if "water" in q:
        return """**Health Effects of Water Pollution**

**Infectious Diseases:**
- Cholera, typhoid, dysentery from contaminated water
- Hepatitis A and giardiasis

**Chemical Contamination:**
- Lead causes developmental delays in children
- Arsenic linked to skin lesions and cancer
- Nitrates cause "blue baby syndrome" in infants

**Protection:**
- Drink filtered or boiled water
- Proper sanitation and sewage treatment
- Reduce chemical runoff from agriculture"""
    
    return None

# ---------- QUERY ROUTING - SIMPLE IF/ELSE CHAIN ----------
def route_query(query):
    q = query.lower()
    
    # RULE 1 - HEALTH EFFECTS (ABSOLUTE HIGHEST PRIORITY)
    # Check for ANY health-related word
    health_words = ['health', 'effect', 'disease', 'respiratory', 'cancer', 'asthma', 'bronchitis', 'toxic']
    if any(word in q for word in health_words):
        # First try the RAG tool
        result = asyncio.run(call_tool("Environmental_Effects_RAG", query))
        if result and len(result) > 50:
            return result
        # Fallback to direct answers
        direct = get_health_answer(query)
        if direct:
            return direct
        return "Health effects information is currently unavailable."
    
    # RULE 2 - TIPS
    tip_words = ['tip', 'advice', 'home', 'garden', 'kitchen', 'recycle']
    if any(word in q for word in tip_words):
        result = asyncio.run(call_tool("Sustainability_Tips", query))
        if result:
            return result
        return "Reduce, reuse, recycle!"
    
    # RULE 3 - PARIS AGREEMENT
    if "paris agreement" in q:
        return """**Paris Agreement** - Legally binding international treaty on climate change adopted in 2015. Aims to limit global warming to well below 2°C, preferably to 1.5°C."""
    
    # RULE 4 - COMPARISON
    if 'compare' in q or ' vs ' in q:
        cities = ['delhi', 'mumbai', 'chennai', 'london', 'new york']
        found = [c for c in cities if c in q]
        if not found:
            found = ['delhi', 'mumbai']
        results = []
        for city in found:
            pol = asyncio.run(call_tool("Pollution_Health_Index", city))
            if pol:
                results.append(f"--- {city.upper()} ---\n{pol}")
        if results:
            return "\n\n".join(results)
        return "Comparison data unavailable."
    
    # RULE 5 - POLLUTION INDEX
    # Only trigger if query has AQI or pollution level terms
    pollution_terms = ['aqi', 'air quality', 'pollution index', 'pollution level']
    if any(word in q for word in pollution_terms):
        result = asyncio.run(call_tool("Pollution_Health_Index", query))
        if result:
            return result
        return "Pollution data unavailable."
    
    # RULE 6 - CARBON FOOTPRINT
    carbon_words = ['carbon', 'footprint', 'co2', 'emission']
    if any(word in q for word in carbon_words):
        result = asyncio.run(call_tool("Carbon_Footprint_Calculator", query))
        if result:
            return result
        return "Carbon footprint data unavailable."
    
    # RULE 7 - POLICIES
    policy_words = ['policy', 'act', 'law', 'treaty', 'agreement', 'regulation']
    if any(word in q for word in policy_words):
        result = asyncio.run(call_tool("Environmental_Policies_RAG", query))
        if result and len(result) > 50:
            return result
        web = asyncio.run(call_tool("Web_Search", query))
        if web:
            return web
        return "Policy information not available."
    
    # RULE 8 - WEB SEARCH
    web = asyncio.run(call_tool("Web_Search", query))
    if web:
        return web
    
    return "Ask me about pollution, carbon footprint, health effects, policies, or sustainability tips."

# ---------- UI ----------
st.title("GreenMind - Environmental Advisor")

if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello! Ask me about:\n\n• Health effects of pollution\n• Air quality (AQI)\n• Carbon footprint\n• Environmental policies\n• Sustainability tips"
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask a question...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = route_query(prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()