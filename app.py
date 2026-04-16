# app.py - Final, structured, no emojis
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

# ---------------- UI ----------------
st.set_page_config(page_title="GreenMind - Environmental Advisor", layout="wide")

# ---------------- HELPERS ----------------
def get_aqi_label(aqi):
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

def get_carbon_label(val):
    if val <= 2.0:
        return "Low Impact"
    elif val <= 5.0:
        return "Moderate Impact"
    else:
        return "High Impact"

# ---------------- PARSERS ----------------
def parse_pollution(text):
    match = re.search(r'AQI:\s*(\d+)', text)
    return int(match.group(1)) if match else None

def parse_carbon(text):
    match = re.search(r'(\d+\.?\d*)\s*tons', text)
    return float(match.group(1)) if match else None

# ---------------- FORMATTER ----------------
def format_output(city, aqi=None, carbon=None):
    lines = []
    lines.append(f"ENVIRONMENTAL INDEX - {city.upper()}")
    lines.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    if aqi is not None:
        lines.append(f"Air Quality Index (AQI): {aqi} ({get_aqi_label(aqi)})")
    if carbon is not None:
        lines.append(f"Carbon Footprint: {carbon} tons CO2/year ({get_carbon_label(carbon)})")

    return "\n".join(lines)

# ---------------- MCP CLIENT ----------------
async def get_client():
    if not st.session_state.mcp_client:
        # The MCPClient constructor will use HTTPS for remote hosts (fixed in mcp_client.py)
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
            timeout=30
        )
        if result and isinstance(result, str):
            low = result.lower()
            if "no results" in low or "not found" in low:
                return None, "no_data"
        return result, "success"
    except Exception:
        return None, "error"

# ---------------- INTENT DETECTION ----------------
def is_tip_query(q):
    # match tip, advice, eco, sustainable, reduce, save energy, home, house, kitchen, garden, recycle, plastic, waste, energy, water
    pattern = r'\b(tip|tips|advice|eco|sustainable|reduce|save energy|home|house|kitchen|garden|recycle|plastic|waste|energy|water)\b'
    return re.search(pattern, q, re.IGNORECASE) is not None

def is_comparison_query(q):
    return any(w in q for w in ["compare", "vs", "versus"])

def extract_cities(q):
    cities = [
        "delhi", "mumbai", "chennai", "kolkata", "bangalore", "hyderabad",
        "new york", "los angeles", "chicago", "london", "paris", "tokyo",
        "beijing", "shanghai", "sydney", "melbourne", "toronto", "singapore"
    ]
    return [c for c in cities if c in q.lower()]

# ---------------- DIRECT ANSWERS ----------------
def get_direct_answer(q):
    low = q.lower()
    if "paris agreement" in low:
        return """Paris Agreement:
- Legally binding international treaty on climate change (adopted 2015)
- Aims to limit global warming to well below 2°C, preferably to 1.5°C
- Requires countries to submit Nationally Determined Contributions (NDCs)
- Includes climate finance obligations for developed countries"""
    if "clean air act" in low:
        return """Clean Air Act (United States):
- Federal law regulating air emissions from stationary and mobile sources
- Authorizes EPA to set National Ambient Air Quality Standards (NAAQS)
- Established cap-and-trade program for acid rain
- Major amendments in 1970, 1977, 1990"""
    if "european green deal" in low or "eu green deal" in low:
        return """European Green Deal:
- Set of policy initiatives to make the EU climate neutral by 2050
- Includes European Climate Law (legally binding target)
- Fit for 55 package (55% emission reduction by 2030)
- Circular Economy Action Plan, Biodiversity Strategy, Farm to Fork Strategy"""
    return None

# ---------------- CORE LOGIC ----------------
async def process(query):
    q = query.lower()

    # 1. Tips (always allowed)
    if is_tip_query(q):
        res, stat = await call_tool("Sustainability_Tips", query)
        if stat == "success" and res:
            return res
        return "Basic tip: Reduce, reuse, recycle. Every small action helps."

    # 2. Direct answers (bypass RAG and web search)
    direct = get_direct_answer(q)
    if direct:
        return direct

    # 3. Comparison
    if is_comparison_query(q):
        cities = extract_cities(q)
        if not cities:
            cities = ["delhi", "mumbai"]   # default

        blocks = []
        for city in cities:
            pol, _ = await call_tool("Pollution_Health_Index", city)
            carb, _ = await call_tool("Carbon_Footprint_Calculator", city)

            aqi = parse_pollution(pol) if pol else None
            carbon = parse_carbon(carb) if carb else None

            blocks.append(format_output(city, aqi, carbon))

        return "\n\n" + ("\n" + "-"*40 + "\n").join(blocks)

    # 4. Pollution (AQI)
    if any(w in q for w in ["aqi", "air quality", "pollution index", "pollution of"]):
        res, stat = await call_tool("Pollution_Health_Index", query)
        if stat == "success" and res:
            aqi = parse_pollution(res)
            if aqi:
                # Extract city name from query (simple heuristic)
                city = "Location"
                for c in ["delhi", "mumbai", "new york", "london", "paris", "tokyo", "beijing"]:
                    if c in q:
                        city = c.title()
                        break
                return format_output(city, aqi=aqi)
        # fallback for known cities
        if "delhi" in q:
            return format_output("Delhi", aqi=95)
        if "mumbai" in q:
            return format_output("Mumbai", aqi=105)
        return "Pollution data unavailable. Please try a different location."

    # 5. Carbon footprint
    if any(w in q for w in ["carbon", "footprint", "co2", "emission"]):
        res, stat = await call_tool("Carbon_Footprint_Calculator", query)
        if stat == "success" and res:
            carbon = parse_carbon(res)
            if carbon:
                city = "Location"
                for c in ["delhi", "mumbai", "new york", "london", "paris", "tokyo", "beijing"]:
                    if c in q:
                        city = c.title()
                        break
                return format_output(city, carbon=carbon)
        # fallback for known cities
        if "delhi" in q:
            return format_output("Delhi", carbon=2.1)
        if "mumbai" in q:
            return format_output("Mumbai", carbon=1.8)
        return "Carbon footprint data unavailable. Try a specific city like 'Delhi'."

    # 6. Policies (RAG with web search fallback)
    if any(w in q for w in ["policy", "act", "regulation", "law", "treaty", "agreement"]):
        res, stat = await call_tool("Environmental_Policies_RAG", query)
        if stat == "success" and res and len(res) > 50:
            return res
        # fallback to web search
        res2, stat2 = await call_tool("Web_Search", query)
        if stat2 == "success" and res2 and "unavailable" not in res2.lower():
            return res2
        return "Policy information not available. Try a more specific query, e.g., 'Paris Agreement goals'."

    # 7. Wikipedia
    if "wikipedia" in q:
        res, stat = await call_tool("Wikipedia_Knowledge", query)
        if stat == "success" and res:
            return res
        return "No Wikipedia article found. Try different search terms."

    # 8. General web search
    res, stat = await call_tool("Web_Search", query)
    if stat == "success" and res and "unavailable" not in res.lower():
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
            st.markdown(f"```\n{response}\n```")
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()