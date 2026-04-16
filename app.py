# app.py - Final, fully corrected frontend
import streamlit as st
import sys
import os
import asyncio
import re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.mcp.client.mcp_client import MCPClient

# ---------- Session ----------
if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = None
if "mcp_connected" not in st.session_state:
    st.session_state.mcp_connected = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- UI ----------
st.set_page_config(page_title="GreenMind", layout="wide")

# ---------- COLOR HELPERS ----------
def get_aqi_color(aqi):
    if aqi <= 50: return "🟢"
    elif aqi <= 100: return "🟡"
    elif aqi <= 150: return "🟠"
    elif aqi <= 200: return "🔴"
    elif aqi <= 300: return "🟣"
    return "⚫"

def get_carbon_color(val):
    if val <= 2.0: return "🟢"
    elif val <= 5.0: return "🟡"
    return "🔴"

# ---------- PARSERS ----------
def parse_pollution(text):
    aqi = re.search(r'AQI:\s*(\d+)', text)
    return {"aqi": int(aqi.group(1)) if aqi else None}

def parse_carbon(text):
    val = re.search(r'(\d+\.?\d*)\s*tons', text)
    return {"carbon": float(val.group(1)) if val else None}

# ---------- FORMATTER ----------
def format_environment(city, aqi=None, carbon=None):
    out = []
    out.append(f"🌍 ENVIRONMENTAL INDEX — {city.upper()}")
    out.append(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    if aqi is not None:
        out.append(f"📊 AQI: {aqi} {get_aqi_color(aqi)}")

    if carbon is not None:
        out.append(f"🌱 Carbon: {carbon} tons CO2/year {get_carbon_color(carbon)}")

    return "\n".join(out)

# ---------- MCP ----------
async def get_client():
    if not st.session_state.mcp_client:
        client = MCPClient(host="greenmind-agent.onrender.com", port=443)
        if await client.connect():
            st.session_state.mcp_client = client
            st.session_state.mcp_connected = True
    return st.session_state.mcp_client

async def call_tool(name, query):
    client = await get_client()
    if not client:
        return None

    try:
        return await asyncio.wait_for(client.call_tool(name, input=query), timeout=30)
    except:
        return None

# ---------- INTENT ----------
def is_tip(q):
    return re.search(r'\b(tip|tips|advice|eco|sustainable|reduce|save energy)\b', q)

def is_comparison(q):
    return any(w in q for w in ["compare", "vs", "versus"])

def extract_cities(q):
    cities = ["delhi","mumbai","chennai","kolkata","london","paris"]
    return [c for c in cities if c in q]

# ---------- CORE ----------
async def process(query):
    q = query.lower()

    # 1. TIPS
    if is_tip(q):
        res = await call_tool("Sustainability_Tips", query)
        return res or "Reduce, reuse, recycle."

    # 2. DIRECT (Paris Agreement)
    if "paris agreement" in q:
        return """Paris Agreement:
• Limits warming to <2°C
• Adopted 2015
• Requires national climate plans"""

    # 3. COMPARISON
    if is_comparison(q):
        cities = extract_cities(q)
        results = []

        for city in cities:
            pol = await call_tool("Pollution_Health_Index", city)
            carb = await call_tool("Carbon_Footprint_Calculator", city)

            aqi = parse_pollution(pol)["aqi"] if pol else None
            carbon = parse_carbon(carb)["carbon"] if carb else None

            results.append(format_environment(city, aqi, carbon))

        return "\n\n" + ("\n" + "-"*40 + "\n").join(results)

    # 4. POLLUTION
    if "aqi" in q or "pollution" in q:
        res = await call_tool("Pollution_Health_Index", query)
        if res:
            parsed = parse_pollution(res)
            return format_environment("Location", aqi=parsed["aqi"])

    # 5. CARBON
    if "carbon" in q:
        res = await call_tool("Carbon_Footprint_Calculator", query)
        if res:
            parsed = parse_carbon(res)
            return format_environment("Location", carbon=parsed["carbon"])

    # 6. POLICY
    if "policy" in q or "agreement" in q:
        res = await call_tool("Environmental_Policies_RAG", query)
        if res:
            return res
        return "No policy info found."

    return "Ask about pollution, carbon, comparison, or sustainability."

def run(query):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(process(query))
    loop.close()
    return result

# ---------- UI ----------
st.title("🌿 GreenMind")

if st.session_state.messages == []:
    st.session_state.messages.append({"role": "assistant", "content": "Ask me about environment."})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask something...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run(prompt)
            st.markdown(f"```\n{response}\n```")

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()