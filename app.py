# app.py - Enhanced with better query understanding for comparisons
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

# Page configuration
st.set_page_config(
    page_title="GreenMind - Environmental Sustainability Advisor",
    page_icon="🌍",
    layout="wide"
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
        font-family: monospace;
    }
    .stChatMessage p {
        font-weight: normal;
        margin-bottom: 0.5rem;
        font-size: 1rem;
        line-height: 1.5;
        font-family: monospace;
    }
    .stChatMessage h1, .stChatMessage h2, .stChatMessage h3 {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
        color: #2E7D32;
        font-family: Arial, sans-serif;
    }
    .stChatMessage strong {
        font-weight: 600;
        color: #1e3a2e;
    }
    
    /* Comparison table styling */
    .comparison-city {
        font-weight: bold;
        color: #2E7D32;
        margin-top: 0.5rem;
        margin-bottom: 0.2rem;
    }
    .comparison-row {
        margin-left: 1rem;
        margin-bottom: 0.2rem;
    }
    .green-text {
        color: #00AA00;
        font-weight: bold;
    }
    .yellow-text {
        color: #CCCC00;
        font-weight: bold;
    }
    .orange-text {
        color: #FF8800;
        font-weight: bold;
    }
    .red-text {
        color: #FF0000;
        font-weight: bold;
    }
    .purple-text {
        color: #AA00AA;
        font-weight: bold;
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

# Initialize session state
if 'mcp_connected' not in st.session_state:
    st.session_state.mcp_connected = False

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
    
    # Store quote data separately, not as HTML in message
    st.session_state.quote_data = today_quote
    
    # Store plain text message without HTML
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

# List of major cities for reference - Updated with requested cities
MAJOR_CITIES = [
    # Indian cities - updated with Bombay, Cochin, Kochi, Ernakulam, Trivandrum
    'delhi', 'mumbai', 'bombay', 'chennai', 'hyderabad', 'kolkata', 'calcutta', 'bangalore', 
    'cochin', 'kochi', 'ernakulam', 'trivandrum', 'thiruvananthapuram',
    'ahmedabad', 'pune', 'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore', 'bhopal',
    'visakhapatnam', 'patna', 'vadodara', 'surat', 'coimbatore', 'mysore',
    
    # US cities
    'new york', 'los angeles', 'chicago', 'california', 'san francisco', 'seattle', 
    'boston', 'washington', 'miami', 'dallas', 'houston', 'philadelphia', 'atlanta',
    'detroit', 'denver', 'phoenix', 'portland', 'san diego', 'las vegas',
    
    # UK/Europe
    'london', 'manchester', 'birmingham', 'liverpool', 'paris', 'berlin', 'munich',
    'hamburg', 'frankfurt', 'rome', 'milan', 'barcelona', 'madrid', 'amsterdam',
    'brussels', 'vienna', 'zurich', 'stockholm', 'copenhagen', 'oslo', 'helsinki',
    'warsaw', 'prague', 'budapest', 'dublin', 'edinburgh', 'glasgow',
    
    # Asia
    'tokyo', 'osaka', 'kyoto', 'yokohama', 'nagoya', 'sapporo', 'beijing', 'shanghai',
    'guangzhou', 'shenzhen', 'chengdu', 'hong kong', 'seoul', 'busan', 'incheon',
    'singapore', 'bangkok', 'phuket', 'chiang mai', 'kuala lumpur', 'jakarta', 'bali',
    'manila', 'ho chi minh', 'hanoi', 'taipei', 'colombo',
    
    # Australia/NZ
    'sydney', 'melbourne', 'brisbane', 'perth', 'adelaide', 'canberra', 'auckland',
    'wellington', 'christchurch',
    
    # Middle East/Africa
    'dubai', 'abu dhabi', 'doha', 'riyadh', 'jeddah', 'dammam', 'kuwait', 'muscat',
    'tel aviv', 'jerusalem', 'istanbul', 'cairo', 'alexandria', 'casablanca', 'tunis',
    'algiers', 'lagos', 'nairobi', 'cape town', 'johannesburg', 'durban',
    
    # South America
    'sao paulo', 'rio de janeiro', 'brasilia', 'salvador', 'fortaleza', 'buenos aires',
    'cordoba', 'rosario', 'santiago', 'valparaiso', 'lima', 'bogota', 'medellin',
    'caracas', 'quito', 'guayaquil', 'la paz', 'montevideo', 'asuncion',
    
    # Canada
    'toronto', 'vancouver', 'montreal', 'calgary', 'ottawa', 'edmonton', 'quebec',
    'winnipeg', 'hamilton', 'halifax',
    
    # Mexico/Central America
    'mexico city', 'guadalajara', 'monterrey', 'puebla', 'tijuana', 'cancun',
    'havana', 'san jose', 'panama city'
]

# Function to call MCP tool
async def call_mcp_tool(tool_name: str, input_text: str):
    """Call a tool via MCP client"""
    try:
        async with MCPClient() as client:
            # Check connection
            if not await client.ping():
                return "Error: Could not connect to MCP Server. Make sure it's running."
            
            # Call the tool
            result = await client.call_tool(tool_name, input=input_text)
            return result
    except Exception as e:
        return f"Error calling tool: {str(e)}"

# Enhanced function to clean and structure responses elegantly
def clean_response(text):
    """Transform raw document text into clean, elegant responses"""
    if not isinstance(text, str):
        return text
    
    # Remove all technical markers
    text = re.sub(r'\[\s*Paragraph\s+\d+\s*\]', '', text)
    text = re.sub(r'H\d+:\s*', '', text)
    text = re.sub(r'TITLE:.*?\n', '', text)
    text = re.sub(r'SOURCE:.*?\n', '', text)
    text = re.sub(r'SCRAPED:.*?\n', '', text)
    text = re.sub(r'HEADINGS:.*?(?=CONTENT:|$)', '', text, flags=re.DOTALL)
    text = re.sub(r'CONTENT:', '', text)
    text = re.sub(r'\[\s*Source:.*?\].*?\n', '', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    
    # Remove navigation and metadata lines
    lines = text.split('\n')
    relevant_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines at start
        if not line and not relevant_lines:
            continue
            
        # Skip navigation/metadata
        if any(skip in line.lower() for skip in [
            'language selection', 'search', 'menu', 'you are here', 
            'page details', 'about this site', 'give feedback', 
            'follow us', 'contact us', 'terms and conditions',
            'privacy', 'accessibility', 'symbols', 'footer',
            'share this page', 'date modified', 'was this page helpful',
            'table of contents', 'on this page', 'related links',
            'government of canada', 'government of canada corporate'
        ]):
            continue
            
        # Skip lines that are just URLs or technical notes
        if line.startswith('http') or 'www.' in line:
            continue
            
        # Skip lines about website restructuring
        if any(phrase in line.lower() for phrase in [
            'this content was part of our previous website',
            'no longer available',
            'we\'ve recently upgraded',
            'restructured our content',
            'sent straight to your inbox',
            'the best of the iea',
            'top energy experts'
        ]):
            continue
            
        # Skip lines with just numbers or special characters
        if re.match(r'^[\d\s\-_=*]+$', line):
            continue
            
        # Clean up the line
        line = re.sub(r'^\d+\.\s*', '', line)  # Remove numbered lists
        line = re.sub(r'^\*\s*', '', line)     # Remove bullet points
        line = re.sub(r'\s+', ' ', line)       # Normalize spaces
        
        if line:
            relevant_lines.append(line)
    
    # Join and clean up
    text = '\n'.join(relevant_lines)
    
    # Remove multiple blank lines
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Add section breaks for better readability
    text = re.sub(r'(United States|Canada|US|USA|Canadian)', r'\n\n\1', text)
    
    return text.strip()

# Function to detect if query is asking for comparison
def is_comparison_query(query):
    """Detect if the query is asking for a comparison"""
    query_lower = query.lower()
    
    comparison_indicators = [
        'compare', 'comparison', 'versus', 'vs', 'difference between',
        'which is better', 'which has better', 'rank', 'ranking',
        'verses', 'v/s', 'top cities', 'best cities', 'worst cities'
    ]
    
    return any(indicator in query_lower for indicator in comparison_indicators)

# Function to extract cities from query
def extract_cities(query):
    """Extract city names from query"""
    query_lower = query.lower()
    found_cities = []
    
    for city in MAJOR_CITIES:
        if city in query_lower:
            # Handle special cases
            if city == 'calcutta' and 'kolkata' not in found_cities:
                found_cities.append('kolkata')
            elif city == 'bombay' and 'mumbai' not in found_cities:
                found_cities.append('mumbai')
            elif city == 'cochin' and 'kochi' not in found_cities:
                found_cities.append('kochi')
            elif city == 'ernakulam' and 'kochi' not in found_cities:
                found_cities.append('kochi')
            elif city == 'trivandrum' and 'thiruvananthapuram' not in found_cities:
                found_cities.append('thiruvananthapuram')
            elif city not in found_cities:
                found_cities.append(city)
    
    return found_cities

# Function to handle comparison queries
async def handle_comparison(query):
    """Handle comparison queries by calling multiple tools"""
    query_lower = query.lower()
    cities = extract_cities(query)
    
    # If we have cities from extract_cities, use them
    if cities:
        print(f"Extracted cities: {cities}")
    else:
        # Try to parse cities from "and" or commas
        import re
        # Look for patterns like "delhi and mumbai" or "delhi, mumbai"
        and_pattern = r'(\w+)\s+and\s+(\w+)'
        comma_pattern = r'(\w+)\s*,\s*(\w+)'
        
        and_match = re.search(and_pattern, query_lower)
        if and_match:
            city1 = and_match.group(1)
            city2 = and_match.group(2)
            # Validate that these are actual cities
            if city1 in MAJOR_CITIES or any(city1 in city for city in MAJOR_CITIES):
                cities.append(city1)
            if city2 in MAJOR_CITIES or any(city2 in city for city in MAJOR_CITIES):
                cities.append(city2)
            print(f"Parsed cities from 'and': {cities}")
        
        if not cities:
            comma_match = re.search(comma_pattern, query_lower)
            if comma_match:
                city1 = comma_match.group(1)
                city2 = comma_match.group(2)
                if city1 in MAJOR_CITIES or any(city1 in city for city in MAJOR_CITIES):
                    cities.append(city1)
                if city2 in MAJOR_CITIES or any(city2 in city for city in MAJOR_CITIES):
                    cities.append(city2)
                print(f"Parsed cities from comma: {cities}")
    
    # If still no cities, use defaults based on query content
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
    call_pollution = 'pollution' in query_lower or 'air quality' in query_lower or 'aqi' in query_lower or 'index' in query_lower
    
    # If neither is specified, call both by default for comparison
    if not call_carbon and not call_pollution:
        call_carbon = True
        call_pollution = True
    
    # Call appropriate tools for each city
    for city in cities[:3]:  # Limit to 3 cities for readability
        if call_carbon:
            result = await call_mcp_tool("Carbon_Footprint_Calculator", city)
            results[f"carbon_{city}"] = result
        
        if call_pollution:
            result = await call_mcp_tool("Pollution_Health_Index", city)
            results[f"aqi_{city}"] = result
    
    return results, cities, call_carbon, call_pollution

# Function to get color class for a value
def get_color_class(value, type='aqi'):
    """Get CSS color class based on value"""
    if type == 'aqi':
        if value <= 50:
            return 'green-text'
        elif value <= 100:
            return 'yellow-text'
        elif value <= 150:
            return 'orange-text'
        elif value <= 200:
            return 'red-text'
        else:
            return 'purple-text'
    elif type == 'carbon':
        if value <= 2.0:
            return 'green-text'
        elif value <= 5.0:
            return 'yellow-text'
        else:
            return 'red-text'
    return ''

# Function to format comparison results with proper multi-line formatting
def format_comparison_results(results, cities, query, call_carbon, call_pollution):
    """Format comparison results in a readable way with multi-line format"""
    
    output = []
    output.append("=" * 70)
    output.append("COMPARISON RESULTS")
    output.append("=" * 70)
    output.append("")
    
    # Process each city individually for multi-line display
    for i, city in enumerate(cities[:3]):
        if i > 0:
            output.append("")  # Add line break between cities
            output.append("-" * 40)
            output.append("")
        
        output.append(f"CITY: {city.upper()}")
        output.append("")
        
        if call_carbon and f"carbon_{city}" in results:
            carbon_text = results[f"carbon_{city}"]
            # Extract carbon value
            carbon_match = re.search(r'(\d+\.?\d*)\s*tons', carbon_text)
            if carbon_match:
                carbon_value = float(carbon_match.group(1))
                color_class = get_color_class(carbon_value, 'carbon')
                
                # Create visual bar for carbon
                bar_length = min(20, int((carbon_value / 10) * 20))
                bar = "█" * bar_length + "░" * (20 - bar_length)
                
                # Determine rating text
                if carbon_value <= 2.0:
                    rating = "Good"
                elif carbon_value <= 5.0:
                    rating = "Moderate"
                else:
                    rating = "High"
                
                output.append(f"  CARBON FOOTPRINT:")
                output.append(f"    Value: {carbon_value} tons CO2 per year")
                output.append(f"    Rating: {rating}")
                output.append(f"    Visual: [{bar}]")
                output.append("")
        
        if call_pollution and f"aqi_{city}" in results:
            aqi_text = results[f"aqi_{city}"]
            
            # Extract AQI value
            aqi_match = re.search(r'AQI\):\s*(\d+)', aqi_text)
            if aqi_match:
                aqi_value = int(aqi_match.group(1))
                color_class = get_color_class(aqi_value, 'aqi')
                
                # Create visual bar for AQI
                bar_length = min(20, int((aqi_value / 300) * 20))
                bar = "█" * bar_length + "░" * (20 - bar_length)
                
                # Determine rating text
                if aqi_value <= 50:
                    rating = "Good"
                elif aqi_value <= 100:
                    rating = "Moderate"
                elif aqi_value <= 150:
                    rating = "Unhealthy for Sensitive Groups"
                elif aqi_value <= 200:
                    rating = "Unhealthy"
                elif aqi_value <= 300:
                    rating = "Very Unhealthy"
                else:
                    rating = "Hazardous"
                
                output.append(f"  POLLUTION INDEX / AIR QUALITY:")
                output.append(f"    AQI: {aqi_value}")
                output.append(f"    Rating: {rating}")
                output.append(f"    Visual: [{bar}]")
                output.append("")
                
                # Extract PM2.5 and PM10 values
                pm25_match = re.search(r'PM2\.5:\s*(\d+)', aqi_text)
                pm10_match = re.search(r'PM10:\s*(\d+)', aqi_text)
                
                if pm25_match:
                    pm25 = pm25_match.group(1)
                    pm25_color = 'green-text' if int(pm25) < 25 else 'yellow-text' if int(pm25) < 50 else 'red-text'
                    output.append(f"    PM2.5: {pm25} μg/m³ [Safe: <25]")
                
                if pm10_match:
                    pm10 = pm10_match.group(1)
                    pm10_color = 'green-text' if int(pm10) < 50 else 'yellow-text' if int(pm10) < 100 else 'red-text'
                    output.append(f"    PM10: {pm10} μg/m³ [Safe: <50]")
                
                # Extract health recommendations
                health_lines = [line for line in aqi_text.split('\n') if 'HEALTH' in line or 'RECOMMENDATIONS' in line]
                if health_lines:
                    output.append(f"    Health: {health_lines[0].strip()}")
    
    output.append("")
    output.append("=" * 70)
    output.append("Note: These are simulated values for demonstration.")
    output.append("For production, connect to real APIs like OpenAQ or WAQI.")
    
    return "\n".join(output)

# Function to process query with MCP
async def process_with_mcp_async(user_query):
    """Async version of query processing"""
    query_lower = user_query.lower()
    
    # Check if this is a multi-city query (contains "and" or commas between cities)
    city_indicators = [' and ', ',', '&']
    has_multiple_cities = any(indicator in user_query for indicator in city_indicators)
    
    # Extract cities from query
    extracted_cities = extract_cities(user_query)
    
    # Check if this is a multi-metric query (asks for both carbon and pollution)
    has_carbon = any(word in query_lower for word in ['carbon', 'footprint', 'co2'])
    has_pollution = any(word in query_lower for word in ['pollution', 'air quality', 'aqi', 'index'])
    
    # If multiple cities AND (carbon or pollution) are mentioned, treat as comparison
    if (len(extracted_cities) >= 2 or has_multiple_cities) and (has_carbon or has_pollution):
        print(f"Detected multi-city comparison query with {len(extracted_cities)} cities")
        results, cities, call_carbon, call_pollution = await handle_comparison(user_query)
        if results:
            formatted = format_comparison_results(results, cities, user_query, call_carbon, call_pollution)
            return formatted, "Comparison_Tool"
    
    # Check if this is a comparison query (original method)
    if is_comparison_query(user_query):
        print("Detected comparison query")
        results, cities, call_carbon, call_pollution = await handle_comparison(user_query)
        if results:
            formatted = format_comparison_results(results, cities, user_query, call_carbon, call_pollution)
            return formatted, "Comparison_Tool"
    
    # Health-related keywords should go to Effects tool
    health_keywords = [
        'cancer', 'health', 'disease', 'illness', 'sick', 'medical', 
        'respiratory', 'cardiovascular', 'lung', 'heart', 'asthma',
        'toxic', 'poison', 'hazardous', 'risk', 'mortality', 'death',
        'chronic', 'acute', 'symptom', 'hospital', 'patient'
    ]
    
    # Pollution/air quality keywords
    pollution_keywords = [
        'air quality', 'aqi', 'pollution index', 'health index', 
        'pollution level', 'pm2.5', 'pm10', 'air pollution'
    ]
    
    # Carbon footprint keywords
    carbon_keywords = [
        'carbon', 'footprint', 'co2', 'emission', 'greenhouse gas'
    ]
    
    # Policy keywords
    policy_keywords = [
        'policy', 'policies', 'act', 'acts', 'regulation', 'law', 'government',
        'agreement', 'treaty', 'legislation', 'prevalent', 'relevant',
        'related to', 'pertaining to'
    ]
    
    # Effects keywords
    effects_keywords = [
        'effect', 'impact', 'degradation', 'climate change',
        'global warming', 'environmental impact'
    ]
    
    # Web search keywords
    search_keywords = [
        'search', 'news', 'current', 'latest', 'recent', 'update'
    ]
    
    # Wikipedia keywords - only when explicitly asked
    wiki_keywords = [
        'wikipedia'
    ]
    
    # General knowledge keywords
    general_keywords = [
        'tell me about', 'what is', 'what are', 'explain', 
        'describe', 'information on', 'tell me', 'main'
    ]
    
    # Sustainability tips keywords
    tips_keywords = [
        'tip', 'advice', 'sustainable', 'green', 'eco friendly',
        'how to', 'guide', 'suggestion'
    ]
    
    # Priority 1: Health-related queries (most specific)
    if any(keyword in query_lower for keyword in health_keywords):
        print(f"Routing to Environmental_Effects_RAG (health query)")
        tool = "Environmental_Effects_RAG"
        result = await call_mcp_tool(tool, user_query)
        cleaned_result = clean_response(result)
        return cleaned_result, tool
    
    # Priority 2: Pollution index
    elif any(keyword in query_lower for keyword in pollution_keywords):
        print(f"Routing to Pollution_Health_Index")
        tool = "Pollution_Health_Index"
        result = await call_mcp_tool(tool, user_query)
        return result, tool
    
    # Priority 3: Carbon footprint
    elif any(keyword in query_lower for keyword in carbon_keywords):
        print(f"Routing to Carbon_Footprint_Calculator")
        tool = "Carbon_Footprint_Calculator"
        result = await call_mcp_tool(tool, user_query)
        return result, tool
    
    # Priority 4: Sustainability tips
    elif any(keyword in query_lower for keyword in tips_keywords):
        print(f"Routing to Sustainability_Tips")
        tool = "Sustainability_Tips"
        result = await call_mcp_tool(tool, user_query)
        return result, tool
    
    # Priority 5: Web search
    elif any(keyword in query_lower for keyword in search_keywords):
        print(f"Routing to Web_Search")
        tool = "Web_Search"
        result = await call_mcp_tool(tool, user_query)
        return result, tool
    
    # Priority 6: General knowledge (routes to Policies RAG)
    elif any(keyword in query_lower for keyword in general_keywords):
        print(f"Routing to Environmental_Policies_RAG (general knowledge)")
        tool = "Environmental_Policies_RAG"
        result = await call_mcp_tool(tool, user_query)
        cleaned_result = clean_response(result)
        return cleaned_result, tool
    
    # Priority 7: Wikipedia (only when explicitly asked)
    elif any(keyword in query_lower for keyword in wiki_keywords):
        print(f"Routing to Wikipedia_Knowledge")
        tool = "Wikipedia_Knowledge"
        result = await call_mcp_tool(tool, user_query)
        return result, tool
    
    # Priority 8: Environmental effects
    elif any(keyword in query_lower for keyword in effects_keywords):
        print(f"Routing to Environmental_Effects_RAG")
        tool = "Environmental_Effects_RAG"
        result = await call_mcp_tool(tool, user_query)
        cleaned_result = clean_response(result)
        return cleaned_result, tool
    
    # Priority 9: Environmental policies
    elif any(keyword in query_lower for keyword in policy_keywords):
        print(f"Routing to Environmental_Policies_RAG")
        tool = "Environmental_Policies_RAG"
        result = await call_mcp_tool(tool, user_query)
        cleaned_result = clean_response(result)
        return cleaned_result, tool
    
    else:
        # Default to policies for general environmental queries
        print(f"Routing to default: Environmental_Policies_RAG")
        tool = "Environmental_Policies_RAG"
        result = await call_mcp_tool(tool, user_query)
        cleaned_result = clean_response(result)
        return cleaned_result, tool

# Wrapper function to maintain compatibility
def process_with_mcp(user_query):
    """Wrapper for async function"""
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
    
    # MCP Server Status
    st.markdown("---")
    st.subheader("MCP Server Status")
    
    # Test connection button
    if st.button("Test Connection"):
        async def test_connection():
            try:
                async with MCPClient() as client:
                    if await client.ping():
                        st.session_state.mcp_connected = True
                        return "Connected"
                    else:
                        st.session_state.mcp_connected = False
                        return "Disconnected"
            except:
                st.session_state.mcp_connected = False
                return "Disconnected"
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        status = loop.run_until_complete(test_connection())
        loop.close()
        st.info(status)
    
    # Display connection status
    if st.session_state.mcp_connected:
        st.markdown('<div class="status-box connected">MCP Server Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box disconnected">MCP Server Disconnected</div>', unsafe_allow_html=True)
        st.markdown("Run `python greenmind_mcp.py` in a terminal to start the server.")
    
    # Available tools
    st.markdown("---")
    st.subheader("Available Tools")
    tools_list = [
        "Environmental_Policies_RAG",
        "Environmental_Effects_RAG (Health impacts)",
        "Web_Search",
        "Wikipedia_Knowledge",
        "Pollution_Health_Index",
        "Carbon_Footprint_Calculator",
        "Sustainability_Tips",
        "Comparison_Tool (Multi-city)"
    ]
    for tool in tools_list:
        st.markdown(f'<div class="tool-item">• {tool}</div>', unsafe_allow_html=True)
    
    # Example queries
    st.markdown("---")
    st.subheader("Try These Queries")
    st.markdown("""
    • "What environmental factors cause cancer?"
    • "Health effects of air pollution"
    • "Compare carbon footprint of Delhi and London"
    • "Air quality in Mumbai vs Tokyo"
    • "Compare pollution index of Chennai and Hyderabad"
    • "Compare air quality of Cochin and Trivandrum"
    • "What is the carbon footprint and pollution index of Delhi and Mumbai?"
    """)
    
    st.markdown("---")
    if st.button("Clear Conversation"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Display welcome message with quote
if st.session_state.messages and len(st.session_state.messages) > 0:
    # Show the first message (welcome) with quote
    with st.chat_message("assistant"):
        # Create stylish quote HTML
        if 'quote_data' in st.session_state:
            quote_html = f'''
            <div class="elegant-quote">
                <div class="quote-text">{st.session_state.quote_data["text"]}</div>
                <div class="quote-author">— {st.session_state.quote_data["author"]}</div>
            </div>
            '''
            st.markdown(quote_html, unsafe_allow_html=True)
        
        # Show the rest of the welcome message
        st.markdown(st.session_state.messages[0]["content"])

# Display remaining messages (skip the first one since we already showed it with quote)
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Ask me about environmental sustainability...")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response via MCP
    with st.chat_message("assistant"):
        with st.spinner("GreenMind is thinking..."):
            response, tool_used = process_with_mcp(prompt)
            st.markdown(response)
            
            # Show which tool was used
            if tool_used:
                st.caption(f"Used tool: {tool_used}")
    
    # Add assistant response
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