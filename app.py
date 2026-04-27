# app.py - Version 2026-04-27-v3
import streamlit as st
import sys
import os
import asyncio
import requests
from datetime import datetime
 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.mcp.client.mcp_client import MCPClient
 
# ---------------- CONNECTIVITY TEST ----------------
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
 
# ---------------- FONT NORMALIZATION CSS ----------------
# Prevents markdown headers in tool output from rendering as huge headings.
# Tool responses are wrapped in a <div class="tool-output"> before display,
# so this CSS only flattens headings inside that wrapper — regular chat
# markdown (bold, lists, etc.) is unaffected everywhere else.
st.markdown("""
<style>
/* Normalize all heading sizes inside tool output blocks */
div.tool-output h1,
div.tool-output h2,
div.tool-output h3,
div.tool-output h4,
div.tool-output h5,
div.tool-output h6 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    margin: 0.4rem 0 0.2rem 0 !important;
    line-height: 1.4 !important;
}
 
/* Keep pre/code blocks readable */
div.tool-output pre,
div.tool-output code {
    font-size: 0.85rem !important;
}
 
/* Tighten paragraph spacing inside tool output */
div.tool-output p {
    margin: 0.2rem 0 !important;
    line-height: 1.5 !important;
}
</style>
""", unsafe_allow_html=True)
 
# ---------------- VERSION MARKER ----------------
st.sidebar.write("**Version:** 2026-04-27-v3")
 
# ---------------- SIDEBAR DEBUG ----------------
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
            timeout=90
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
        return """**Paris Agreement** — Legally binding international treaty on climate change.
 
**Key points:**
- Adopted by 196 parties at COP 21 in Paris on 12 December 2015
- Entered into force on 4 November 2016
- Goal: Limit global warming to well below 2°C, preferably to 1.5°C
- Requires countries to submit Nationally Determined Contributions (NDCs)"""
    return None
 
# ---------------- QUERY CLASSIFIERS ----------------
# Health/effects keywords — checked BEFORE pollution/carbon to avoid mis-routing.
HEALTH_KEYWORDS = [
    'health', 'disease', 'respiratory', 'cancer', 'effect', 'effects',
    'impact', 'impacts', 'harm', 'harmful', 'symptom', 'symptoms',
    'cause', 'causes', 'risk', 'risks', 'toxic', 'toxicity',
]
 
TIP_KEYWORDS = [
    'tip', 'tips', 'advice', 'home', 'house', 'garden',
    'energy saving', 'water saving', 'recycle', 'sustainable living',
]
 
POLICY_KEYWORDS = [
    'policy', 'policies', 'act', 'regulation', 'law', 'treaty',
    'agreement', 'protocol', 'framework', 'legislation',
]
 
POLLUTION_KEYWORDS = [
    'aqi', 'air quality', 'pollution index', 'pollution level',
    'pollution of', 'air pollution level', 'pollution in',
]
 
CARBON_KEYWORDS = [
    'carbon footprint', 'footprint', 'co2 emission', 'carbon emission',
    'greenhouse gas', 'ghg',
]
 
COMPARISON_KEYWORDS = ['compare', ' vs ', 'versus']
 
def matches_any(q, keywords):
    return any(k in q for k in keywords)
 
def extract_cities(q):
    cities = ['delhi', 'mumbai', 'chennai', 'kolkata', 'london',
              'new york', 'tokyo', 'beijing', 'paris', 'sydney']
    return [c for c in cities if c in q]
 
# ---------------- RESPONSE WRAPPER ----------------
def tool_response(text: str) -> str:
    """
    Wrap tool output in a div so the CSS above can normalize heading sizes.
    Strips leading markdown '#' headings from the first line if they would
    render as an H1/H2 — replaces them with bold text instead.
    """
    if not text:
        return text
 
    # Replace markdown headings with bold equivalents to avoid giant text
    lines = text.split('\n')
    normalized = []
    for line in lines:
        # Match lines that start with one or more '#' characters
        stripped = line.lstrip()
        if stripped.startswith('#'):
            # Count heading level
            level = len(stripped) - len(stripped.lstrip('#'))
            heading_text = stripped.lstrip('#').strip()
            if level == 1:
                # H1 → bold + slightly larger via HTML
                normalized.append(f'**{heading_text}**')
            elif level <= 3:
                # H2/H3 → bold
                normalized.append(f'**{heading_text}**')
            else:
                # H4+ → italic bold
                normalized.append(f'***{heading_text}***')
        else:
            normalized.append(line)
 
    return '\n'.join(normalized)
 
