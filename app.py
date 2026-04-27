# app.py - FINAL WORKING VERSION
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
    /* Make all text normal size */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
    .stChatMessage h1, .stChatMessage h2, .stChatMessage h3,
    h1, h2, h3, h4, h5, h6 {
        font-size: 1rem !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- VERSION ----------
st.sidebar.write("**Version:** FINAL-2026-04-27")

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
        return None

# ---------- ROUTING - SIMPLE AND CLEAR ----------
def is_health_query(q):
    health_words = ['health', 'effect', 'disease', 'respiratory', 'cancer', 'asthma']
    return any(word in q for word in health_words)

def is_tip_query(q):
    tip_words = ['tip', 'advice', 'home', 'garden', 'kitchen', 'recycle']
    return any(word in q for word in tip_words)

def is_pollution_query(q):
    pollution_words = ['aqi', 'air quality', 'pollution index', 'pollution level']
    return any(word in q for word in pollution_words)

def is_carbon_query(q):
    carbon_words = ['carbon', 'footprint', 'co2', 'emission']
    return any(word in q for word in carbon_words)

def is_compare_query(q):
    return 'compare' in q or ' vs ' in q or 'versus' in q

def is_policy_query(q):
    policy_words = ['policy', 'act', 'law', 'treaty', 'agreement', 'regulation']
    return any(word in q for word in policy_words)

async def process(query):
    q = query.lower()
    
    # 1. HEALTH - FIRST PRIORITY
    if is_health_query(q):
        result = await call_tool("Environmental_Effects_RAG", query)
        if result:
            return result
        return "Health effects information is currently unavailable. Please try again."
    
    # 2. TIPS
    if is_tip_query(q):
        result = await call_tool("Sustainability_Tips", query)
        if result:
            return result
        return "Simple tip: Reduce, reuse, recycle."
    
    # 3. DIRECT ANSWER FOR COMMON QUERIES
    if "paris agreement" in q:
        return """Paris Agreement - Legally binding international treaty on climate change adopted in 2015. Aims to limit global warming to well below 2°C, preferably to 1.5°C."""
    
    # 4. COMPARE
    if is_compare_query(q):
        cities = ['delhi', 'mumbai', 'chennai', 'london', 'new york']
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
    
    # 5. POLLUTION
    if is_pollution_query(q):
        result = await call_tool("Pollution_Health_Index", query)
        if result:
            return result
        return "Pollution data unavailable."
    
    # 6. CARBON
    if is_carbon_query(q):
        result = await call_tool("Carbon_Footprint_Calculator", query)
        if result:
            return result
        return "Carbon footprint data unavailable."
    
    # 7. POLICIES
    if is_policy_query(q):
        result = await call_tool("Environmental_Policies_RAG", query)
        if result and len(result) > 50:
            return result
        web = await call_tool("Web_Search", query)
        if web:
            return web
        return "Policy information not available."
    
    # 8. FALLBACK
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
        "content": "Hello! Ask me about:\n• Pollution levels (AQI)\n• Carbon footprint\n• Health effects\n• Environmental policies\n• Sustainability tips"
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