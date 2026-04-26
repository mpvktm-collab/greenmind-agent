# app.py - Debug version with connectivity test
import streamlit as st
import sys
import os
import asyncio
import requests
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.mcp.client.mcp_client import MCPClient

# ---------------- CONNECTIVITY TEST (direct, bypassing MCPClient) ----------------
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

# ---------------- SIDEBAR DEBUG INFO ----------------
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
            timeout=60
        )
        if result and isinstance(result, str):
            low = result.lower()
            if "no results" in low or "not found" in low:
                return None, "no_data"
        return result, "success"
    except Exception as e:
        return None, f"error: {str(e)}"

# ---------------- DIRECT ANSWERS ----------------
def get_direct_answer(query):
    q = query.lower()
    if "paris agreement" in q:
        return """Paris Agreement - Legally binding international treaty on climate change.

Key points:
- Adopted by 196 parties at COP 21 in Paris on 12 December 2015
- Entered into force on 4 November 2016
- Goal: Limit global warming to well below 2 degrees Celsius, preferably to 1.5 degrees
- Requires countries to submit Nationally Determined Contributions (NDCs)
- Requires developed countries to provide climate finance"""
    return None

def is_tip_query(q):
    keywords = ['tip', 'tips', 'advice', 'home', 'house', 'garden', 'energy', 'water', 'recycle']
    return any(k in q for k in keywords)

def is_comparison_query(q):
    return any(w in q for w in ["compare", "vs", "versus"])

def extract_cities(q):
    cities = ['delhi', 'mumbai', 'chennai', 'london', 'new york', 'tokyo']
    return [c for c in cities if c in q.lower()]

# ---------------- MAIN PROCESSING ----------------
async def process(query):
    q = query.lower()

    # Tips
    if is_tip_query(q):
        res, _ = await call_tool("Sustainability_Tips", query)
        if res:
            return res
        return "Simple tip: Reduce, reuse, recycle."

    # Direct answers
    direct = get_direct_answer(query)
    if direct:
        return direct

    # Comparison
    if is_comparison_query(q):
        cities = extract_cities(q)
        if not cities:
            cities = ["delhi", "mumbai"]
        parts = []
        for city in cities:
            pol, _ = await call_tool("Pollution_Health_Index", city)
            if pol:
                parts.append(pol)
        if parts:
            return "\n\n" + ("\n" + "-"*40 + "\n").join(parts)
        return "Unable to compare."

    # Pollution
    if any(w in q for w in ["pollution", "aqi", "air quality"]):
        res, _ = await call_tool("Pollution_Health_Index", query)
        if res:
            return res
        return "Pollution data unavailable."

    # Carbon
    if any(w in q for w in ["carbon", "footprint"]):
        res, _ = await call_tool("Carbon_Footprint_Calculator", query)
        if res:
            return res
        return "Carbon data unavailable."

    return "Ask about pollution, carbon footprint, or sustainability tips."

def run(query):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(process(query))
    loop.close()
    return result

# ---------------- UI ----------------
st.title("GreenMind - Environmental Advisor")

if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Ask about pollution, carbon footprint, or sustainability."
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Enter your query")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            response = run(prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()