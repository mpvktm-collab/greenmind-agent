# app.py - Final with version marker and correct routing
# app.py - Complete version without emojis
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

# ---------------- VERSION MARKER (to verify deployment) ----------------
st.sidebar.write("**Version:** 2026-04-16-final-no-emoji")

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
            timeout=60          # increased to handle cold starts
        )
        if result and isinstance(result, str):
            low = result.lower()
            if "no results" in low or "not found" in low:
                return None, "no_data"
        return result, "success"
    except Exception as e:
        return None, f"error: {str(e)}"

# ---------------- DIRECT ANSWERS (hardcoded, no emojis) ----------------
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
    if "clean air act" in q:
        return """Clean Air Act (United States) - Controls air pollution.

Key provisions:
- EPA sets National Ambient Air Quality Standards (NAAQS)
- Regulates emissions from stationary and mobile sources
- Cap-and-trade program for acid rain
- First passed 1963, major amendments in 1970, 1977, 1990"""
    if "european green deal" in q or "eu green deal" in q:
        return """European Green Deal - Aims to make the EU climate neutral by 2050.

Key policies:
- European Climate Law (legally binding climate neutrality)
- Fit for 55 package (55 percent emission reduction by 2030)
- Circular Economy Action Plan
- Biodiversity Strategy for 2030
- Farm to Fork Strategy"""
    return None

# ---------------- INTENT DETECTION ----------------
def is_tip_query(q):
    keywords = [
        'tip', 'tips', 'advice', 'sustainable', 'eco-friendly', 'home', 'house',
        'kitchen', 'garden', 'recycle', 'plastic', 'waste', 'energy', 'water',
        'sustainability', 'green living', 'reduce', 'reuse'
    ]
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

    # 1. TIPS (must be FIRST)
    if is_tip_query(q):
        res, _ = await call_tool("Sustainability_Tips", query)
        if res:
            return res
        return "Simple tip: Reduce, reuse, recycle. Every small action helps."

    # 2. DIRECT ANSWERS
    direct = get_direct_answer(query)
    if direct:
        return direct

    # 3. HEALTH EFFECTS (use Effects RAG)
    if any(w in q for w in ["health", "disease", "respiratory", "cancer", "asthma", "bronchitis"]):
        res, _ = await call_tool("Environmental_Effects_RAG", query)
        if res and len(res) > 50:
            return res
        if "air pollution" in q:
            return "Air pollution can cause asthma, bronchitis, lung cancer, and respiratory infections. Fine particles (PM2.5) penetrate deep into the lungs and bloodstream."
        return "Health effects information not available. Please rephrase your question."

    # 4. COMPARISON (raw tool outputs)
    if is_comparison_query(q):
        cities = extract_cities(q)
        if not cities:
            cities = ["delhi", "mumbai"] if "pollution" in q else ["delhi", "london"]
        parts = []
        for city in cities:
            pol, _ = await call_tool("Pollution_Health_Index", city)
            if pol:
                parts.append(pol)
            carb, _ = await call_tool("Carbon_Footprint_Calculator", city)
            if carb:
                parts.append(carb)
        if parts:
            return "\n\n" + ("\n" + "-"*50 + "\n").join(parts)
        return "Unable to compare. Try 'compare pollution in Delhi and Mumbai'."

    # 5. POLLUTION / AQI
    if any(w in q for w in ["aqi", "air quality", "pollution index", "pollution of"]):
        res, _ = await call_tool("Pollution_Health_Index", query)
        if res:
            return res
        return "Pollution data unavailable. Please try a different location."

    # 6. CARBON FOOTPRINT
    if any(w in q for w in ["carbon", "footprint", "co2", "emission"]):
        res, _ = await call_tool("Carbon_Footprint_Calculator", query)
        if res:
            return res
        return "Carbon footprint data unavailable. Try a specific city like 'Delhi'."

    # 7. POLICIES (RAG with web search fallback)
    if any(w in q for w in ["policy", "act", "regulation", "law", "treaty", "agreement"]):
        res, _ = await call_tool("Environmental_Policies_RAG", query)
        if res and len(res) > 50:
            return res
        res2, _ = await call_tool("Web_Search", query)
        if res2 and "unavailable" not in res2.lower():
            return res2
        return "Policy information not available. Try a more specific query, e.g., 'Paris Agreement goals'."

    # 8. WIKIPEDIA
    if "wikipedia" in q:
        res, _ = await call_tool("Wikipedia_Knowledge", query)
        if res:
            return res
        return "No Wikipedia article found. Try different search terms."

    # 9. GENERAL WEB SEARCH
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

# ---------------- UI (wrap all assistant responses in <pre> for consistent monospace) ----------------
st.title("GreenMind - Environmental Advisor")

if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Ask about pollution, carbon footprint, sustainability, policies, or compare cities."
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and not msg["content"].startswith("Ask about"):
            st.markdown(
                f'<pre style="font-family: monospace; font-size: 1rem; background-color: #f5f5f5; padding: 12px; border-radius: 8px; white-space: pre-wrap;">{msg["content"]}</pre>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(msg["content"])

prompt = st.chat_input("Enter your query")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            response = run(prompt)
            st.markdown(
                f'<pre style="font-family: monospace; font-size: 1rem; background-color: #f5f5f5; padding: 12px; border-radius: 8px; white-space: pre-wrap;">{response}</pre>',
                unsafe_allow_html=True
            )
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()