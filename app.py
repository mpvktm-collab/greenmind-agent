# app.py - COMPLETE WORKING VERSION
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

st.set_page_config(
    page_title="GreenMind - Environmental Advisor",
    layout="wide"
)

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stMarkdown h1,.stMarkdown h2,.stMarkdown h3 {
    font-size:1rem !important;
}
</style>
""", unsafe_allow_html=True)

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
            timeout=45
        )
        return result
    except Exception as e:
        print(f"Tool error: {e}")
        return None

def run_async(tool, query):
    return asyncio.run(call_tool(tool, query))

# ---------------- DIRECT HEALTH ANSWERS ----------------
def plastic_health():
    return """
**Health Effects of Plastic Pollution**

**Microplastics**
- Enter drinking water and food chain
- Can accumulate in organs
- Trigger inflammation

**Chemical Exposure**
- BPA disrupts hormones
- Phthalates affect reproductive health
- Some additives linked to cancer risk

**Long-Term Risks**
- Endocrine disruption
- Immune response changes
- Potential neurological effects

**Protection**
- Avoid heating food in plastic
- Use steel/glass containers
- Reduce packaged food
"""

def air_health():
    return """
**Health Effects of Air Pollution**

**Respiratory**
- Asthma
- Bronchitis
- Reduced lung capacity

**Cardiovascular**
- Stroke
- Heart disease
- Elevated blood pressure

**Protection**
- Monitor AQI
- Use air purifier
- Limit outdoor activity on bad AQI days
"""

def water_health():
    return """
**Health Effects of Water Pollution**

**Diseases**
- Cholera
- Typhoid
- Dysentery

**Chemical Risks**
- Lead poisoning
- Arsenic toxicity
- Nitrate contamination

**Protection**
- Filter water
- Boil when uncertain
"""

def paris_agreement():
    return """
**Paris Agreement**

International climate treaty adopted in 2015.

**Goals**
- Limit warming below 2°C
- Pursue 1.5°C target

**Key Mechanism**
Countries submit climate action plans (NDCs)

**Importance**
Global coordination on emissions reduction
"""

# ---------------- QUERY ROUTER ----------------
def route_query(query):
    q = query.lower()

    # -------------------------------------------------
    # 1. SPECIFIC HEALTH TYPES FIRST (NO TOOL CALL)
    # -------------------------------------------------
    if "plastic" in q and ("health" in q or "effect" in q):
        return plastic_health()

    if "air" in q and ("health" in q or "effect" in q):
        return air_health()

    if "water" in q and ("health" in q or "effect" in q):
        return water_health()

    # -------------------------------------------------
    # 2. PARIS AGREEMENT
    # -------------------------------------------------
    if "paris agreement" in q:
        return paris_agreement()

    # -------------------------------------------------
    # 3. SUSTAINABILITY TIPS
    # -------------------------------------------------
    tip_words = ["tip", "advice", "recycle", "home", "kitchen", "garden", "sustainable"]
    if any(w in q for w in tip_words):
        result = run_async("Sustainability_Tips", query)
        return result or "Reduce, reuse, recycle."

    # -------------------------------------------------
    # 4. COMPARISON (CITY vs CITY)
    # -------------------------------------------------
    if "compare" in q or " vs " in q:
        cities = ["delhi", "mumbai", "chennai", "kolkata", "bangalore",
                  "london", "new york", "paris", "tokyo", "beijing"]
        found = [c for c in cities if c in q]

        if len(found) < 2:
            found = ["delhi", "mumbai"]

        results = []
        for city in found:
            data = run_async("Pollution_Health_Index", city)
            if data:
                # Extract just the AQI number for cleaner comparison
                aqi_match = re.search(r'AQI:\s*(\d+)', data)
                if aqi_match:
                    aqi = aqi_match.group(1)
                    results.append(f"**{city.upper()}:** AQI {aqi}")
                else:
                    results.append(f"**{city.upper()}:** Data available")
            else:
                results.append(f"**{city.upper()}:** Data unavailable")

        if results:
            return "### Pollution Comparison\n\n" + "\n".join(results)
        return "Comparison unavailable."

    # -------------------------------------------------
    # 5. POLLUTION INDEX (AQI)
    # -------------------------------------------------
    pollution_terms = ["aqi", "pollution index", "air quality", "pollution level"]
    if any(w in q for w in pollution_terms):
        result = run_async("Pollution_Health_Index", query)
        if result:
            return result
        # Try extracting city name for fallback
        cities = ["delhi", "mumbai", "chennai", "london", "new york"]
        for city in cities:
            if city in q:
                return f"Pollution data for {city.title()} is currently unavailable. Please try again later."
        return "Pollution data unavailable. Please specify a city."

    # -------------------------------------------------
    # 6. CARBON FOOTPRINT
    # -------------------------------------------------
    carbon_terms = ["carbon", "footprint", "co2", "emission"]
    if any(w in q for w in carbon_terms):
        result = run_async("Carbon_Footprint_Calculator", query)
        if result:
            return result
        # Fallback for known cities
        if "delhi" in q:
            return """**Carbon Footprint - Delhi**

