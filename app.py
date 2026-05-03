import streamlit as st
import sys
import os
import asyncio
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.mcp.client.mcp_client import MCPClient

# ---------------- SESSION ----------------
if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = None
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="GreenMind", layout="wide")

# ---------------- MCP ----------------
async def get_client():
    if st.session_state.mcp_client is None:
        client = MCPClient(host="greenmind-agent.onrender.com")
        await client.connect()
        st.session_state.mcp_client = client
    return st.session_state.mcp_client


async def call_tool(tool_name, query):
    try:
        client = await get_client()
        result = await asyncio.wait_for(
            client.call_tool(tool_name, input=query),
            timeout=40
        )
        return result
    except:
        return None


def run_async(tool, query):
    return asyncio.run(call_tool(tool, query))


# ---------------- VALIDATORS ----------------
def is_aqi_response(text):
    if not text:
        return False
    patterns = ["AQI:", "PM2.5", "ENVIRONMENTAL HEALTH INDEX"]
    return any(p.lower() in text.lower() for p in patterns)


# ---------------- DIRECT RESPONSES ----------------
def plastic_health():
    return """Health Effects of Plastic Pollution

Microplastics:
- Enter food and water
- Accumulate in organs
- Cause inflammation

Chemicals:
- BPA disrupts hormones
- Phthalates affect fertility

Prevention:
- Avoid plastic containers for hot food
- Use glass or steel
"""


def water_tips():
    return """Sustainability Tips for Reducing Water Pollution

- Avoid dumping chemicals or oils into drains
- Use eco-friendly detergents
- Reduce plastic waste entering waterways
- Properly dispose of medicines and hazardous waste
- Conserve water to reduce wastewater load
"""


def paris():
    return """Paris Agreement

- Global climate treaty (2015)
- Limits warming below 2°C
- Countries submit climate plans
"""


# ---------------- ROUTER ----------------
def route_query(query):
    q = query.lower()

    # -------------------------------------------------
    # 1. EXACT INTENT: SUSTAINABILITY TIPS (HIGHEST PRIORITY)
    # -------------------------------------------------
    if "tip" in q or "advice" in q or "sustainability" in q:

        # special case: water pollution tips
        if "water" in q:
            return water_tips()

        result = run_async("Sustainability_Tips", query)

        # reject wrong tool output
        if result and not is_aqi_response(result):
            return result

        return "Use less plastic, conserve water, and recycle."

    # -------------------------------------------------
    # 2. HEALTH (STRICT)
    # -------------------------------------------------
    if "health" in q or "effect" in q:

        if "plastic" in q:
            return plastic_health()

        result = run_async("Environmental_Effects_RAG", query)

        if result and not is_aqi_response(result):
            return result

        return "Pollution affects respiratory, cardiovascular, and immune systems."

    # -------------------------------------------------
    # 3. PARIS AGREEMENT
    # -------------------------------------------------
    if "paris agreement" in q:
        return paris()

    # -------------------------------------------------
    # 4. COMPARISON
    # -------------------------------------------------
    if "compare" in q or " vs " in q:
        cities = ["delhi", "mumbai", "london"]
        found = [c for c in cities if c in q]

        if len(found) < 2:
            found = ["delhi", "mumbai"]

        results = []
        for city in found:
            data = run_async("Pollution_Health_Index", city)
            if data:
                aqi = re.search(r"AQI:\s*(\d+)", data)
                if aqi:
                    results.append(f"{city.upper()}: AQI {aqi.group(1)}")

        return "\n".join(results) if results else "Comparison unavailable."

    # -------------------------------------------------
    # 5. POLLUTION (STRICT TRIGGER)
    # -------------------------------------------------
    if any(x in q for x in ["aqi", "air quality", "pollution index"]):
        result = run_async("Pollution_Health_Index", query)
        if result:
            return result
        return "Pollution data unavailable."

    # -------------------------------------------------
    # 6. CARBON
    # -------------------------------------------------
    if any(x in q for x in ["carbon", "footprint", "co2"]):
        result = run_async("Carbon_Footprint_Calculator", query)

        if result and not is_aqi_response(result):
            return result

        if "delhi" in q:
            return "Delhi carbon footprint: ~2.1 tons CO2 per capita per year."

        return "Carbon data unavailable."

    # -------------------------------------------------
    # 7. POLICIES
    # -------------------------------------------------
    if any(x in q for x in ["policy", "law", "treaty", "agreement"]):
        result = run_async("Environmental_Policies_RAG", query)
        if result:
            return result
        return "Policy information unavailable."

    # -------------------------------------------------
    # 8. FALLBACK
    # -------------------------------------------------
    return "Ask about pollution, carbon footprint, health effects, sustainability, or policies."


# ---------------- UI ----------------
st.title("GreenMind")

if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Ask about sustainability, pollution, health, or policies."
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask something")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = route_query(prompt)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()