# ---------------- HEALTH EFFECTS FALLBACKS ----------------
HEALTH_FALLBACKS = {
    'plastic': """**Health Effects of Plastic Pollution**
 
Plastic pollution poses serious risks to human health through multiple exposure pathways:
 
**Microplastics & Ingestion**
- Microplastics have been detected in drinking water, seafood, salt, and even human blood
- Particles can accumulate in organs, triggering inflammation and oxidative stress
- Nanoplastics (<1 μm) can cross the blood-brain barrier
 
**Chemical Leaching**
- BPA (Bisphenol A) and phthalates leach from plastics and act as endocrine disruptors
- Linked to hormonal imbalances, reproductive issues, and developmental problems in children
- Flame retardants and stabilisers in plastics are associated with neurotoxicity
 
**Carcinogenic Risk**
- Several plastic additives (e.g., styrene, vinyl chloride) are classified as probable carcinogens
- Burning plastic releases dioxins and furans — highly toxic compounds
 
**Respiratory Exposure**
- Plastic fibres in the air (from synthetic textiles, degrading waste) cause lung irritation
- Workers in plastic manufacturing face elevated occupational risks
 
**Prevention Tips**
- Reduce single-use plastics and switch to glass or stainless steel containers
- Never heat food in plastic containers
- Filter tap water and choose certified plastic-free products""",
 
    'air': """**Health Effects of Air Pollution**
 
Air pollution is one of the leading environmental causes of death globally (WHO: ~7 million deaths/year).
 
**Respiratory System**
- Short-term: Irritation of airways, coughing, wheezing
- Long-term: Asthma, chronic bronchitis, COPD, reduced lung function
 
**Cardiovascular System**
- Fine particles (PM2.5) enter the bloodstream, increasing risk of heart attack and stroke
- Long-term exposure linked to atherosclerosis and hypertension
 
**Cancer**
- PM2.5 and diesel exhaust are classified as Group 1 carcinogens (IARC)
- Elevated lung cancer risk even in non-smokers in polluted areas
 
**Neurological Effects**
- Emerging evidence links air pollution to cognitive decline and dementia
- Children exposed to high pollution levels show reduced IQ and attention issues
 
**Vulnerable Groups**
- Children, elderly, pregnant women, and those with pre-existing conditions face the highest risk
 
PM2.5 is considered the most dangerous pollutant — particles smaller than 2.5 μm penetrate deep into the lungs and enter the bloodstream.""",
 
    'water': """**Health Effects of Water Pollution**
 
Contaminated water is responsible for approximately 485,000 deaths from diarrhoeal diseases annually (WHO).
 
**Microbial Contamination**
- Bacteria (E. coli, Salmonella), viruses (Hepatitis A), and parasites cause acute gastrointestinal illness
- Long-term exposure to low levels increases risk of chronic gut disease
 
**Chemical Pollutants**
- Heavy metals (lead, mercury, arsenic): neurotoxic, carcinogenic, damage kidneys and liver
- Nitrates from agricultural runoff cause methemoglobinaemia ("blue baby syndrome") in infants
- PFAS ("forever chemicals"): linked to cancer, thyroid disease, and immune suppression
 
**Skin & Eye Contact**
- Contaminated water causes dermatitis, eye infections, and chemical burns
 
**Long-Term Risks**
- Chronic low-level exposure to pollutants raises cancer risk (bladder, kidney, colorectal)""",
}
 
def get_health_fallback(q):
    for keyword, response in HEALTH_FALLBACKS.items():
        if keyword in q:
            return response
    return None
 
