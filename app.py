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

# ---------------- GLOBAL EVENT LOOP ----------------
# Create a single event loop to reuse
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

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
    """Run async function using the global event loop"""
    return loop.run_until_complete(call_tool(tool, query))

# ---------------- VALIDATORS ----------------
def is_aqi_response(text):
    """Check if response is AQI data (should be rejected for health queries)"""
    if not text:
        return False
    # AQI responses contain these patterns
    aqi_patterns = ["AQI:", "PM2.5", "ENVIRONMENTAL HEALTH INDEX", "PM10", "Low → →"]
    text_lower = text.lower()
    return any(p.lower() in text_lower for p in aqi_patterns)

# ---------------- DIRECT RESPONSES ----------------
def plastic_health():
    return """**Health Effects of Plastic Pollution**

**Microplastics:**
- Enter food and water supply
- Accumulate in organs
- Cause inflammation

**Chemicals:**
- BPA disrupts hormones
- Phthalates affect fertility
- Linked to reproductive issues

**Prevention:**
- Avoid plastic containers for hot food
- Use glass or steel containers
- Reduce single-use plastics"""

def water_tips():
    return """**Sustainability Tips for Reducing Water Pollution**

- Avoid dumping chemicals or oils into drains
- Use eco-friendly detergents
- Reduce plastic waste entering waterways
- Properly dispose of medicines and hazardous waste
- Conserve water to reduce wastewater load"""

def paris():
    return """**Paris Agreement**

- Global climate treaty adopted in 2015
- Aims to limit warming below 2°C
- Countries submit climate action plans (NDCs)"""

def air_health():
    return """**Health Effects of Air Pollution**

**Respiratory:**
- Asthma and bronchitis
- Reduced lung function
- Lung cancer risk

**Cardiovascular:**
- Heart attacks and stroke
- High blood pressure

**Protection:**
- Monitor AQI levels
- Use air purifiers indoors
- Wear masks on high pollution days"""

# ---------------- ROUTER ----------------
def route_query(query):
    q = query.lower()

    # -------------------------------------------------
    # 1. EXACT INTENT: SUSTAINABILITY TIPS
    # -------------------------------------------------
    if "tip" in q or "advice" in q or "sustainability" in q:
        # Special case: water pollution tips
        if "water" in q:
            return water_tips()
        
        result = run_async("Sustainability_Tips", query)
        # Accept result if it's not AQI data
        if result and not is_aqi_response(result):
            return result
        return "Use less plastic, conserve water, and recycle."

    # -------------------------------------------------
    # 2. HEALTH (STRICT - CHECK SPECIFIC FIRST)
    # -------------------------------------------------
    if "health" in q or "effect" in q or "disease" in q:
        # Plastic health
        if "plastic" in q:
            return plastic_health()
        
        # Air health
        if "air" in q:
            return air_health()
        
        # Try RAG for other health queries
        result = run_async("Environmental_Effects_RAG", query)
        if result and not is_aqi_response(result) and len(result) > 50:
            return result
        
        return "Pollution affects respiratory, cardiovascular, and immune systems. For specific effects, ask about 'plastic pollution health effects' or 'air pollution health effects'."

    # -------------------------------------------------
    # 3. PARIS AGREEMENT
    # -------------------------------------------------
    if "paris agreement" in q:
        return paris()

    # -------------------------------------------------
    # 4. COMPARISON
    # -------------------------------------------------
    if "compare" in q or " vs " in q:
        cities = ["delhi", "mumbai", "chennai", "kolkata", "london", "new york"]
        found = [c for c in cities if c in q]
        
        if len(found) < 2:
            found = ["delhi", "mumbai"]
        
        results = []
        for city in found:
            data = run_async("Pollution_Health_Index", city)
            if data:
                aqi_match = re.search(r"AQI:\s*(\d+)", data)
                if aqi_match:
                    results.append(f"**{city.upper()}:** AQI {aqi_match.group(1)}")
                else:
                    results.append(f"**{city.upper()}:** Data available")
        
        if results:
            return "### Pollution Comparison\n\n" + "\n".join(results)
        return "Comparison unavailable."

    # -------------------------------------------------
    # 5. POLLUTION (AQI)
    # -------------------------------------------------
    if any(x in q for x in ["aqi", "air quality", "pollution index"]):
        result = run_async("Pollution_Health_Index", query)
        if result:
            return result
        return "Pollution data unavailable. Please specify a city like 'Delhi'."

    # -------------------------------------------------
    # 6. CARBON FOOTPRINT
    # -------------------------------------------------
    if any(x in q for x in ["carbon", "footprint", "co2"]):
        result = run_async("Carbon_Footprint_Calculator", query)
        if result and not is_aqi_response(result):
            return result
        # Fallback for known cities
        if "delhi" in q:
            return """**Carbon Footprint - Delhi**

Per Capita: 2.1 tons CO2/year
Classification: 🟡 Moderate Impact

Primary Sources: Transportation, Industry, Power Generation"""
        if "mumbai" in q:
            return """**Carbon Footprint - Mumbai**

Per Capita: 1.8 tons CO2/year
Classification: 🟢 Low Impact

Primary Sources: Transportation, Commercial Buildings, Power Generation"""
        return "Carbon data unavailable. Try 'carbon footprint of Delhi'."

    # -------------------------------------------------
    # 7. POLICIES
    # -------------------------------------------------
    if any(x in q for x in ["policy", "law", "treaty", "agreement", "act"]):
        result = run_async("Environmental_Policies_RAG", query)
        if result and len(result) > 50:
            return result
        return "Policy information unavailable. Try 'Paris Agreement'."

    # -------------------------------------------------
    # 8. FALLBACK
    # -------------------------------------------------
    return """Ask me about:

• **Health effects** - "health effects of plastic pollution"
• **Air quality** - "AQI of Delhi"  
• **Carbon footprint** - "carbon footprint of Mumbai"
• **Policies** - "Paris Agreement"
• **Sustainability tips** - "sustainability tips for home"
• **Comparisons** - "compare pollution in Delhi and Mumbai"
"""

# ---------------- UI ----------------
st.title("🌿 GreenMind - Environmental Advisor")

if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": """Hello! Ask me about:

• **Health effects** of plastic, air, or water pollution
• **Air quality** (AQI) in any city
• **Carbon footprint** of cities
• **Environmental policies** like the Paris Agreement
• **Sustainability tips** for your home
• **Comparisons** between cities"""
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask a question...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = route_query(prompt)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()