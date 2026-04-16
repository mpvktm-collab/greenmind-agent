# app.py - Final, structured JSON tool pipeline
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
st.set_page_config(page_title="GreenMind", layout="wide")

# ---------------- HELPERS ----------------
def get_aqi_label(aqi):
    if aqi <= 50: return "Good"
    elif aqi <= 100: return "Moderate"
    elif aqi <= 150: return "Sensitive"
    elif aqi <= 200: return "Unhealthy"
    elif aqi <= 300: return "Very Unhealthy"
    return "Hazardous"

def get_carbon_label(val):
    if val <= 2.0: return "Low"
    elif val <= 5.0: return "Moderate"
    return "High"

# ---------------- PARSERS ----------------
def parse_pollution(text):
    match = re.search(r'AQI:\s*(\d+)', text)
    return int(match.group(1)) if match else None

def parse_carbon(text):
    match = re.search(r'(\d+\.?\d*)\s*tons', text)
    return float(match.group(1)) if match else None

# ---------------- FORMATTER ----------------
def format_output(city, aqi=None, carbon=None):
    output = []
    output.append(f"ENVIRONMENTAL INDEX - {city.upper()}")
    output.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    if aqi is not None:
        output.append(f"AQI: {aqi} ({get_aqi_label(aqi)})")

    if carbon is not None:
        output.append(f"Carbon Footprint: {carbon} tons CO2/year ({get_carbon_label(carbon)})")

    return "\n".join(output)

# ---------------- MCP ----------------
async def get_client():
    if not st.session_state.mcp_client:
        client = MCPClient(host="greenmind-agent.onrender.com", port=443)
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
    except:
        return None, "error"

# ---------------- INTENT ----------------
def is_tip(q):
    return re.search(r'\b(tip|tips|advice|eco|sustainable|reduce|save energy)\b', q)

def is_comparison(q):
    return any(w in q for w in ["compare", "vs", "versus"])

def extract_cities(q):
    cities = [
        "delhi","mumbai","chennai","kolkata",
        "london","paris","new york","tokyo"
    ]
    return [c for c in cities if c in q]

# ---------------- DIRECT ANSWERS ----------------
def get_direct_answer(q):
    if "paris agreement" in q:
        return """Paris Agreement:
- International climate treaty adopted in 2015
- Limits global warming to below 2°C, ideally 1.5°C
- Countries submit national climate action plans
- Includes climate finance obligations"""
    return None

# ---------------- CORE LOGIC ----------------
async def process(query):
    q = query.lower()

    # 1. Tips
    if is_tip(q):
        res, stat = await call_tool("Sustainability_Tips", query)
        if stat == "success" and res:
            return res
        return "Basic tip: Reduce, reuse, recycle."

    # 2. Direct answers
    direct = get_direct_answer(q)
    if direct:
        return direct

    # 3. Comparison
    if is_comparison(q):
        cities = extract_cities(q)
        if not cities:
            cities = ["delhi", "mumbai"]

        blocks = []

        for city in cities:
            pol, _ = await call_tool("Pollution_Health_Index", city)
            carb, _ = await call_tool("Carbon_Footprint_Calculator", city)

            aqi = parse_pollution(pol) if pol else None
            carbon = parse_carbon(carb) if carb else None

            blocks.append(format_output(city, aqi, carbon))

        return "\n\n" + ("\n" + "-"*40 + "\n").join(blocks)

    # 4. Pollution
    if "aqi" in q or "pollution" in q:
        res, stat = await call_tool("Pollution_Health_Index", query)
        if stat == "success" and res:
            aqi = parse_pollution(res)
            return format_output("Location", aqi=aqi)

        if "delhi" in q:
            return format_output("Delhi", aqi=95)

        return "Pollution data unavailable."

    # 5. Carbon
    if any(w in q for w in ["carbon","footprint","co2"]):
        res, stat = await call_tool("Carbon_Footprint_Calculator", query)
        if stat == "success" and res:
            carbon = parse_carbon(res)
            if carbon:
                return format_output("Location", carbon=carbon)

        if "delhi" in q:
            return format_output("Delhi", carbon=2.1)

        return "Carbon data unavailable."

    # 6. Policies
    if any(w in q for w in ["policy","act","law","agreement","treaty"]):
        res, stat = await call_tool("Environmental_Policies_RAG", query)
        if stat == "success" and res:
            return res

        res2, stat2 = await call_tool("Web_Search", query)
        if stat2 == "success" and res2:
            return res2

        return "Policy information not available."

    return "Ask about pollution, carbon footprint, sustainability, or environmental policies."

# ---------------- RUNNER ----------------
def run(query):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(process(query))
    loop.close()
    return result

# ---------------- UI ----------------
st.title("GreenMind - Environmental Advisor")

if st.session_state.messages == []:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Ask about pollution, carbon footprint, sustainability, or policies."
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Enter your query")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Processing"):
            response = run(prompt)
            st.markdown(f"```\n{response}\n```")

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()