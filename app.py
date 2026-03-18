# app.py - Complete version with improved routing

# app.py - Complete version with improved routing for city carbon footprint
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

# Initialize MCP client in session state (only once)
if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = None
    st.session_state.mcp_connected = False
    st.session_state.connection_attempted = False

# Page configuration with sidebar expanded by default
st.set_page_config(
    page_title="GreenMind - Environmental Sustainability Advisor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"  # This keeps sidebar open by default
)

# Force sidebar to stay expanded with CSS
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"] {
            display: block;
        }
        section[data-testid="stSidebar"][aria-expanded="false"] {
            display: block;
            margin-left: 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Custom CSS with stylish quote formatting
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        font-size: 2.2rem;
        margin-bottom: 0.3rem;
        font-weight: 600;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .main-header h3 {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.95;
        font-style: italic;
    }
    
    /* Stylish quote box */
    .elegant-quote {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8f0e8 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.15);
        border-left: 6px solid #2E7D32;
        position: relative;
    }
    .elegant-quote::before {
        content: '"';
        font-size: 4rem;
        color: #2E7D32;
        opacity: 0.3;
        position: absolute;
        top: -10px;
        left: 10px;
        font-family: Georgia, serif;
    }
    .elegant-quote::after {
        content: '"';
        font-size: 4rem;
        color: #2E7D32;
        opacity: 0.3;
        position: absolute;
        bottom: -30px;
        right: 10px;
        font-family: Georgia, serif;
    }
    .quote-text {
        font-size: 1.3rem;
        font-style: italic;
        color: #1e3a2e;
        font-weight: 500;
        line-height: 1.6;
        margin-bottom: 0.5rem;
        font-family: 'Georgia', serif;
    }
    .quote-author {
        font-size: 1rem;
        color: #4a7850;
        font-weight: 400;
        text-align: right;
        margin-top: 0.5rem;
        font-family: 'Arial', sans-serif;
        letter-spacing: 1px;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    .stChatMessage p {
        font-weight: normal;
        margin-bottom: 0.5rem;
        font-size: 1rem;
        line-height: 1.5;
    }
    .stChatMessage h1, .stChatMessage h2, .stChatMessage h3 {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
        color: #2E7D32;
    }
    .stChatMessage strong {
        font-weight: 600;
        color: #1e3a2e;
    }
    
    /* Sidebar styling */
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
    }
    .status-box {
        padding: 0.8rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 0.95rem;
        font-weight: 500;
        text-align: center;
    }
    .connected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .disconnected {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Tool list styling */
    .tool-item {
        padding: 0.3rem 0;
        color: #2E7D32;
        font-weight: 500;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: #666;
        padding: 1rem;
        font-size: 0.85rem;
        border-top: 1px solid #e0e0e0;
        margin-top: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
    }
    .footer small {
        color: #4a7850;
        font-style: italic;
    }
    
    hr {
        margin: 1rem 0;
        border: 0;
        height: 1px;
        background: linear-gradient(to right, transparent, #2E7D32, transparent);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for messages
if 'messages' not in st.session_state:
    # Welcome message with stylish environmental quote
    welcome_quotes = [
        {"text": "The earth is what we all have in common.", "author": "Wendell Berry"},
        {"text": "The environment is where we all meet; where we all have a mutual interest.", "author": "Lady Bird Johnson"},
        {"text": "We do not inherit the earth from our ancestors; we borrow it from our children.", "author": "Native American Proverb"},
        {"text": "The greatest threat to our planet is the belief that someone else will save it.", "author": "Robert Swan"},
        {"text": "Look deep into nature, and then you will understand everything better.", "author": "Albert Einstein"},
        {"text": "The Earth does not belong to us: we belong to the Earth.", "author": "Marlee Matlin"},
        {"text": "Nature is painting for us, day after day, pictures of infinite beauty.", "author": "John Ruskin"},
        {"text": "The poetry of the earth is never dead.", "author": "John Keats"},
        {"text": "In every walk with nature, one receives far more than he seeks.", "author": "John Muir"},
        {"text": "The environment and the economy are really both two sides of the same coin.", "author": "Christine Lagarde"}
    ]
    today_quote = welcome_quotes[datetime.now().day % len(welcome_quotes)]
    
    # Store quote data separately
    st.session_state.quote_data = today_quote
    
    # Store plain text message
    st.session_state.messages = [{
        "role": "assistant",
        "content": f"Hello! I'm GreenMind, your environmental sustainability advisor.\n\n"
                  f"I can help you with:\n"
                  f"• Environmental policies and regulations\n"
                  f"• Environmental effects and impacts (including health effects)\n"
                  f"• Current environmental news\n"
                  f"• Pollution and health indices\n"
                  f"• Carbon footprint calculations\n"
                  f"• Sustainability tips\n"
                  f"• Comparisons between cities or environmental factors\n\n"
                  f"How can I help you protect our planet today?"
    }]

# List of major cities
MAJOR_CITIES = [
    'delhi', 'mumbai', 'bombay', 'chennai', 'hyderabad', 'kolkata', 'calcutta', 'bangalore', 
    'cochin', 'kochi', 'ernakulam', 'trivandrum', 'thiruvananthapuram',
    'ahmedabad', 'pune', 'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore', 'bhopal',
    'new york', 'los angeles', 'chicago', 'london', 'paris', 'tokyo', 'beijing', 'shanghai',
    'sydney', 'melbourne', 'toronto', 'vancouver', 'mexico city', 'sao paulo', 'dubai',
    'singapore', 'hong kong', 'seoul', 'bangkok', 'jakarta', 'moscow', 'berlin', 'rome',
    'madrid', 'barcelona', 'amsterdam', 'brussels', 'vienna', 'zurich', 'stockholm',
    'oslo', 'helsinki', 'dublin', 'edinburgh', 'glasgow', 'manchester', 'birmingham'
]

# Function to get or create MCP client
async def get_mcp_client():
    """Get the cached MCP client from session state or create a new one"""
    if st.session_state.mcp_client is None and not st.session_state.connection_attempted:
        st.session_state.connection_attempted = True
        mcp_host = os.getenv('MCP_HOST', 'greenmind-agent.onrender.com')
        
        print(f"Creating new MCP client for host: {mcp_host}")
        try:
            client = MCPClient(host=mcp_host)
            connected = await client.connect()
            
            if connected:
                print("MCP client connected successfully")
                st.session_state.mcp_client = client
                st.session_state.mcp_connected = True
            else:
                print("Failed to connect MCP client")
                st.session_state.mcp_connected = False
        except Exception as e:
            print(f"Error creating MCP client: {str(e)}")
            st.session_state.mcp_connected = False
    
    return st.session_state.mcp_client

# Function to call MCP tool with timeout
async def call_mcp_tool(tool_name: str, input_text: str):
    """Call a tool via MCP client using cached connection"""
    client = await get_mcp_client()
    
    if client is None or not st.session_state.mcp_connected:
        return "Error: Could not connect to MCP Server. Make sure it's running."
    
    try:
        result = await client.call_tool(tool_name, input=input_text)
        return result
    except Exception as e:
        print(f"Error calling tool: {str(e)}")
        # Reset client on error
        st.session_state.mcp_client = None
        st.session_state.mcp_connected = False
        return f"Error calling tool: {str(e)}"

# Clean response function
def clean_response(text):
    """Transform raw document text into clean, elegant responses"""
    if not isinstance(text, str):
        return text
    
    text = re.sub(r'\[\s*Paragraph\s+\d+\s*\]', '', text)
    text = re.sub(r'H\d+:\s*', '', text)
    text = re.sub(r'TITLE:.*?\n', '', text)
    text = re.sub(r'SOURCE:.*?\n', '', text)
    text = re.sub(r'SCRAPED:.*?\n', '', text)
    text = re.sub(r'HEADINGS:.*?(?=CONTENT:|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'CONTENT:', '', text)
    text = re.sub(r'\[\s*Source:.*?\].*?\n', '', text)
    text = re.sub(r'https?://\S+', '', text)
    
    lines = text.split('\n')
    relevant_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if any(skip in line.lower() for skip in ['language selection', 'search', 'menu', 'you are here']):
            continue
        line = re.sub(r'^\d+\.\s*', '', line)
        line = re.sub(r'^\*\s*', '', line)
        line = re.sub(r'\s+', ' ', line)
        relevant_lines.append(line)
    
    text = '\n'.join(relevant_lines)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    return text.strip()

# Function to detect if query is asking for comparison
def is_comparison_query(query):
    query_lower = query.lower()
    indicators = ['compare', 'comparison', 'versus', 'vs', 'difference between', 'rank', 'ranking']
    return any(indicator in query_lower for indicator in indicators)

# Function to extract cities from query
def extract_cities(query):
    query_lower = query.lower()
    found_cities = []
    for city in MAJOR_CITIES:
        if city in query_lower:
            if city == 'bombay' and 'mumbai' not in found_cities:
                found_cities.append('mumbai')
            elif city == 'calcutta' and 'kolkata' not in found_cities:
                found_cities.append('kolkata')
            elif city == 'cochin' and 'kochi' not in found_cities:
                found_cities.append('kochi')
            elif city == 'trivandrum' and 'thiruvananthapuram' not in found_cities:
                found_cities.append('thiruvananthapuram')
            elif city not in found_cities:
                found_cities.append(city)
    return found_cities

# Function to handle comparison queries
async def handle_comparison(query):
    query_lower = query.lower()
    cities = extract_cities(query)
    
    if not cities:
        if 'carbon' in query_lower and 'air quality' in query_lower:
            cities = ['delhi', 'mumbai', 'london', 'new york']
        elif 'carbon' in query_lower:
            cities = ['delhi', 'london', 'new york', 'tokyo']
        elif 'air quality' in query_lower or 'pollution' in query_lower:
            cities = ['delhi', 'beijing', 'mumbai', 'los angeles']
        else:
            cities = ['delhi', 'mumbai', 'london', 'new york']
    
    results = {}
    
    # Determine which tools to call based on query
    call_carbon = 'carbon' in query_lower or 'footprint' in query_lower
    call_pollution = 'pollution' in query_lower or 'air quality' in query_lower or 'aqi' in query_lower
    
    # For city comparisons with "and", call both if relevant
    if 'and' in query_lower or ',' in query_lower:
        if 'carbon' in query_lower:
            call_carbon = True
        if 'pollution' in query_lower or 'air quality' in query_lower:
            call_pollution = True
    
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

# Function to format comparison results
def format_comparison_results(results, cities, query, call_carbon, call_pollution):
    output = []
    output.append("=" * 70)
    output.append("COMPARISON RESULTS")
    output.append("=" * 70)
    output.append("")
    
    for i, city in enumerate(cities[:3]):
        if i > 0:
            output.append("")
            output.append("-" * 40)
            output.append("")
        
        output.append(f"CITY: {city.upper()}")
        output.append("")
        
        if call_carbon and f"carbon_{city}" in results:
            carbon_text = results[f"carbon_{city}"]
            carbon_match = re.search(r'(\d+\.?\d*)\s*tons', carbon_text)
            if carbon_match:
                carbon_value = carbon_match.group(1)
                output.append(f"  CARBON FOOTPRINT: {carbon_value} tons CO2 per year")
        
        if call_pollution and f"aqi_{city}" in results:
            aqi_text = results[f"aqi_{city}"]
            aqi_match = re.search(r'AQI\):\s*(\d+)', aqi_text)
            if aqi_match:
                aqi_value = aqi_match.group(1)
                output.append(f"  AIR QUALITY INDEX: {aqi_value}")
                
                pm25_match = re.search(r'PM2\.5:\s*(\d+)', aqi_text)
                pm10_match = re.search(r'PM10:\s*(\d+)', aqi_text)
                
                if pm25_match:
                    output.append(f"  PM2.5: {pm25_match.group(1)} μg/m³")
                if pm10_match:
                    output.append(f"  PM10: {pm10_match.group(1)} μg/m³")
    
    output.append("")
    output.append("=" * 70)
    output.append("Note: These are simulated values for demonstration.")
    return "\n".join(output)

# Function to process query with MCP
async def process_with_mcp_async(user_query):
    query_lower = user_query.lower()
    
    # Check for comparison query first
    if is_comparison_query(user_query) or len(extract_cities(user_query)) >= 2:
        print("Detected comparison query")
        results, cities, call_carbon, call_pollution = await handle_comparison(user_query)
        if results:
            formatted = format_comparison_results(results, cities, user_query, call_carbon, call_pollution)
            return formatted, "Comparison_Tool"
    
    # Improved carbon footprint detection - check for city names
    carbon_keywords = ['carbon', 'footprint', 'co2', 'emission']
    city_names = ['delhi', 'mumbai', 'new york', 'london', 'paris', 'tokyo', 'beijing', 
                  'chicago', 'los angeles', 'san francisco', 'berlin', 'sydney']
    
    # Check if query has carbon keywords AND city names
    has_carbon = any(word in query_lower for word in carbon_keywords)
    has_city = any(city in query_lower for city in city_names)
    
    if has_carbon and has_city:
        tool = "Carbon_Footprint_Calculator"
        print(f"Routing to {tool} for city carbon footprint")
        result = await call_mcp_tool(tool, user_query)
        cleaned_result = clean_response(result)
        return cleaned_result, tool
    
    # Health-related keywords
    if any(word in query_lower for word in ['cancer', 'health', 'disease', 'respiratory']):
        tool = "Environmental_Effects_RAG"
    elif any(word in query_lower for word in ['air quality', 'aqi', 'pollution']):
        tool = "Pollution_Health_Index"
    elif any(word in query_lower for word in ['carbon', 'footprint', 'co2']):
        # Only reach here if no city was detected
        tool = "Carbon_Footprint_Calculator"
    elif any(word in query_lower for word in ['policy', 'act', 'regulation', 'law']):
        tool = "Environmental_Policies_RAG"
    elif any(word in query_lower for word in ['effect', 'impact', 'climate change']):
        tool = "Environmental_Effects_RAG"
    elif any(word in query_lower for word in ['tip', 'advice', 'sustainable']):
        tool = "Sustainability_Tips"
    elif any(word in query_lower for word in ['search', 'news', 'current']):
        tool = "Web_Search"
    elif any(word in query_lower for word in ['wikipedia']):
        tool = "Wikipedia_Knowledge"
    else:
        tool = "Environmental_Policies_RAG"
    
    print(f"Routing to {tool}")
    result = await call_mcp_tool(tool, user_query)
    cleaned_result = clean_response(result)
    return cleaned_result, tool

# Wrapper function
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
    <h3>Your Intelligent Environmental Sustainability Advisor</h3>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.header("About GreenMind")
    st.markdown("""
    GreenMind is an AI-powered environmental advisor that helps you understand and protect our planet.
    
    **Capabilities:**
    • Environmental policies and regulations
    • Environmental effects and health impacts
    • Current environmental news
    • Pollution and health indices
    • Carbon footprint calculations
    • Sustainability tips
    • City comparisons
    """)
    
    st.markdown("---")
    st.subheader("MCP Server Status")
    
    # Display MCP_HOST from environment
    mcp_host = os.getenv('MCP_HOST', 'Not set')
    st.info(f"MCP Server: {mcp_host}")
    
    # Test connection button
    if st.button("Test MCP Connection"):
        async def test_connection():
            host = os.getenv('MCP_HOST', 'greenmind-agent.onrender.com')
            client = MCPClient(host=host)
            return await client.connect()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        status = loop.run_until_complete(test_connection())
        loop.close()
        
        if status:
            st.success("Connected")
        else:
            st.error("Connection failed")
    
    if st.session_state.mcp_connected:
        st.markdown('<div class="status-box connected">MCP Server Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box disconnected">MCP Server Disconnected</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Available Tools")
    tools_list = [
        "Environmental_Policies_RAG",
        "Environmental_Effects_RAG",
        "Web_Search",
        "Wikipedia_Knowledge",
        "Pollution_Health_Index",
        "Carbon_Footprint_Calculator",
        "Sustainability_Tips",
        "Comparison_Tool"
    ]
    for tool in tools_list:
        st.markdown(f'<div class="tool-item">• {tool}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("Clear Conversation"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Display welcome message with quote
if st.session_state.messages and len(st.session_state.messages) > 0:
    with st.chat_message("assistant"):
        if 'quote_data' in st.session_state:
            quote_html = f'''
            <div class="elegant-quote">
                <div class="quote-text">{st.session_state.quote_data["text"]}</div>
                <div class="quote-author">— {st.session_state.quote_data["author"]}</div>
            </div>
            '''
            # Critical: This parameter makes the HTML render properly
            st.markdown(quote_html, unsafe_allow_html=True)
        
        st.markdown(st.session_state.messages[0]["content"])

# Display remaining messages
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
                st.caption(f"Used tool: {tool_used}")
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    GreenMind - Working towards a sustainable future, one conversation at a time.<br>
    <small>Remember: Every small action counts towards a greener planet.</small>
</div>
""", unsafe_allow_html=True)