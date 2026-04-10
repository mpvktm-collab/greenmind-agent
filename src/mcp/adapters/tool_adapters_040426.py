# src/mcp/adapters/tool_adapters.py
from tools.rag_tools_040526 import PoliciesRAGTool, EffectsRAGTool
from src.tools.web_search import WebSearchTool, WikipediaTool
from tools.pollution_index import PollutionIndexTool
from tools.extra_tools_040626 import CarbonFootprintCalculator, SustainabilityTipsTool

class ToolAdapter:
    def __init__(self, name, handle, description=""):
        self.name = name
        self.handle = handle
        self.description = description

def create_adapters():
    """Create all tool adapters for the MCP server"""
    adapters = []
    
    # RAG tools
    try:
        policies_tool = PoliciesRAGTool()
        adapters.append(ToolAdapter(
            name="Environmental_Policies_RAG",
            handle=lambda input: policies_tool._run(input),
            description="Retrieves information about environmental policies, regulations, and acts from various countries. Use this when asked about environmental laws, policies, regulations, or government initiatives."
        ))
        print("Created adapter for Environmental_Policies_RAG")
    except Exception as e:
        print(f"Failed to create Environmental_Policies_RAG: {str(e)}")
    
    try:
        effects_tool = EffectsRAGTool()
        adapters.append(ToolAdapter(
            name="Environmental_Effects_RAG",
            handle=lambda input: effects_tool._run(input),
            description="Provides information about environmental degradation, causes, and its effects on health and ecosystems. Use this when asked about environmental impacts, climate change effects, pollution consequences, or health effects."
        ))
        print("Created adapter for Environmental_Effects_RAG")
    except Exception as e:
        print(f"Failed to create Environmental_Effects_RAG: {str(e)}")
    
    # Web tools
    try:
        web_tool = WebSearchTool()
        adapters.append(ToolAdapter(
            name="Web_Search",
            handle=lambda input: web_tool._run(input),
            description="Searches the web for current environmental news and information. Use this for recent developments and current events."
        ))
        print("Created adapter for Web_Search")
    except Exception as e:
        print(f"Failed to create Web_Search: {str(e)}")
    
    try:
        wiki_tool = WikipediaTool()
        adapters.append(ToolAdapter(
            name="Wikipedia_Knowledge",
            handle=lambda input: wiki_tool._run(input),
            description="Searches Wikipedia for environmental topics. Use this for well-known environmental topics and concepts."
        ))
        print("Created adapter for Wikipedia_Knowledge")
    except Exception as e:
        print(f"Failed to create Wikipedia_Knowledge: {str(e)}")
    
    # Pollution tool
    try:
        pollution_tool = PollutionIndexTool()
        adapters.append(ToolAdapter(
            name="Pollution_Health_Index",
            handle=lambda input: pollution_tool._run(input),
            description="Retrieves current pollution levels and environmental health indices for any location. Use this when asked about air quality, pollution levels, or AQI."
        ))
        print("Created adapter for Pollution_Health_Index")
    except Exception as e:
        print(f"Failed to create Pollution_Health_Index: {str(e)}")
    
    # Carbon footprint tool
    try:
        carbon_tool = CarbonFootprintCalculator()
        adapters.append(ToolAdapter(
            name="Carbon_Footprint_Calculator",
            handle=lambda input: carbon_tool._run(input),
            description="Provides estimates of carbon footprint for various activities and cities. Use this when asked about carbon footprint of activities like driving, flying, or specific cities."
        ))
        print("Created adapter for Carbon_Footprint_Calculator")
    except Exception as e:
        print(f"Failed to create Carbon_Footprint_Calculator: {str(e)}")
    
    # Sustainability tips tool
    try:
        tips_tool = SustainabilityTipsTool()
        adapters.append(ToolAdapter(
            name="Sustainability_Tips",
            handle=lambda input: tips_tool._run(input),
            description="Provides practical, everyday tips for living more sustainably. Use this when asked for eco-friendly tips, sustainable living advice, or green lifestyle suggestions."
        ))
        print("Created adapter for Sustainability_Tips")
    except Exception as e:
        print(f"Failed to create Sustainability_Tips: {str(e)}")
    
    print(f"Total adapters created: {len(adapters)}")
    return adapters