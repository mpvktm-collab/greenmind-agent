# app.py - Complete version with fixed tips routing 
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
# INITIALIZE SESSION STATE FIRST
# ============================================
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

# Page configuration
st.set_page_config(
    page_title="GreenMind - Environmental Sustainability Advisor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for sticky header and improved readability
st.markdown("""
<style>
    /* Sticky header - always visible at top */
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
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .main-header h1 { 
        font-size: 2rem; 
        margin-bottom: 0.2rem; 
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-header h3 { 
        font-size: 0.85rem; 
        font-weight: 400; 
        font-style: italic; 
        margin-bottom: 0;
        background-color: rgba(0,0,0,0.25);
        display: inline-block;
        padding: 0.2rem 1rem;
        border-radius: 30px;
        color: #FFFFFF;
        text-shadow: 1px 1px 1px rgba(0,0,0,0.2);
    }
    
    /* Consistent font for all outputs */
    .stChatMessage p, .stChatMessage div, .stMarkdown, .stMarkdown pre {
        font-size: 1rem !important;
        font-family: 'Courier New', Courier, monospace !important;
        line-height: 1.5 !important;
    }
    
    .stChatMessage pre {
        font-size: 1rem !important;
        font-family: 'Courier New', Courier, monospace !important;
        background-color: #f5f5f5;
        padding: 12px;
        border-radius: 8px;
        white-space: pre-wrap;
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

# Environmental keywords (including 'home' and other tip-related terms)
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
    query_lower = query.lower()
    for keyword in ENVIRONMENTAL_KEYWORDS:
        if keyword in query_lower:
            return True
    return False

def get_out_of_domain_response():
    return "I specialize in environmental topics only.\n\nPlease ask me about:\n• Environmental policies and regulations\n• Pollution index and air quality (AQI)\n• Carbon footprint\n• Climate change and environmental effects\n• Health effects of pollution\n• Sustainability tips\n• Compare pollution levels between cities"

def get_direct_answer(query):
    query_lower = query.lower()
    
    if 'paris agreement' in query_lower:
        return """The Paris Agreement is a legally binding international treaty on climate change.

Key points:
• Adopted by 196 parties at COP 21 in Paris on 12 December 2015
• Entered into force on 4 November 2016
• Goal: Limit global warming to well below 2°C, preferably to 1.5°C
• Requires countries to submit Nationally Determined Contributions (NDCs)
• Requires developed countries to provide climate finance"""
    
    if 'pm2.5' in query_lower and ('respiratory' in query_lower or 'health' in query_lower):
        return """PM2.5 (fine particulate matter) affects respiratory health in several ways:

Health Effects:
• Penetrates deep into lungs and enters bloodstream
• Causes inflammation and oxidative stress
• Triggers asthma attacks
• Worsens chronic bronchitis and COPD
• Increases risk of lung infections
• Linked to lung cancer development"""
    
    if 'clean air act' in query_lower:
        return """The Clean Air Act is a United States federal law designed to control air pollution.

Key provisions:
• Authorizes EPA to set National Ambient Air Quality Standards (NAAQS)
• Regulates emissions from stationary and mobile sources
• Established cap-and-trade program for acid rain
• Requires states to develop implementation plans"""
    
    return None

async def get_mcp_client():
    if st.session_state.mcp_client is None and not st.session_state.connection_attempted:
        st.session_state.connection_attempted = True
        mcp_host = os.getenv('MCP_HOST', 'localhost')
        
        try:
            client = MCPClient(host=mcp_host, port=8000)
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
            cities = ['delhi', 'london', 'new york']
        else:
            cities = ['delhi', 'mumbai', 'london']
    
    results = {}
    call_carbon = 'carbon' in query_lower or 'footprint' in query_lower
    call_pollution = 'pollution' in query_lower or 'air quality' in query_lower or 'aqi' in query_lower
    
    if not call_carbon and not call_pollution:
        call_carbon = True
        call_pollution = True
    
    for city in cities[:3]:
        if call_carbon:
            result, status = await call_mcp_tool("Carbon_Footprint_Calculator", city)
            if status == "success" and result:
                results[f"carbon_{city}"] = result
        if call_pollution:
            result, status = await call_mcp_tool("Pollution_Health_Index", city)
            if status == "success" and result:
                results[f"aqi_{city}"] = result
    
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

# Initialize welcome messages
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
        "content": "Hello! I'm GreenMind.\n\nAsk me about:\n• Pollution Index (AQI)\n• Carbon Footprint\n• Environmental Policies\n• Health Effects of Pollution\n• Climate Change Impacts\n• Compare Cities\n• Sustainability Tips\n\nHow can I help protect our planet today?"
    }]

async def process_with_mcp_async(user_query):
    query_lower = user_query.lower()
    
    # FIRST: Check for tips queries (before out-of-domain check)
    tip_keywords = ['tip', 'advice', 'sustainable', 'eco-friendly', 'home', 'house', 'kitchen', 'garden', 'recycle', 'plastic', 'waste', 'energy', 'water']
    if any(word in query_lower for word in tip_keywords):
        result, status = await call_mcp_tool("Sustainability_Tips", user_query)
        if status == "success" and result:
            return result, "Sustainability_Tips"
        return "Simple tip: Reduce, Reuse, Recycle! Every small action helps our planet.", "Sustainability_Tips"
    
    # THEN check if query is environmental
    if not is_environmental_query(user_query):
        return get_out_of_domain_response(), "OutOfDomain"
    
    # Check for direct answers
    direct_answer = get_direct_answer(user_query)
    if direct_answer:
        return direct_answer, "Direct_Answer"
    
    # Comparison query
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

Prevention: Drink clean water, proper sanitation, water treatment.""", "Effects_Fallback"
        return "Air pollution can cause asthma, bronchitis, lung cancer, and respiratory infections. Water pollution can cause cholera, typhoid, and dysentery.", "Effects_Fallback"
    
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
        return "Climate change causes rising temperatures, sea level rise, extreme weather events, and biodiversity loss.", "Effects_Fallback"
    
    # Policy queries
    if any(word in query_lower for word in ['policy', 'act', 'regulation', 'law', 'treaty', 'clean air', 'clean water']):
        result, status = await call_mcp_tool("Environmental_Policies_RAG", user_query)
        if status == "success" and result and len(str(result)) > 50:
            return result, "Environmental_Policies_RAG"
        return "The Clean Air Act regulates air emissions. The Clean Water Act regulates water pollution. The Paris Agreement addresses climate change.", "Policies_Fallback"
    
    # Wikipedia queries
    if 'wikipedia' in query_lower:
        result, status = await call_mcp_tool("Wikipedia_Knowledge", user_query)
        if status == "success" and result:
            return result, "Wikipedia_Knowledge"
        return "No Wikipedia article found. Try different search terms.", "Wikipedia_Knowledge"
    
    # Web search fallback
    result, status = await call_mcp_tool("Web_Search", user_query)
    if status == "success" and result and "unavailable" not in result.lower():
        return result, "Web_Search"
    
    return "I couldn't find information on that topic. Please try a different question.", "Default"

def process_with_mcp(user_query):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result, tool = loop.run_until_complete(process_with_mcp_async(user_query))
    loop.close()
    return result, tool

# Header - Sticky with improved readability
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
    st.markdown("• Sustainability Tips")
    
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
            st.markdown(f'<pre style="font-family: Courier New, Courier, monospace; font-size: 1rem; background-color: #f5f5f5; padding: 12px; border-radius: 8px; overflow-x: auto; white-space: pre-wrap;">{response}</pre>', unsafe_allow_html=True)
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