# app.py - Final version for stable backend (commit 5b0f18d)
import streamlit as st
import sys
import os
import asyncio
import re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.mcp.client.mcp_client import MCPClient
from config import Config

# ---------- Session state initialization ----------
if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = None
if "mcp_connected" not in st.session_state:
    st.session_state.mcp_connected = False
if "connection_attempted" not in st.session_state:
    st.session_state.connection_attempted = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quote_data" not in st.session_state:
    st.session_state.quote_data = None

st.set_page_config(
    page_title="GreenMind - Environmental Sustainability Advisor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CSS (sticky header, consistent font) ----------
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #4CAF50 100%);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 1rem;
        position: sticky;
        top: 0;
        z-index: 999;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        font-size: 2rem;
        margin-bottom: 0.2rem;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    /* The subtitle style is also applied inline in the HTML for safety */
    .stChatMessage pre, .stChatMessage code, .stMarkdown pre {
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 1rem !important;
        background-color: #f5f5f5 !important;
        padding: 12px !important;
        border-radius: 8px !important;
        white-space: pre-wrap !important;
        border: 1px solid #e0e0e0 !important;
    }
    .elegant-quote {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 15px;
        text-align: center;
        border-left: 6px solid #2E7D32;
    }
    .quote-text { font-size: 1.1rem; font-style: italic; color: #1B5E20; }
    .quote-author { font-size: 0.8rem; color: #2E7D32; text-align: right; margin-top: 0.5rem; }
    .status-box { padding: 0.5rem; border-radius: 8px; margin-bottom: 0.8rem; text-align: center; font-size: 0.85rem; }
    .connected { background-color: #d4edda; color: #155724; }
    .disconnected { background-color: #f8d7da; color: #721c24; }
    .footer { text-align: center; color: #666; padding: 0.5rem; margin-top: 1rem; font-size: 0.7rem; border-top: 1px solid #e0e0e0; }
    .stChatMessage { padding: 10px !important; margin: 8px 0 !important; background-color: #ffffff; border-radius: 10px; border: 1px solid #e0e0e0; }
</style>
""", unsafe_allow_html=True)

# ---------- Environmental keywords ----------
ENVIRONMENTAL_KEYWORDS = [
    'environment', 'climate', 'pollution', 'polluion', 'polution', 'air quality',
    'sustainable', 'carbon', 'footprint', 'co2', 'emission', 'aqi',
    'water', 'waste', 'plastic', 'forest', 'biodiversity', 'green',
    'policy', 'act', 'regulation', 'law', 'treaty', 'agreement',
    'effect', 'impact', 'health', 'disease', 'cancer', 'respiratory',
    'diseases', 'waterborne', 'cholera', 'typhoid', 'asthma', 'bronchitis',
    'wikipedia', 'eco-friendly', 'transportation', 'recycle', 'compare',
    'pollution index', 'air quality index', 'pm2.5', 'paris agreement', 'clean air act',
    'tip', 'advice', 'home', 'house', 'kitchen', 'garden', 'energy', 'water', 'waste'
]

def is_environmental_query(query):
    q = query.lower()
    return any(k in q for k in ENVIRONMENTAL_KEYWORDS)

def get_out_of_domain_response():
    return "I specialize in environmental topics only.\n\nPlease ask me about:\n• Environmental policies and regulations\n• Pollution index and air quality (AQI)\n• Carbon footprint\n• Climate change and environmental effects\n• Health effects of pollution\n• Sustainability tips\n• Compare pollution levels between cities"

def get_direct_answer(query):
    q = query.lower()
    if 'paris agreement' in q:
        return """The Paris Agreement is a legally binding international treaty on climate change.

Key points:
• Adopted by 196 parties at COP 21 in Paris on 12 December 2015
• Entered into force on 4 November 2016
• Goal: Limit global warming to well below 2°C, preferably to 1.5°C
• Requires countries to submit Nationally Determined Contributions (NDCs)
• Requires developed countries to provide climate finance"""
    if 'pm2.5' in q and ('respiratory' in q or 'health' in q):
        return """PM2.5 (fine particulate matter) affects respiratory health:

• Penetrates deep into lungs and bloodstream
• Causes inflammation and oxidative stress
• Triggers asthma attacks
• Worsens COPD and bronchitis
• Increases lung infections and cancer risk"""
    if 'clean air act' in q:
        return """The Clean Air Act (US) controls air pollution.

Key provisions:
• EPA sets National Ambient Air Quality Standards (NAAQS)
• Regulates emissions from stationary and mobile sources
• Cap-and-trade for acid rain
• First passed 1963, amended 1970, 1977, 1990"""
    return None

# ---------- MCP client (uses HTTPS for remote host) ----------
async def get_mcp_client():
    if st.session_state.mcp_client is None and not st.session_state.connection_attempted:
        st.session_state.connection_attempted = True
        mcp_host = os.getenv('MCP_HOST', 'greenmind-agent.onrender.com')
        try:
            client = MCPClient(host=mcp_host, port=443)
            connected = await client.connect()
            if connected:
                st.session_state.mcp_client = client
                st.session_state.mcp_connected = True
            else:
                st.session_state.mcp_connected = False
        except Exception as e:
            print(f"Error: {e}")
            st.session_state.mcp_connected = False
    return st.session_state.mcp_client

async def call_mcp_tool(tool_name: str, input_text: str, retry=0):
    client = await get_mcp_client()
    if client is None or not st.session_state.mcp_connected:
        return None, "Connection error"
    try:
        result = await asyncio.wait_for(
            client.call_tool(tool_name, input=input_text),
            timeout=45.0
        )
        if result and isinstance(result, str):
            if "no results" in result.lower() or "not found" in result.lower():
                return None, "no_data"
            if "ratelimit" in result.lower() or "unavailable" in result.lower():
                return None, "rate_limit"
        return result, "success"
    except asyncio.TimeoutError:
        if retry < 2:
            await asyncio.sleep(2)
            return await call_mcp_tool(tool_name, input_text, retry+1)
        return None, "timeout"
    except Exception as e:
        return None, str(e)

def clean_response(text):
    if not isinstance(text, str):
        return text
    text = re.sub(r'\[\s*Paragraph\s+\d+\s*\]', '', text)
    text = re.sub(r'TITLE:.*?\n', '', text)
    text = re.sub(r'SOURCE:.*?\n', '', text)
    text = re.sub(r'CONTENT:', '', text)
    return text.strip()

def is_comparison_query(query):
    return any(w in query.lower() for w in ['compare','comparison','versus','vs','difference between'])

def extract_cities(query):
    cities = ['delhi','mumbai','chennai','kolkata','bangalore','hyderabad',
              'new york','los angeles','chicago','london','paris','tokyo',
              'beijing','shanghai','sydney','melbourne','toronto','singapore']
    return [c for c in cities if c in query.lower()]

async def handle_comparison(query):
    ql = query.lower()
    cities = extract_cities(query) or (['delhi','mumbai'] if 'pollution' in ql else ['delhi','london'])
    call_carbon = 'carbon' in ql or 'footprint' in ql
    call_pollution = 'pollution' in ql or 'air quality' in ql or 'aqi' in ql
    if not call_carbon and not call_pollution:
        call_pollution = True
    results = {}
    for city in cities[:3]:
        if call_pollution:
            res, _ = await call_mcp_tool("Pollution_Health_Index", city)
            if res:
                results[f"aqi_{city}"] = res
        if call_carbon:
            res, _ = await call_mcp_tool("Carbon_Footprint_Calculator", city)
            if res:
                results[f"carbon_{city}"] = res
    return results, cities[:3], call_carbon, call_pollution

def format_comparison_results(results, cities, call_carbon, call_pollution):
    out = ["="*50, "ENVIRONMENTAL COMPARISON RESULTS", "="*50]
    for city in cities:
        out.append(f"\n📍 {city.upper()}\n" + "-"*30)
        if call_pollution and f"aqi_{city}" in results:
            txt = results[f"aqi_{city}"]
            m = re.search(r'AQI:\s*(\d+)', txt)
            if m:
                aqi = int(m.group(1))
                color = "🟢" if aqi<=50 else "🟡" if aqi<=100 else "🟠" if aqi<=150 else "🔴" if aqi<=200 else "🟣" if aqi<=300 else "⚫"
                out.append(f"  AQI: {aqi} {color}")
        if call_carbon and f"carbon_{city}" in results:
            txt = results[f"carbon_{city}"]
            m = re.search(r'(\d+\.?\d*)\s*tons', txt)
            if m:
                val = float(m.group(1))
                color = "🟢" if val<=2.0 else "🟡" if val<=5.0 else "🔴"
                out.append(f"  Carbon: {val} tons CO2/year {color}")
    out.extend(["\n"+"="*50, "Color Reference: 🟢 Good/Low   🟡 Moderate   🟠 Sensitive   🔴 Unhealthy   🟣 Very Unhealthy   ⚫ Hazardous"])
    return "\n".join(out)

# ---------- Welcome message and quote ----------
if st.session_state.messages == []:
    quotes = [
        {"text": "The earth is what we all have in common.", "author": "Wendell Berry"},
        {"text": "We borrow the earth from our children.", "author": "Native American Proverb"},
        {"text": "The greatest threat is believing someone else will save it.", "author": "Robert Swan"}
    ]
    st.session_state.quote_data = quotes[datetime.now().day % len(quotes)]
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm GreenMind.\n\nAsk me about:\n• Pollution Index (AQI)\n• Carbon Footprint\n• Environmental Policies\n• Health Effects\n• Climate Impacts\n• Compare Cities\n• Sustainability Tips\n\nHow can I help protect our planet today?"
    }]

# ---------- Main processing ----------
async def process_with_mcp_async(user_query):
    ql = user_query.lower()

    # 1. Tips (always allowed)
    tip_keywords = ['tip','advice','sustainable','eco-friendly','home','house','kitchen','garden','recycle','plastic','waste','energy','water']
    if any(w in ql for w in tip_keywords):
        res, stat = await call_mcp_tool("Sustainability_Tips", user_query)
        if stat == "success" and res:
            return res, "Tips"
        return "Simple tip: Reduce, Reuse, Recycle! Every small action helps.", "Tips"

    # 2. Domain check
    if not is_environmental_query(user_query):
        return get_out_of_domain_response(), "OutOfDomain"

    # 3. Direct answers for known policies
    direct = get_direct_answer(user_query)
    if direct:
        return direct, "Direct"

    # 4. Comparison
    if is_comparison_query(user_query) or len(extract_cities(user_query)) >= 2 or 'compare' in ql:
        results, cities, cc, cp = await handle_comparison(user_query)
        if results:
            return format_comparison_results(results, cities, cc, cp), "Comparison"
        return "Unable to compare. Try 'compare pollution in Delhi and Mumbai'.", "Comparison"

    # 5. Disease/health
    if any(w in ql for w in ['disease','health','cancer','respiratory','asthma','bronchitis','cholera','typhoid','waterborne']):
        res, stat = await call_mcp_tool("Environmental_Effects_RAG", user_query)
        if stat == "success" and res and len(res)>50:
            return res, "Effects_RAG"
        if 'water' in ql and 'pollution' in ql:
            return "Water pollution causes cholera, typhoid, dysentery, hepatitis A, giardiasis.\nPrevention: clean water, sanitation.", "Effects_Fallback"
        return "Air pollution can cause asthma, bronchitis, lung cancer. Water pollution causes cholera, typhoid, dysentery.", "Effects_Fallback"

    # 6. Pollution index
    if any(w in ql for w in ['air quality','aqi','pollution','polluion','polution','pollution index']):
        res, stat = await call_mcp_tool("Pollution_Health_Index", user_query)
        if stat == "success" and res:
            return res, "Pollution"
        return "Unable to fetch pollution data. Please try a different location.", "Pollution"

    # 7. Carbon footprint
    if any(w in ql for w in ['carbon','footprint','co2','emission']):
        res, stat = await call_mcp_tool("Carbon_Footprint_Calculator", user_query)
        if stat == "success" and res:
            return res, "Carbon"
        return "Unable to calculate carbon footprint. Try a specific city like 'Delhi'.", "Carbon"

    # 8. Other effects (climate change, deforestation)
    if any(w in ql for w in ['effect','impact','climate change','global warming','deforestation']):
        res, stat = await call_mcp_tool("Environmental_Effects_RAG", user_query)
        if stat == "success" and res and len(res)>50:
            return res, "Effects_RAG"
        return "Climate change causes rising temperatures, sea level rise, extreme weather, biodiversity loss. Deforestation releases CO2 and reduces carbon sinks.", "Effects_Fallback"

    # 9. Policies (RAG with fallback to web search)
    if any(w in ql for w in ['policy','act','regulation','law','treaty','clean air','clean water']):
        res, stat = await call_mcp_tool("Environmental_Policies_RAG", user_query)
        if stat == "success" and res and len(res)>50:
            return res, "Policies_RAG"
        # fallback to web search
        res2, stat2 = await call_mcp_tool("Web_Search", user_query)
        if stat2 == "success" and res2 and "unavailable" not in res2.lower():
            return res2, "Web_Search"
        return "No policy information found. Try a more specific query (e.g., 'Paris Agreement goals').", "Policies_Fallback"

    # 10. Wikipedia
    if 'wikipedia' in ql:
        res, stat = await call_mcp_tool("Wikipedia_Knowledge", user_query)
        if stat == "success" and res:
            return res, "Wikipedia"
        return "No Wikipedia article found. Try different terms.", "Wikipedia"

    # 11. Web search (general)
    res, stat = await call_mcp_tool("Web_Search", user_query)
    if stat == "success" and res and "unavailable" not in res.lower():
        return res, "Web_Search"

    return "I couldn't find information on that topic. Please try a different question.", "Default"

def process_with_mcp(query):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result, tool = loop.run_until_complete(process_with_mcp_async(query))
    loop.close()
    return result, tool

# ---------- UI ----------
# Header with inline style for guaranteed readability
st.markdown("""
<div class="main-header">
    <h1>🌿 GreenMind 🌍</h1>
    <h3 style="background-color: rgba(0,0,0,0.35); display: inline-block; padding: 0.2rem 1rem; border-radius: 30px; color: #FFFFFF; text-shadow: 1px 1px 1px rgba(0,0,0,0.2);">Your Environmental Sustainability Advisor</h3>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("About GreenMind")
    st.markdown("Environmental sustainability advisor for:\n• Policies\n• Pollution Index (AQI)\n• Carbon Footprint\n• Health Effects\n• Climate Impacts\n• City Comparisons\n• Sustainability Tips")
    st.markdown("---")
    if st.session_state.mcp_connected:
        st.markdown('<div class="status-box connected">✅ MCP Server Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box disconnected">⚠️ MCP Server Connecting...</div>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# Show welcome message
if st.session_state.messages:
    with st.chat_message("assistant"):
        if st.session_state.quote_data:
            st.markdown(f'<div class="elegant-quote"><div class="quote-text">"{st.session_state.quote_data["text"]}"</div><div class="quote-author">— {st.session_state.quote_data["author"]}</div></div>', unsafe_allow_html=True)
        st.markdown(st.session_state.messages[0]["content"])

for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask me about environmental sustainability...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("🌱 GreenMind is thinking..."):
            response, tool = process_with_mcp(prompt)
            # Wrap every response in a monospace <pre> for consistent font
            st.markdown(f'<pre style="font-family: \'Courier New\', Courier, monospace; font-size: 1rem; background-color: #f5f5f5; padding: 12px; border-radius: 8px; white-space: pre-wrap;">{response}</pre>', unsafe_allow_html=True)
            if tool and tool not in ("OutOfDomain","Default"):
                st.caption(f"🔧 Tool: {tool}")
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

st.markdown("""
<div class="footer">
    🌱 GreenMind - Every small action counts towards a greener planet 🌍
</div>
""", unsafe_allow_html=True)