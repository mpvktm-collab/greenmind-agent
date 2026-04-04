# app.py - Complete version with all required tools
import streamlit as st
import sys
import os
import asyncio
import re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.mcp.client.mcp_client import MCPClient
from config import Config

# Initialize session state
if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = None
    st.session_state.mcp_connected = False
    st.session_state.connection_attempted = False

st.set_page_config(
    page_title="GreenMind - Environmental Sustainability Advisor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .main-header h1 { font-size: 2.2rem; margin-bottom: 0.3rem; }
    .main-header h3 { font-size: 1.2rem; font-weight: 300; font-style: italic; }
    .elegant-quote {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8f0e8 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        text-align: center;
        border-left: 6px solid #2E7D32;
    }
    .quote-text { font-size: 1.3rem; font-style: italic; color: #1e3a2e; }
    .quote-author { font-size: 1rem; color: #4a7850; text-align: right; margin-top: 0.5rem; }
    .status-box { padding: 0.8rem; border-radius: 8px; margin-bottom: 1rem; text-align: center; }
    .connected { background-color: #d4edda; color: #155724; }
    .disconnected { background-color: #f8d7da; color: #721c24; }
    .footer { text-align: center; color: #666; padding: 1rem; margin-top: 2rem; border-top: 1px solid #e0e0e0; }
</style>
""", unsafe_allow_html=True)

# Welcome message with environmental quote
if 'messages' not in st.session_state:
    welcome_quotes = [
        {"text": "The earth is what we all have in common.", "author": "Wendell Berry"},
        {"text": "We do not inherit the earth from our ancestors; we borrow it from our children.", "author": "Native American Proverb"},
        {"text": "The greatest threat to our planet is the belief that someone else will save it.", "author": "Robert Swan"},
        {"text": "The environment is where we all meet; where we all have a mutual interest.", "author": "Lady Bird Johnson"}
    ]
    today_quote = welcome_quotes[datetime.now().day % len(welcome_quotes)]
    
    st.session_state.quote_data = today_quote
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm GreenMind, your environmental sustainability advisor.\n\nI can help you with:\n• Environmental Policies and Regulations\n• Environmental Effects and Health Impacts\n• Current Environmental News (Web Search)\n• Pollution Index and Air Quality (AQI)\n• Carbon Footprint Calculations\n• Sustainability Tips\n• City Comparisons\n\nHow can I help you protect our planet today?"
    }]

MAJOR_CITIES = ['delhi', 'mumbai', 'chennai', 'hyderabad', 'kolkata', 'bangalore', 'new york', 'los angeles', 'chicago', 'london', 'paris', 'tokyo', 'beijing', 'shanghai']

async def get_mcp_client():
    if st.session_state.mcp_client is None and not st.session_state.connection_attempted:
        st.session_state.connection_attempted = True
        mcp_host = os.getenv('MCP_HOST', 'greenmind-mcp-server.onrender.com')
        
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

async def call_mcp_tool(tool_name: str, input_text: str):
    client = await get_mcp_client()
    
    if client is None or not st.session_state.mcp_connected:
        return "Error: Could not connect to MCP Server. Make sure it's running."
    
    try:
        result = await asyncio.wait_for(
            client.call_tool(tool_name, input=input_text),
            timeout=90.0
        )
        return result
    except asyncio.TimeoutError:
        return "The server is waking up from inactivity. Please try again in a moment."
    except Exception as e:
        print(f"Error: {str(e)}")
        st.session_state.mcp_client = None
        st.session_state.mcp_connected = False
        return f"Error: {str(e)}"

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
    query_lower = query.lower()
    return [city for city in MAJOR_CITIES if city in query_lower]

async def handle_comparison(query):
    query_lower = query.lower()
    cities = extract_cities(query)
    if not cities:
        cities = ['delhi', 'mumbai', 'london']
    
    results = {}
    call_carbon = 'carbon' in query_lower or 'footprint' in query_lower
    call_pollution = 'pollution' in query_lower or 'air quality' in query_lower or 'aqi' in query_lower
    
    if not call_carbon and not call_pollution:
        call_carbon = True
        call_pollution = True
    
    for city in cities[:3]:
        if call_carbon:
            result = await call_mcp_tool("Carbon_Footprint_Calculator", city)
            results[f"carbon_{city}"] = result
        if call_pollution:
            result = await call_mcp_tool("Pollution_Health_Index", city)
            results[f"aqi_{city}"] = result
    
    return results, cities, call_carbon, call_pollution

def format_comparison_results(results, cities, call_carbon, call_pollution):
    output = ["=" * 50, "ENVIRONMENTAL COMPARISON RESULTS", "=" * 50]
    for city in cities[:3]:
        output.append(f"\nCITY: {city.upper()}")
        output.append("-" * 30)
        if call_pollution and f"aqi_{city}" in results:
            aqi_text = str(results[f"aqi_{city}"])
            aqi_match = re.search(r'AQI:\s*(\d+)', aqi_text)
            if aqi_match:
                output.append(f"AQI: {aqi_match.group(1)}")
        if call_carbon and f"carbon_{city}" in results:
            carbon_text = str(results[f"carbon_{city}"])
            carbon_match = re.search(r'(\d+\.?\d*)\s*tons', carbon_text)
            if carbon_match:
                output.append(f"Carbon Footprint: {carbon_match.group(1)} tons CO2/year")
    output.append("\n" + "=" * 50)
    return "\n".join(output)

async def process_with_mcp_async(user_query):
    query_lower = user_query.lower()
    
    # Comparison query
    if is_comparison_query(user_query) or len(extract_cities(user_query)) >= 2:
        results, cities, call_carbon, call_pollution = await handle_comparison(user_query)
        if results:
            return format_comparison_results(results, cities, call_carbon, call_pollution), "Comparison_Tool"
    
    # Route to appropriate tool based on query
    if any(word in query_lower for word in ['policy', 'act', 'regulation', 'law', 'agreement', 'treaty']):
        result = await call_mcp_tool("Environmental_Policies_RAG", user_query)
        return clean_response(result), "Environmental_Policies_RAG"
    
    if any(word in query_lower for word in ['effect', 'impact', 'health', 'disease', 'respiratory', 'cancer', 'degradation']):
        result = await call_mcp_tool("Environmental_Effects_RAG", user_query)
        return clean_response(result), "Environmental_Effects_RAG"
    
    if any(word in query_lower for word in ['search', 'news', 'current', 'recent']):
        result = await call_mcp_tool("Web_Search", user_query)
        return result, "Web_Search"
    
    if any(word in query_lower for word in ['wikipedia']):
        result = await call_mcp_tool("Wikipedia_Knowledge", user_query)
        return result, "Wikipedia_Knowledge"
    
    if any(word in query_lower for word in ['air quality', 'aqi', 'pollution index', 'pollution of']):
        result = await call_mcp_tool("Pollution_Health_Index", user_query)
        return result, "Pollution_Health_Index"
    
    if any(word in query_lower for word in ['carbon', 'footprint', 'co2', 'emission']):
        result = await call_mcp_tool("Carbon_Footprint_Calculator", user_query)
        return result, "Carbon_Footprint_Calculator"
    
    if any(word in query_lower for word in ['tip', 'advice', 'sustainable']):
        result = await call_mcp_tool("Sustainability_Tips", user_query)
        return result, "Sustainability_Tips"
    
    # Default to policies RAG
    result = await call_mcp_tool("Environmental_Policies_RAG", user_query)
    return clean_response(result), "Environmental_Policies_RAG"

def process_with_mcp(user_query):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result, tool = loop.run_until_complete(process_with_mcp_async(user_query))
    loop.close()
    return result, tool

# UI Header
st.markdown("""
<div class="main-header">
    <h1>GreenMind</h1>
    <h3>Your Intelligent Environmental Sustainability Advisor</h3>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("About GreenMind")
    st.markdown("""
    **Required Tools:**
    • Environmental Policies RAG
    • Environmental Effects RAG
    • Web Search
    • Pollution Health Index
    • Carbon Footprint Calculator
    • Sustainability Tips
    • City Comparisons
    """)
    
    st.markdown("---")
    st.subheader("MCP Server Status")
    if st.session_state.mcp_connected:
        st.markdown('<div class="status-box connected">MCP Server Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box disconnected">MCP Server Disconnected</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("Clear Conversation"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# Display welcome message
if st.session_state.messages:
    with st.chat_message("assistant"):
        quote_html = f'''
        <div class="elegant-quote">
            <div class="quote-text">"{st.session_state.quote_data["text"]}"</div>
            <div class="quote-author">— {st.session_state.quote_data["author"]}</div>
        </div>
        '''
        st.markdown(quote_html, unsafe_allow_html=True)
        st.markdown(st.session_state.messages[0]["content"])

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
        with st.spinner("GreenMind is thinking..."):
            response, tool_used = process_with_mcp(prompt)
            st.markdown(response)
            if tool_used:
                st.caption(f"Tool used: {tool_used}")
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

st.markdown("""
<div class="footer">
    GreenMind - Working towards a sustainable future, one conversation at a time.
</div>
""", unsafe_allow_html=True)