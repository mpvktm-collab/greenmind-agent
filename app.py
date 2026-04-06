# app.py - Complete version with fixed header, transport tips, and concise layout
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

# Initialize MCP client in session state
if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = None
    st.session_state.mcp_connected = False
    st.session_state.connection_attempted = False

# Page configuration
st.set_page_config(
    page_title="GreenMind - Environmental Sustainability Advisor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Compact and sticky header
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
        padding: 0.8rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .main-header h1 { font-size: 1.6rem; margin-bottom: 0; }
    .main-header h3 { font-size: 0.9rem; font-weight: 300; font-style: italic; margin-bottom: 0; }
    .elegant-quote {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8f0e8 100%);
        padding: 0.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
        border-left: 4px solid #2E7D32;
    }
    .quote-text { font-size: 0.9rem; font-style: italic; color: #1e3a2e; }
    .quote-author { font-size: 0.7rem; color: #4a7850; text-align: right; margin-top: 0.2rem; }
    .status-box { padding: 0.5rem; border-radius: 8px; margin-bottom: 0.8rem; text-align: center; font-size: 0.8rem; }
    .connected { background-color: #d4edda; color: #155724; }
    .disconnected { background-color: #f8d7da; color: #721c24; }
    .footer { text-align: center; color: #666; padding: 0.5rem; margin-top: 1rem; border-top: 1px solid #e0e0e0; font-size: 0.7rem; }
    .stChatMessage { background-color: #ffffff; border-radius: 10px; padding: 8px; margin: 4px 0; border: 1px solid #e0e0e0; }
    .stChatMessage p { font-size: 0.9rem; margin-bottom: 0.3rem; }
    hr { margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

# Environmental keywords for domain detection (including common typos)
ENVIRONMENTAL_KEYWORDS = [
    'environment', 'climate', 'pollution', 'polluion', 'polution', 'air quality',
    'sustainable', 'carbon', 'footprint', 'co2', 'emission', 'aqi',
    'water quality', 'renewable', 'energy', 'recycle', 'waste', 'plastic',
    'forest', 'biodiversity', 'green', 'policy', 'regulation', 'act', 'law',
    'treaty', 'agreement', 'clean air', 'clean water', 'endangered',
    'conservation', 'eco-friendly', 'solar', 'wind', 'electric vehicle',
    'public transport', 'tree', 'plant', 'wildlife', 'ocean', 'river',
    'waste management', 'greenhouse', 'global warming', 'ozone', 'rainforest',
    'transportation', 'bike', 'walk', 'bus', 'train', 'car', 'vehicle'
]

def is_environmental_query(query):
    """Check if query is related to environmental sustainability with typo tolerance"""
    query_lower = query.lower()
    
    for keyword in ENVIRONMENTAL_KEYWORDS:
        if keyword in query_lower:
            return True
    
    pollution_variations = ['pollution', 'polluion', 'polution', 'polluton', 'pollutin']
    for var in pollution_variations:
        if var in query_lower:
            return True
    
    if 'index of' in query_lower:
        cities = ['delhi', 'mumbai', 'chennai', 'kolkata', 'bangalore', 'new york', 'london', 'tokyo', 'beijing']
        if any(city in query_lower for city in cities):
            return True
    
    if 'aqi' in query_lower or 'carbon' in query_lower or 'footprint' in query_lower:
        return True
    
    return False

def get_out_of_domain_response():
    return """I specialize in environmental topics only.

Ask me about:
• Policies & Regulations
• Pollution Index (AQI)
• Carbon Footprint
• Climate Effects
• Sustainability Tips"""

def get_no_data_response(tool_name):
    responses = {
        "Environmental_Policies_RAG": "No policy information found.",
        "Environmental_Effects_RAG": "No environmental effects found.",
        "Web_Search": "No relevant information found.",
        "default": "Information not found. Please rephrase."
    }
    return responses.get(tool_name, responses["default"])

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
        return None, "Connection error"
    
    timeout_value = 30.0
    
    try:
        result = await asyncio.wait_for(
            client.call_tool(tool_name, input=input_text),
            timeout=timeout_value
        )
        if result and isinstance(result, str):
            if "no results" in result.lower() or "not found" in result.lower() or "no web search" in result.lower():
                return None, "no_data"
        return result, "success"
    except asyncio.TimeoutError:
        return None, "timeout"
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, "error"

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
    return [city for city in cities if city in query_lower]

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
    
    for city in cities[:2]:
        if call_carbon:
            result, status = await call_mcp_tool("Carbon_Footprint_Calculator", city)
            if status == "success" and result:
                results[f"carbon_{city}"] = result
        if call_pollution:
            result, status = await call_mcp_tool("Pollution_Health_Index", city)
            if status == "success" and result:
                results[f"aqi_{city}"] = result
    
    return results, cities[:2], call_carbon, call_pollution

def format_comparison_results(results, cities, call_carbon, call_pollution):
    output = ["=" * 35, "COMPARISON", "=" * 35]
    
    for city in cities:
        output.append(f"\n{city.upper()}:")
        if call_pollution and f"aqi_{city}" in results:
            text = str(results[f"aqi_{city}"])
            aqi_match = re.search(r'AQI:\s*(\d+)', text)
            if aqi_match:
                output.append(f"  AQI: {aqi_match.group(1)}")
        if call_carbon and f"carbon_{city}" in results:
            text = str(results[f"carbon_{city}"])
            match = re.search(r'(\d+\.?\d*)\s*tons', text)
            if match:
                output.append(f"  Carbon: {match.group(1)} tons")
    
    return "\n".join(output)

# Initialize session state for messages
if 'messages' not in st.session_state:
    welcome_quotes = [
        {"text": "The earth is what we all have in common.", "author": "Wendell Berry"},
        {"text": "We borrow the earth from our children.", "author": "Native American Proverb"},
        {"text": "The greatest threat is believing someone else will save it.", "author": "Robert Swan"}
    ]
    today_quote = welcome_quotes[datetime.now().day % len(welcome_quotes)]
    
    st.session_state.quote_data = today_quote
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm GreenMind.\n\nAsk me about:\n• Policies • Pollution (AQI)\n• Carbon Footprint • Climate\n• Sustainability Tips\n\nHow can I help?"
    }]

async def process_with_mcp_async(user_query):
    query_lower = user_query.lower()
    
    if not is_environmental_query(user_query):
        return get_out_of_domain_response(), "OutOfDomain"
    
    # Comparison query
    if is_comparison_query(user_query) or len(extract_cities(user_query)) >= 2:
        results, cities, call_carbon, call_pollution = await handle_comparison(user_query)
        if results:
            return format_comparison_results(results, cities, call_carbon, call_pollution), "Comparison_Tool"
        return "Unable to compare. Try specific city names.", "Comparison_Tool"
    
    # Carbon footprint queries
    if any(word in query_lower for word in ['carbon', 'footprint', 'co2', 'emission']):
        result, status = await call_mcp_tool("Carbon_Footprint_Calculator", user_query)
        if status == "success" and result:
            return result, "Carbon_Footprint_Calculator"
        return "Unable to calculate carbon footprint.", "Carbon_Footprint_Calculator"
    
    # Pollution queries (including typos)
    pollution_indicators = ['air quality', 'aqi', 'pollution', 'polluion', 'polution', 'pollution index']
    if any(word in query_lower for word in pollution_indicators):
        result, status = await call_mcp_tool("Pollution_Health_Index", user_query)
        if status == "success" and result:
            return result, "Pollution_Health_Index"
        return "Unable to fetch pollution data.", "Pollution_Health_Index"
    
    # Policy queries (RAG)
    if any(word in query_lower for word in ['policy', 'act', 'regulation', 'law', 'agreement', 'treaty']):
        result, status = await call_mcp_tool("Environmental_Policies_RAG", user_query)
        if status == "success" and result and len(str(result)) > 50:
            return clean_response(result), "Environmental_Policies_RAG"
        return get_no_data_response("Environmental_Policies_RAG"), "Environmental_Policies_RAG"
    
    # Effects queries (RAG)
    if any(word in query_lower for word in ['effect', 'impact', 'health', 'disease', 'climate change']):
        result, status = await call_mcp_tool("Environmental_Effects_RAG", user_query)
        if status == "success" and result and len(str(result)) > 50:
            return clean_response(result), "Environmental_Effects_RAG"
        return get_no_data_response("Environmental_Effects_RAG"), "Environmental_Effects_RAG"
    
    # Tips queries - with transport routing
    if any(word in query_lower for word in ['tip', 'advice', 'sustainable', 'eco-friendly', 'reduce', 'recycle']):
        transport_keywords = ['transport', 'transportation', 'bike', 'walk', 'car', 'bus', 'train', 'metro', 'vehicle', 'drive', 'commute', 'eco-friendly transport']
        if any(word in query_lower for word in transport_keywords):
            result, status = await call_mcp_tool("Sustainability_Tips", "transport")
            if status == "success" and result:
                return result, "Sustainability_Tips"
        result, status = await call_mcp_tool("Sustainability_Tips", user_query)
        if status == "success" and result:
            return result, "Sustainability_Tips"
        return "Simple tip: Reduce, Reuse, Recycle!", "Sustainability_Tips"
    
    # Web search fallback
    result, status = await call_mcp_tool("Web_Search", user_query)
    if status == "success" and result and "no results" not in result.lower():
        return result, "Web_Search"
    
    return get_no_data_response("default"), "Default"

def process_with_mcp(user_query):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result, tool = loop.run_until_complete(process_with_mcp_async(user_query))
    loop.close()
    return result, tool

# Header
st.markdown("""
<div class="main-header">
    <h1>GreenMind</h1>
    <h3>Your Environmental Sustainability Advisor</h3>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("I answer ONLY environmental questions.")
    
    st.markdown("---")
    st.subheader("Status")
    if st.session_state.mcp_connected:
        st.markdown('<div class="status-box connected">Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box disconnected">Connecting...</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Tools")
    tools = ["Policies RAG", "Effects RAG", "Web Search", "Pollution Index", "Carbon Footprint", "Tips", "Comparisons"]
    for tool in tools:
        st.markdown(f"• {tool}")
    
    st.markdown("---")
    if st.button("Clear Chat"):
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
        with st.spinner("Thinking..."):
            response, tool_used = process_with_mcp(prompt)
            st.markdown(response)
            if tool_used and tool_used != "OutOfDomain":
                st.caption(f"Tool: {tool_used}")
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Footer
st.markdown("""
<div class="footer">
    GreenMind - Every small action counts.
</div>
""", unsafe_allow_html=True)