# ---------------- MAIN PROCESSING ----------------
async def process(query):
    q = query.lower()
 
    # ----------------------------------------------------------------
    # PRIORITY 1: SUSTAINABILITY TIPS
    # Must come first so "energy saving tips" doesn't fall to carbon/health.
    # ----------------------------------------------------------------
    if matches_any(q, TIP_KEYWORDS):
        res, status = await call_tool("Sustainability_Tips", query)
        if res:
            return tool_response(res)
        return "**Sustainability Tip:** Reduce, reuse, recycle — and carry a reusable bag!"
 
    # ----------------------------------------------------------------
    # PRIORITY 2: HEALTH / EFFECTS
    # Checked BEFORE pollution index and carbon so that queries like
    # "health effects of plastic pollution" are NOT mis-routed to the
    # Pollution_Health_Index tool.
    # ----------------------------------------------------------------
    if matches_any(q, HEALTH_KEYWORDS):
        res, status = await call_tool("Environmental_Effects_RAG", query)
        if res and len(res) > 80:
            return tool_response(res)
        # RAG returned nothing useful — use curated fallback
        fallback = get_health_fallback(q)
        if fallback:
            return fallback
        # Last resort: web search
        res_web, _ = await call_tool("Web_Search", query)
        if res_web and len(res_web) > 80:
            return tool_response(res_web)
        return "Health effects information is currently unavailable. Please rephrase your question."
 
    # ----------------------------------------------------------------
    # PRIORITY 3: DIRECT HARDCODED ANSWERS (fast path for common queries)
    # ----------------------------------------------------------------
    direct = get_direct_answer(query)
    if direct:
        return direct
 
    # ----------------------------------------------------------------
    # PRIORITY 4: COMPARISON (city vs city)
    # ----------------------------------------------------------------
    if matches_any(q, COMPARISON_KEYWORDS):
        cities = extract_cities(q)
        if not cities:
            cities = ["delhi", "mumbai"] if "pollution" in q else ["delhi", "london"]
        parts = []
        for city in cities:
            pol, _ = await call_tool("Pollution_Health_Index", city)
            if pol:
                parts.append(tool_response(pol))
            carb, _ = await call_tool("Carbon_Footprint_Calculator", city)
            if carb:
                parts.append(tool_response(carb))
        if parts:
            return ("\n" + "—" * 40 + "\n").join(parts)
        return "Unable to retrieve comparison data for the requested locations."
 
    # ----------------------------------------------------------------
    # PRIORITY 5: POLLUTION / AQI INDEX
    # Only triggered by explicit AQI/pollution-level queries — NOT by
    # generic mentions of "pollution" which could be health/policy topics.
    # ----------------------------------------------------------------
    if matches_any(q, POLLUTION_KEYWORDS):
        res, _ = await call_tool("Pollution_Health_Index", query)
        if res:
            return tool_response(res)
        return "Pollution index data is currently unavailable for that location."
 
    # ----------------------------------------------------------------
    # PRIORITY 6: CARBON FOOTPRINT
    # ----------------------------------------------------------------
    if matches_any(q, CARBON_KEYWORDS):
        res, _ = await call_tool("Carbon_Footprint_Calculator", query)
        if res:
            return tool_response(res)
        return "Carbon footprint data is currently unavailable."
 
    # ----------------------------------------------------------------
    # PRIORITY 7: ENVIRONMENTAL POLICIES
    # ----------------------------------------------------------------
    if matches_any(q, POLICY_KEYWORDS):
        res, _ = await call_tool("Environmental_Policies_RAG", query)
        if res and len(res) > 50:
            return tool_response(res)
        # Fallback to web search for policy queries
        res_web, _ = await call_tool("Web_Search", query)
        if res_web and res_web.strip():
            return tool_response(res_web)
        return "Policy information is not available for that query."
 
    # ----------------------------------------------------------------
    # PRIORITY 8: WIKIPEDIA (explicit request)
    # ----------------------------------------------------------------
    if "wikipedia" in q:
        res, _ = await call_tool("Wikipedia_Knowledge", query)
        if res:
            return tool_response(res)
        return "No Wikipedia article found for that topic."
 
    # ----------------------------------------------------------------
    # PRIORITY 9: GENERAL WEB SEARCH (catch-all)
    # Note: res2 bug from previous version is fixed — res_web is used
    # consistently throughout this function.
    # ----------------------------------------------------------------
    res_web, _ = await call_tool("Web_Search", query)
    if res_web and res_web.strip():
        return tool_response(res_web)
 
    return (
        "I couldn't find information on that topic. "
        "I can help with environmental policies, pollution levels, "
        "health effects, carbon footprints, or sustainability tips."
    )
 
def run(query):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(process(query))
    loop.close()
    return result
 
# ---------------- UI ----------------
st.title("🌿 GreenMind — Environmental Advisor")
 
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Hello! I'm **GreenMind**, your intelligent environmental advisor. 🌍\n\n"
            "*\"The Earth does not belong to us — we belong to the Earth.\"*\n\n"
            "Ask me about pollution levels, environmental policies, health effects, "
            "carbon footprints, or sustainability tips."
        )
    })
 
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
 
prompt = st.chat_input("Ask GreenMind anything about the environment...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("🌱 Thinking..."):
            response = run(prompt)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()