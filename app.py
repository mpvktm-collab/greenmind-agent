# app.py - Complete version with proper session state initialization order
import streamlit as st
import sys
import os
import asyncio
import re
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.mcp.client.mcp_client import MCPClient
from config import Config

# ============================================
# STEP 1: INITIALIZE ALL SESSION STATE FIRST
# ============================================
# This MUST be done before any st.session_state access

# Initialize mcp client state
if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = None
if "mcp_connected" not in st.session_state:
    st.session_state.mcp_connected = False
if "connection_attempted" not in st.session_state:
    st.session_state.connection_attempted = False

# Initialize messages state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize quote data state
if "quote_data" not in st.session_state:
    st.session_state.quote_data = None

# ============================================
# STEP 2: PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="GreenMind - Environmental Sustainability Advisor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# STEP 3: CUSTOM CSS
# ============================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #4CAF50 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .main-header h1 { font-size: 2rem; margin-bottom: 0; }
    .main-header h3 { font-size: 0.85rem; font-weight: 300; font-style: italic; }
    .elegant-quote {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: center;
        border-left: 6px solid #2E7D32;
    }
    .quote-text { font-size: 1.1rem; font-style: italic; color: #1B5E20; }
    .quote-author { font-size: 0.8rem; color: #2E7D32; text-align: right; }
    .status-box { padding: 0.5rem; border-radius: 8px; margin-bottom: 0.8rem; text-align: center; }
    .connected { background-color: #d4edda; color: #155724; }
    .disconnected { background-color: #f8d7da; color: #721c24; }
    .footer { text-align: center; color: #666; padding: 0.5rem; margin-top: 1rem; font-size: 0.7rem; }
    .stChatMessage { background-color: #ffffff; border-radius: 10px; padding: 8px; margin: 4px 0; border: 1px solid #e0e0e0; }
    .stChatMessage pre, .stChatMessage code {
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# STEP 4: ENVIRONMENTAL KEYWORDS
# ============================================
ENVIRONMENTAL_KEYWORDS = [
    'environment', 'climate', 'pollution', 'polluion', 'polution', 'air quality',
    'sustainable', 'carbon', 'footprint', 'co2', 'emission', 'aqi',
    'water', 'waste', 'plastic', 'forest', 'biodiversity', 'green',
    'policy', 'act', 'regulation', 'law', 'treaty', 'agreement',
    'effect', 'impact', 'health', 'disease', 'cancer', 'respiratory',
    'diseases', 'waterborne', 'cholera', 'typhoid', 'asthma', 'bronchitis',
    'wikipedia', 'eco-friendly', 'transportation', 'recycle', 'compare',
    'pollution index', 'air quality index'
]

def is_environmental_query(query):
    query_lower = query.lower()
    for keyword in ENVIRONMENTAL_KEYWORDS:
        if keyword in query_lower:
            return True
    return False

def get_out_of_domain_response():
    return """I specialize in environmental topics only.

Please ask me about:
• Environmental policies and regulations
• Pollution index and air quality (AQI)
• Carbon footprint
• Climate change and environmental effects
• Health effects of pollution
• Sustainability tips
• Compare pollution levels between cities"""

async def get_mcp_client():
    if st.session_state.mcp_client is None and not st.session_state.connection_attempted:
        st.session_state.connection_attempted = True
       # mcp_host = os.getenv('MCP_HOST', 'greenmind-mcp-server.onrender.com')
        mcp_host = os.getenv('MCP_HOST', 'localhost:8000')
        
        try:
            client = MCPClient(host=mcp_host)
            connected = await client.connect()
            if connected:
                st.session_state.mcp_client = client
                st.session_state.mcp_connected = True
            else:
                st.session_state.mcp_connected = False
        except Exception as e:
            print(f"Error: {str(e)}")
            st.session_state.mcp_connected = False
    
    return st.session_state.mcp_client

async def call_mcp_tool(tool_name: str, input_text: str, retry=0):
    client = await get_mcp_client()
    
    if client is None or not st.session_state.mcp_connected:
        return None, "Connection error"
    
    try:
        result = await asyncio.wait_for(
            client.call_tool(tool_name, input=input_text),
            timeout=60.0
        )
        if result and isinstance(result, str):
            if "no results" in result.lower() or "not found" in result.lower():
                return None, "no_data"
        return result, "success"
    except asyncio.TimeoutError:
        if retry < 2:
            await asyncio.sleep(2)
            return await call_mcp_tool(tool_name, input_text, retry + 1)
        return None, "timeout"
    except Exception as e:
        return None, f"Error: {str(e)}"

def clean_response(text):
    if not isinstance(text, str):
        return text
    text = re.sub(r'\[\s*Paragraph\s+\d+\s*\]', '', text)
    text = re.sub(r'TITLE:.*?\n', '', text)
    text = re.sub(r'SOURCE:.*?\n', '', text)
    text = re.sub(r'CONTENT:', '', text)
    return text.strip()

def is_comparison_query(query):
    query_lower = query.lower()
    indicators = ['compare', 'comparison', 'versus', 'vs', 'difference between']
    return any(indicator in query_lower for indicator in indicators)

def extract_cities(query):
    cities = ['delhi', 'mumbai', 'chennai', 'kolkata', 'bangalore', 'hyderabad',
              'new york', 'los angeles', 'chicago', 'london', 'paris', 'tokyo',
              'beijing', 'shanghai', 'sydney', 'melbourne', 'toronto', 'singapore']
    query_lower = query.lower()
    found = []
    for city in cities:
        if city in query_lower:
            found.append(city)
    return found

async def handle_comparison(query):
    query_lower = query.lower()
    cities = extract_cities(query)
    
    if not cities:
        if 'pollution' in query_lower or 'aqi' in query_lower:
            cities = ['delhi', 'mumbai']
        elif 'carbon' in query_lower:
            cities = ['delhi', 'mumbai']
        else:
            cities = ['delhi', 'mumbai']
    
    results = {}
    call_carbon = 'carbon' in query_lower or 'footprint' in query_lower
    call_pollution = 'pollution' in query_lower or 'air quality' in query_lower or 'aqi' in query_lower
    
    if not call_carbon and not call_pollution:
        call_pollution = True
    
    for city in cities[:3]:
        if call_pollution:
            result, status = await call_mcp_tool("Pollution_Health_Index", city)
            if status == "success" and result:
                results[f"aqi_{city}"] = result
        if call_carbon:
            result, status = await call_mcp_tool("Carbon_Footprint_Calculator", city)
            if status == "success" and result:
                results[f"carbon_{city}"] = result
    
    return results, cities[:3], call_carbon, call_pollution

def format_comparison_results(results, cities, call_carbon, call_pollution):
    output = []
    output.append("=" * 50)
    output.append("ENVIRONMENTAL COMPARISON RESULTS")
    output.append("=" * 50)
    
    for city in cities:
        output.append(f"\n📍 {city.upper()}")
        output.append("-" * 30)
        
        if call_pollution and f"aqi_{city}" in results:
            text = str(results[f"aqi_{city}"])
            aqi_match = re.search(r'AQI:\s*(\d+)', text)
            if aqi_match:
                aqi_value = int(aqi_match.group(1))
                if aqi_value <= 50:
                    color = "🟢"
                    level = "Good"
                elif aqi_value <= 100:
                    color = "🟡"
                    level = "Moderate"
                elif aqi_value <= 150:
                    color = "🟠"
                    level = "Unhealthy for Sensitive Groups"
                elif aqi_value <= 200:
                    color = "🔴"
                    level = "Unhealthy"
                elif aqi_value <= 300:
                    color = "🟣"
                    level = "Very Unhealthy"
                else:
                    color = "⚫"
                    level = "Hazardous"
                output.append(f"  AQI: {aqi_value} {color} ({level})")
            
            pm25_match = re.search(r'PM2\.5:\s*(\d+)', text)
            if pm25_match:
                output.append(f"  PM2.5: {pm25_match.group(1)} μg/m³")
        
        if call_carbon and f"carbon_{city}" in results:
            text = str(results[f"carbon_{city}"])
            match = re.search(r'(\d+\.?\d*)\s*tons', text)
            if match:
                carbon_value = float(match.group(1))
                if carbon_value <= 2.0:
                    color = "🟢"
                    level = "Low Impact"
                elif carbon_value <= 5.0:
                    color = "🟡"
                    level = "Moderate Impact"
                else:
                    color = "🔴"
                    level = "High Impact"
                output.append(f"  Carbon: {carbon_value} tons CO2/year {color} ({level})")
    
    output.append("\n" + "=" * 50)
    output.append("\nColor Reference:")
    output.append("🟢 Good / Low Impact    🟡 Moderate    🟠 Sensitive Groups")
    output.append("🔴 Unhealthy / High Impact    🟣 Very Unhealthy    ⚫ Hazardous")
    output.append("=" * 50)
    
    return "\n".join(output)

# ============================================
# STEP 5: INITIALIZE WELCOME MESSAGES AND QUOTES
# ============================================
if st.session_state.messages == []:
    welcome_quotes = [
        {"text": "The earth is what we all have in common.", "author": "Wendell Berry"},
        {"text": "We borrow the earth from our children.", "author": "Native American Proverb"},
        {"text": "The greatest threat is believing someone else will save it.", "author": "Robert Swan"}
    ]
    today_quote = welcome_quotes[datetime.now().day % len(welcome_quotes)]
    
    st.session_state.quote_data = today_quote
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm GreenMind.\n\nAsk me about:\n• Pollution Index (AQI)\n• Carbon Footprint\n• Environmental Policies\n• Health Effects of Pollution\n• Climate Change Impacts\n• Compare Cities\n\nHow can I help protect our planet today?"
    }]

# ============================================
# STEP 6: PROCESS QUERY FUNCTION
# ============================================
async def process_with_mcp_async(user_query):
    query_lower = user_query.lower()
    
    if not is_environmental_query(user_query):
        return get_out_of_domain_response(), "OutOfDomain"
    
    # Comparison query - check FIRST
    if is_comparison_query(user_query) or len(extract_cities(query_lower)) >= 2 or 'compare' in query_lower:
        results, cities, call_carbon, call_pollution = await handle_comparison(user_query)
        if results:
            return format_comparison_results(results, cities, call_carbon, call_pollution), "Comparison_Tool"
        return "Unable to compare. Try 'compare pollution in Delhi and Mumbai'.", "Comparison_Tool"
    
    # Disease/health queries
    disease_keywords = ['disease', 'health', 'cancer', 'respiratory', 'asthma', 'bronchitis', 
                        'cholera', 'typhoid', 'waterborne', 'illness', 'sick', 'diseases']
    if any(word in query_lower for word in disease_keywords):
        result, status = await call_mcp_tool("Environmental_Effects_RAG", user_query)
        if status == "success" and result and len(str(result)) > 50:
            return result, "Environmental_Effects_RAG"
        if 'water' in query_lower and 'pollution' in query_lower:
            return """Water pollution causes several diseases:

Common waterborne diseases:
• Cholera - caused by contaminated water
• Typhoid fever - bacterial infection from contaminated water
• Dysentery - severe diarrhea from contaminated water
• Hepatitis A - viral liver infection
• Giardiasis - parasitic infection
• Cryptosporidiosis - parasitic infection

Prevention: Drink clean water, proper sanitation, water treatment."""
        result2, status2 = await call_mcp_tool("Web_Search", user_query)
        if status2 == "success" and result2:
            return result2, "Web_Search"
        return "Water pollution can cause cholera, typhoid, dysentery, hepatitis A, and other waterborne diseases. Air pollution can cause asthma, bronchitis, lung cancer, and respiratory infections.", "Effects_Fallback"
    
    # Wikipedia queries
    if 'wikipedia' in query_lower:
        result, status = await call_mcp_tool("Wikipedia_Knowledge", user_query)
        if status == "success" and result:
            return result, "Wikipedia_Knowledge"
        return "No Wikipedia article found. Try different search terms.", "Wikipedia_Knowledge"
    
    # Pollution queries
    pollution_indicators = ['air quality', 'aqi', 'pollution', 'polluion', 'polution', 'pollution index']
    if any(word in query_lower for word in pollution_indicators):
        result, status = await call_mcp_tool("Pollution_Health_Index", user_query)
        if status == "success" and result:
            return result, "Pollution_Health_Index"
        return "Unable to fetch pollution data. Please try a different location.", "Pollution_Health_Index"
    
    # Carbon footprint queries
    if any(word in query_lower for word in ['carbon', 'footprint', 'co2', 'emission']):
        result, status = await call_mcp_tool("Carbon_Footprint_Calculator", user_query)
        if status == "success" and result:
            return result, "Carbon_Footprint_Calculator"
        return "Unable to calculate carbon footprint. Try a specific city like 'Delhi'.", "Carbon_Footprint_Calculator"
    
    # Effects queries
    if any(word in query_lower for word in ['effect', 'impact', 'climate change', 'global warming', 'deforestation']):
        result, status = await call_mcp_tool("Environmental_Effects_RAG", user_query)
        if status == "success" and result and len(str(result)) > 50:
            return result, "Environmental_Effects_RAG"
        result2, status2 = await call_mcp_tool("Web_Search", user_query)
        if status2 == "success" and result2:
            return result2, "Web_Search"
        return "No environmental effects information found.", "Effects_RAG"
    
    # Policy queries
    if any(word in query_lower for word in ['policy', 'act', 'regulation', 'law', 'treaty', 'clean air', 'clean water']):
        result, status = await call_mcp_tool("Environmental_Policies_RAG", user_query)
        if status == "success" and result and len(str(result)) > 50:
            return result, "Environmental_Policies_RAG"
        result2, status2 = await call_mcp_tool("Web_Search", user_query)
        if status2 == "success" and result2:
            return result2, "Web_Search"
        return "No policy information found. Try 'Clean Air Act' or be more specific.", "Policies_RAG"
    
    # Tips queries
    if any(word in query_lower for word in ['tip', 'advice', 'sustainable', 'eco-friendly', 'reduce', 'recycle']):
        transport_keywords = ['transport', 'transportation', 'bike', 'walk', 'car', 'bus', 'train']
        if any(word in query_lower for word in transport_keywords):
            result, status = await call_mcp_tool("Sustainability_Tips", "transport")
            if status == "success" and result:
                return result, "Sustainability_Tips"
        result, status = await call_mcp_tool("Sustainability_Tips", user_query)
        if status == "success" and result:
            return result, "Sustainability_Tips"
        return "Simple tip: Reduce, Reuse, Recycle! Every small action helps our planet.", "Sustainability_Tips"
    
    # Web search fallback
    result, status = await call_mcp_tool("Web_Search", user_query)
    if status == "success" and result:
        return result, "Web_Search"
    
    return "I couldn't find information on that topic. Please try a different question.", "Default"

def process_with_mcp(user_query):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result, tool = loop.run_until_complete(process_with_mcp_async(user_query))
    loop.close()
    return result, tool

# ============================================
# STEP 7: RENDER UI
# ============================================

# Header
st.markdown("""
<div class="main-header">
    <h1>🌿 GreenMind 🌍</h1>
    <h3>Your Environmental Sustainability Advisor</h3>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("About GreenMind")
    st.markdown("Environmental sustainability advisor for:")
    st.markdown("• Policies & Regulations")
    st.markdown("• Pollution Index (AQI)")
    st.markdown("• Carbon Footprint")
    st.markdown("• Health Effects")
    st.markdown("• Climate Impacts")
    st.markdown("• City Comparisons")
    
    st.markdown("---")
    if st.session_state.mcp_connected:
        st.markdown('<div class="status-box connected">✅ MCP Server Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box disconnected">⚠️ MCP Server Connecting...</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# Display welcome message
if st.session_state.messages:
    with st.chat_message("assistant"):
        if st.session_state.quote_data:
            quote_html = f'''
            <div class="elegant-quote">
                <div class="quote-text">"{st.session_state.quote_data["text"]}"</div>
                <div class="quote-author">— {st.session_state.quote_data["author"]}</div>
            </div>
            '''
            st.markdown(quote_html, unsafe_allow_html=True)
        st.markdown(st.session_state.messages[0]["content"])

# Chat history
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Ask me about environmental sustainability...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🌱 GreenMind is thinking..."):
            response, tool_used = process_with_mcp(prompt)
            st.markdown(f'<pre style="font-family: monospace; font-size: 0.85rem; background-color: #f5f5f5; padding: 12px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap;">{response}</pre>', unsafe_allow_html=True)
            if tool_used and tool_used != "OutOfDomain":
                st.caption(f"🔧 Tool: {tool_used}")
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Footer
st.markdown("""
<div class="footer">
    🌱 GreenMind - Every small action counts towards a greener planet 🌍
</div>
""", unsafe_allow_html=True)