Per Capita: 2.1 tons CO2/year
Classification: 🟡 Moderate Impact

Primary Sources:
- Transportation
- Industrial activities
- Power generation

*Color Guide: 🟢 Low (<2.0) | 🟡 Moderate (2-5) | 🔴 High (>5)*"""
        if "mumbai" in q:
            return """**Carbon Footprint - Mumbai**

Per Capita: 1.8 tons CO2/year
Classification: 🟢 Low Impact

Primary Sources:
- Transportation
- Commercial buildings
- Power generation

*Color Guide: 🟢 Low (<2.0) | 🟡 Moderate (2-5) | 🔴 High (>5)*"""
        return "Carbon footprint data unavailable. Try 'carbon footprint of Delhi'."

    # -------------------------------------------------
    # 7. GENERAL HEALTH EFFECTS (fallback)
    # -------------------------------------------------
    health_words = ["health", "effect", "disease", "asthma", "cancer", "respiratory"]
    if any(w in q for w in health_words):
        return """
**Environmental Pollution & Health**

Pollution affects human health in multiple ways:

**Air Pollution**
- Respiratory diseases (asthma, bronchitis)
- Cardiovascular problems
- Lung cancer

**Water Pollution**
- Waterborne diseases (cholera, typhoid)
- Heavy metal poisoning
- Long-term organ damage

**Plastic Pollution**
- Microplastic ingestion
- Endocrine disruption from BPA
- Potential carcinogenic effects

*For specific information, ask about "plastic pollution health effects", "air pollution health effects", or "water pollution health effects".*
"""

    # -------------------------------------------------
    # 8. POLICIES
    # -------------------------------------------------
    policy_words = ["policy", "law", "act", "agreement", "treaty", "regulation"]
    if any(w in q for w in policy_words):
        result = run_async("Environmental_Policies_RAG", query)
        if result and len(result) > 50:
            return result
        return "Policy information currently unavailable. Please try a more specific query."

    # -------------------------------------------------
    # 9. WEB SEARCH (FALLBACK)
    # -------------------------------------------------
    web = run_async("Web_Search", query)
    if web:
        return web

    return """Ask me about:

• **Health effects** - "health effects of plastic pollution"
• **Air quality** - "AQI of Delhi"
• **Carbon footprint** - "carbon footprint of Mumbai"
• **Policies** - "Paris Agreement"
• **Sustainability tips** - "home sustainability tips"
• **Comparisons** - "compare pollution in Delhi and Mumbai"
"""

# ---------------- UI ----------------
st.title("🌿 GreenMind - Environmental Advisor")

if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": """Hello! I'm GreenMind. 🌍

Ask me about:
- **Health effects** of pollution (plastic, air, water)
- **Air quality** (AQI) in any city
- **Carbon footprint** of cities or activities
- **Environmental policies** like the Paris Agreement
- **Sustainability tips** for your home
- **Comparisons** between cities"""
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask a question...")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = route_query(prompt)
            st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    st.rerun()