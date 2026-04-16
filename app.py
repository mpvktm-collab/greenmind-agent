# app.py - Final version using raw tool outputs, consistent routing
import streamlit as st
import sys
import os
import asyncio
import re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.mcp.client.mcp_client import MCPClient

# ---------------- SESSION ----------------
if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = None
if "mcp_connected" not in st.session_state:
    st.session_state.mcp_connected = False
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="GreenMind - Environmental Advisor", layout="wide")

# ---------------- MCP CLIENT (HTTPS for remote) ----------------
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
            timeout=45
        )
        if result and isinstance(result, str):
            low = result.lower()
            if "no results" in low or "not found" in low:
                return None, "no_data"
        return result, "success"
    except Exception as e:
        return None, f"error: {str(e)}"

# ---------------- DIRECT ANSWERS (fallback) ----------------
def get_direct_answer(query):
    q = query.lower()
    if "paris agreement" in q:
        return """The Paris Agreement is a legally binding international treaty on climate change.

Key points:
• Adopted by 196 parties at COP 21 in Paris on 12 December 2015
• Entered into force on 4 November 2016
• Goal: Limit global warming to well below 2°C, preferably to 1.5°C
• Requires countries to submit Nationally Determined Contributions (NDCs)
• Requires developed countries to provide climate finance"""
    if "clean air act" in q:
        return """The Clean Air Act (US) controls air pollution.

Key provisions:
• EPA sets National Ambient Air Quality Standards (NAAQS)
• Regulates emissions from stationary and mobile sources
• Cap-and-trade for acid rain
• First passed 1963, amended 1970, 1977, 1990"""
    if "european green deal" in q or "eu green deal" in q:
        return """The European Green Deal aims to make the EU climate neutral by 2050.

Key policies:
• European Climate Law (legally binding climate neutrality)
• Fit for 55 package (55% emission reduction by 2030)
• Circular Economy Action Plan
• Biodiversity Strategy for 2030
• Farm to Fork Strategy"""
    return None

# ---------------- INTENT DETECTION ----------------
def is_tip_query(q):
    # match common tip keywords
    keywords = ['tip', 'advice', 'sustainable', 'eco-friendly', 'home', 'house',
                'kitchen', 'garden', 'recycle', 'plastic', 'waste', 'energy', 'water']
    return any(k in q for k in keywords)

def is_comparison_query(q):
    return any(w in q for w in ["compare", "comparison", "vs", "versus"])

def extract_cities(q):
    cities = ['delhi','mumbai','chennai','kolkata','bangalore','hyderabad',
              'new york','los angeles','chicago','london','paris','tokyo',
              'beijing','shanghai','sydney','melbourne','toronto','singapore']
    return [c for c in cities if c in q.lower()]

# ---------------- MAIN PROCESSING ----------------
async def process(query):
    q = query.lower()

    # 1. Tips (must be first)
    if is_tip_query(q):
        res, _ = await call_tool("Sustainability_Tips", query)
        if res:
            return res
        return "Simple tip: Reduce, reuse, recycle. Every small action helps."

    # 2. Direct answers (bypass RAG/web)
    direct = get_direct_answer(query)
    if direct:
        return direct

    # 3. Comparison: combine raw outputs of tools
    if is_comparison_query(q):
        cities = extract_cities(q)
        if not cities:
            # default pair
            cities = ["delhi", "mumbai"] if "pollution" in q else ["delhi", "london"]

        parts = []
        for city in cities:
            # Get pollution data
            pol, _ = await call_tool("Pollution_Health_Index", city)
            if pol:
                parts.append(pol)
            # Get carbon data (optional)
            carb, _ = await call_tool("Carbon_Footprint_Calculator", city)
            if carb:
                parts.append(carb)
        if parts:
            return "\n\n" + ("\n" + "-"*50 + "\n").join(parts)
        return "Unable to compare. Try specific city names like Delhi and Mumbai."

    # 4. Pollution / AQI
    if any(w in q for w in ["aqi", "air quality", "pollution index", "pollution of"]):
        res, _ = await call_tool("Pollution_Health_Index", query)
        if res:
            return res
        # fallback for known cities (if tool fails)
        if "delhi" in q:
            return "Pollution data for Delhi is currently unavailable. Please try again later."
        return "Pollution data unavailable. Please try a different location."

    # 5. Carbon footprint
    if any(w in q for w in ["carbon", "footprint", "co2", "emission"]):
        res, _ = await call_tool("Carbon_Footprint_Calculator", query)
        if res:
            return res
        if "delhi" in q:
            return "Carbon footprint data for Delhi is currently unavailable."
        return "Carbon footprint data unavailable. Try a specific city like 'Delhi'."

    # 6. Health effects (use Effects RAG)
    if any(w in q for w in ["health", "disease", "respiratory", "cancer", "asthma"]):
        res, _ = await call_tool("Environmental_Effects_RAG", query)
        if res and len(res) > 50:
            return res
        # fallback generic answer
        if "air pollution" in q:
            return "Air pollution can cause asthma, bronchitis, lung cancer, and respiratory infections. Fine particles (PM2.5) penetrate deep into the lungs and bloodstream."
        return "Health effects information not available. Please rephrase your question."

    # 7. Policies (RAG with fallback to web search)
    if any(w in q for w in ["policy", "act", "regulation", "law", "treaty", "agreement"]):
        res, _ = await call_tool("Environmental_Policies_RAG", query)
        if res and len(res) > 50:
            return res
        # fallback to web search
        res2, _ = await call_tool("Web_Search", query)
        if res2 and "unavailable" not in res2.lower():
            return res2
        return "Policy information not available. Try a more specific query, e.g., 'Paris Agreement goals'."

    # 8. Wikipedia
    if "wikipedia" in q:
        res, _ = await call_tool("Wikipedia_Knowledge", query)
        if res:
            return res
        return "No Wikipedia article found. Try different search terms."

    # 9. General web search
    res, _ = await call_tool("Web_Search", query)
    if res and "unavailable" not in res.lower():
        return res

    return "I couldn't find information on that topic. Please ask about environmental policies, pollution, carbon footprint, or sustainability tips."

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
        "content": "Ask about pollution, carbon footprint, sustainability, policies, or compare cities."
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
            st.markdown(response)   # raw markdown (rich formatting preserved)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()