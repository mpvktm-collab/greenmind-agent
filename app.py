# app.py - Complete version with out-of-domain detection and concise responses
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

# Environmental keywords for domain detection
ENVIRONMENTAL_KEYWORDS = [
    'environment', 'climate', 'pollution', 'sustainable', 'carbon', 'footprint',
    'aqi', 'air quality', 'water quality', 'renewable', 'energy', 'recycle',
    'waste', 'plastic', 'forest', 'biodiversity', 'emission', 'green',
    'policy', 'regulation', 'act', 'law', 'treaty', 'agreement', 'clean air',
    'clean water', 'endangered', 'conservation', 'ecological', 'eco-friendly',
    'solar', 'wind', 'electric vehicle', 'public transport', 'tree', 'plant',
    'wildlife', 'ocean', 'river', 'waste management', 'carbon footprint',
    'greenhouse', 'global warming', 'ozone', 'rainforest', 'wildlife'
]

def is_environmental_query(query):
    """Check if query is related to environmental sustainability"""
    query_lower = query.lower()
    # Check for environmental keywords
    for keyword in ENVIRONMENTAL_KEYWORDS:
        if keyword in query_lower:
            return True
    # Check for city + pollution pattern
    if 'pollution index of' in query_lower or 'aqi of' in query_lower:
        return True
    # Check for city + carbon pattern
    if 'carbon footprint of' in query_lower:
        return True
    return False

def get_out_of_domain_response(query):
    """Return concise response for out-of-domain queries"""
    return """I specialize in environmental sustainability topics only.

Please ask me about:
• Environmental policies and regulations
• Pollution index and air quality (AQI)
• Carbon footprint calculations
• Climate change and environmental effects
• Sustainability tips and eco-friendly practices
• Environmental news and current affairs

How can I help you with environmental sustainability today?"""

def get_no_data_response(tool_name):
    """Return concise response when no data is available"""
    responses = {
        "Environmental_Policies_RAG": "I couldn't find specific policy information for your query. Please try rephrasing or ask about a different policy.",
        "Environmental_Effects_RAG": "I couldn't find specific environmental effect information. Please try a different question about environmental impacts.",
        "Web_Search": "No relevant environmental information found. Please try a different search term.",
        "default": "I couldn't find the information you're looking for. Please try rephrasing your question."
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

async def call_mcp_tool(tool_name: str, input_text: str, retry_count: int = 0):
    client = await get_mcp_client()
    
    if client is None or not st.session_state.mcp_connected:
        return None, "Connection error"
    
    # Short timeout for faster response
    timeout_value = 30.0
    
    try:
        result = await asyncio.wait_for(
            client.call_tool(tool_name, input=input_text),
            timeout=timeout_value
        )
        # Check if result is empty or indicates no results
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
    
    for city in cities[:2]:  # Limit to 2 cities for speed
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
    output = ["=" * 40, "COMPARISON RESULTS", "=" * 40]
    
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
                output.append(f"  Carbon: {match.group(1)} tons CO2/year")
    
    return "\n".join(output)

# Initialize session state for messages
if 'messages' not in st.session_state:
    welcome_quotes = [
        {"text": "The earth is what we all have in common.", "author": "Wendell Berry"},
        {"text": "We do not inherit the earth from our ancestors; we borrow it from our children.", "author": "Native American Proverb"},
        {"text": "The greatest threat to our planet is the belief that someone else will save it.", "author": "Robert Swan"}
    ]
    today_quote = welcome_quotes[datetime.now().day % len(welcome_quotes)]
    
    st.session_state.quote_data = today_quote
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm GreenMind, your environmental sustainability advisor.\n\nAsk me about:\n• Environmental policies\n• Pollution & air quality\n• Carbon footprint\n• Climate effects\n• Sustainability tips\n\nHow can I help you today?"
    }]

async def process_with_mcp_async(user_query):
    query_lower = user_query.lower()
    
    # Check if query is environmental
    if not is_environmental_query(user_query):
        return get_out_of_domain_response(user_query), "OutOfDomain"
    
    # Comparison query
    if is_comparison_query(user_query) or len(extract_cities(user_query)) >= 2:
        results, cities, call_carbon, call_pollution = await handle_comparison(user_query)
        if results:
            return format_comparison_results(results, cities, call_carbon, call_pollution), "Comparison_Tool"
        return "Unable to compare cities. Please try specific city names.", "Comparison_Tool"
    
    # Carbon footprint queries
    if any(word in query_lower for word in ['carbon', 'footprint', 'co2', 'emission']):
        result, status = await call_mcp_tool("Carbon_Footprint_Calculator", user_query)
        if status == "success" and result:
            return result, "Carbon_Footprint_Calculator"
        return "Unable to calculate carbon footprint. Please try a specific city or activity.", "Carbon_Footprint_Calculator"
    
    # Pollution queries
    if any(word in query_lower for word in ['air quality', 'aqi', 'pollution', 'pollution index']):
        result, status = await call_mcp_tool("Pollution_Health_Index", user_query)
        if status == "success" and result:
            return result, "Pollution_Health_Index"
        return "Unable to fetch pollution data. Please try a different location.", "Pollution_Health_Index"
    
    # Policy queries (RAG)
    if any(word in query_lower for word in ['policy', 'act', 'regulation', 'law', 'agreement', 'treaty']):
        result, status = await call_mcp_tool("Environmental_Policies_RAG", user_query)
        if status == "success" and result:
            cleaned = clean_response(result)
            if len(cleaned) > 50:  # Has meaningful content
                return cleaned, "Environmental_Policies_RAG"
        return get_no_data_response("Environmental_Policies_RAG"), "Environmental_Policies_RAG"
    
    # Effects queries (RAG)
    if any(word in query_lower for word in ['effect', 'impact', 'health', 'disease', 'climate change']):
        result, status = await call_mcp_tool("Environmental_Effects_RAG", user_query)
        if status == "success" and result:
            cleaned = clean_response(result)
            if len(cleaned) > 50:
                return cleaned, "Environmental_Effects_RAG"
        return get_no_data_response("Environmental_Effects_RAG"), "Environmental_Effects_RAG"
    
    # Tips queries
    if any(word in query_lower for word in ['tip', 'advice', 'sustainable', 'eco-friendly', 'reduce', 'recycle']):
        result, status = await call_mcp_tool("Sustainability_Tips", user_query)
        if status == "success" and result:
            return result, "Sustainability_Tips"
        return "Here's a simple tip: Reduce, Reuse, Recycle! Every small action helps our planet.", "Sustainability_Tips"
    
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
    st.header("About GreenMind")
    st.markdown("I answer ONLY environmental sustainability questions.")
    
    st.markdown("---")
    st.subheader("Status")
    if st.session_state.mcp_connected:
        st.markdown('<div class="status-box connected">Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box disconnected">Connecting...</div>', unsafe_allow_html=True)
    
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
    GreenMind - Every small action counts towards a greener planet.
</div>
""", unsafe_allow_html=True)