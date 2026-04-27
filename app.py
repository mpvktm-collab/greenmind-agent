# app.py - Version 2026-04-27-FINAL
import streamlit as st
import sys
import os
import asyncio
import requests
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.mcp.client.mcp_client import MCPClient

# ---------- SESSION STATE ----------
if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = None
if "mcp_connected" not in st.session_state:
    st.session_state.mcp_connected = False
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="GreenMind - Environmental Advisor", layout="wide")

# ---------- FORCE ALL TEXT TO NORMAL SIZE ----------
st.markdown("""
<style>
    /* Force all headings to normal size */
    h1, h2, h3, h4, h5, h6 {
        font-size: 1rem !important;
        font-weight: bold !important;
    }
    /* Force all text to normal size */
    p, li, div, span {
        font-size: 1rem !important;
    }
    /* Keep code blocks readable */
    pre, code {
        font-size: 0.85rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------- VERSION ----------
st.sidebar.write("Version: FINAL")

# ---------- MCP CLIENT ----------
async def get_client():
    if not st.session_state.mcp_client:
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
            timeout=90
        )
        return result, "success"
    except Exception as e:
        return None, str(e)

# ---------- PROCESS QUERY - CRITICAL ORDER ----------
async def process(query):
    q = query.lower()
    
    # RULE 1: If query has "health" or "effect" -> Use Effects RAG
    if 'health' in q or 'effect' in q:
        res, _ = await call_tool("Environmental_Effects_RAG", query)
        if res and len(res) > 50:
            return res
        return "Health effects information is currently unavailable."
    
    # RULE 2: If query has "tip" or "advice" or "home" -> Use Tips
    if 'tip' in q or 'advice' in q or 'home' in q:
        res, _ = await call_tool("Sustainability_Tips", query)
        if res:
            return res
        return "Reduce, reuse, recycle!"
    
    # RULE 3: If query has "compare" or "vs" -> Compare cities
    if 'compare' in q or ' vs ' in q:
        cities = ['delhi', 'mumbai', 'chennai', 'london', 'new york', 'tokyo']
        found = [c for c in cities if c in q]
        if not found:
            found = ['delhi', 'mumbai']
        results = []
        for city in found:
            pol, _ = await call_tool("Pollution_Health_Index", city)
            if pol:
                results.append(pol)
        if results:
            return "\n\n---\n\n".join(results)
        return "Comparison data unavailable."
    
    # RULE 4: Pollution index
    if 'pollution' in q or 'aqi' in q or 'air quality' in q:
        res, _ = await call_tool("Pollution_Health_Index", query)
        if res:
            return res
        return "Pollution data unavailable."
    
    # RULE 5: Carbon footprint
    if 'carbon' in q or 'footprint' in q or 'co2' in q:
        res, _ = await call_tool("Carbon_Footprint_Calculator", query)
        if res:
            return res
        return "Carbon footprint data unavailable."
    
    # RULE 6: Policies
    if 'policy' in q or 'act' in q or 'law' in q or 'treaty' in q:
        res, _ = await call_tool("Environmental_Policies_RAG", query)
        if res and len(res) > 50:
            return res
        return "Policy information not available."
    
    # RULE 7: Web search
    res, _ = await call_tool("Web_Search", query)
    if res:
        return res
    
    return "Ask about pollution, carbon footprint, health effects, or sustainability tips."

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
        "content": "Ask me about pollution, carbon footprint, health effects, policies, or sustainability tips."
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Enter your question...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run(prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()