from src.tools.rag_tools import PoliciesRAGTool, EffectsRAGTool
from src.tools.web_search import WebSearchTool, WikipediaTool
from src.tools.pollution_index import PollutionIndexTool
from src.tools.extra_tools import CarbonFootprintCalculator, SustainabilityTipsTool

class ToolAdapter:
    def __init__(self, name, handler, description=""):
        self.name = name
        self.handler = handler
        self.description = description

def create_adapters():
    """Create all tool adapters for the MCP server"""
    adapters = []
    
    # Initialize RAG tools
    try:
        policies_tool = PoliciesRAGTool()
        adapters.append(ToolAdapter(
            name="Environmental_Policies_RAG",
            handler=policies_tool.run,
            description="Retrieves information about environmental policies, regulations, and acts from various countries. Use this when asked about environmental laws, policies, regulations, or government initiatives."
        ))
        print("Created adapter for Environmental_Policies_RAG")
    except Exception as e:
        print(f"Failed to create Environmental_Policies_RAG adapter: {str(e)}")
    
    try:
        effects_tool = EffectsRAGTool()
        adapters.append(ToolAdapter(
            name="Environmental_Effects_RAG",
            handler=effects_tool.run,
            description="Provides information about environmental degradation, causes, and its effects on health and ecosystems. Use this when asked about environmental impacts, climate change effects, pollution consequences, or health effects."
        ))
        print("Created adapter for Environmental_Effects_RAG")
    except Exception as e:
        print(f"Failed to create Environmental_Effects_RAG adapter: {str(e)}")
    
    # Web tools
    try:
        web_tool = WebSearchTool()
        adapters.append(ToolAdapter(
            name="Web_Search",
            handler=web_tool._run,
            description="Searches the web for current environmental news and information. Use this for recent developments and current events."
        ))
        print("Created adapter for Web_Search")
    except Exception as e:
        print(f"Failed to create Web_Search adapter: {str(e)}")
    
    try:
        wiki_tool = WikipediaTool()
        adapters.append(ToolAdapter(
            name="Wikipedia_Knowledge",
            handler=wiki_tool._run,
            description="Searches Wikipedia for environmental topics. Use this for well-known environmental topics and concepts."
        ))
        print("Created adapter for Wikipedia_Knowledge")
    except Exception as e:
        print(f"Failed to create Wikipedia_Knowledge adapter: {str(e)}")
    
    # Pollution tool
    try:
        pollution_tool = PollutionIndexTool()
        adapters.append(ToolAdapter(
            name="Pollution_Health_Index",
            handler=pollution_tool._run,
            description="Retrieves current pollution levels and environmental health indices for any location. Use this when asked about air quality, pollution levels, or AQI."
        ))
        print("Created adapter for Pollution_Health_Index")
    except Exception as e:
        print(f"Failed to create Pollution_Health_Index adapter: {str(e)}")
    
    # Carbon footprint tool
    try:
        carbon_tool = CarbonFootprintCalculator()
        adapters.append(ToolAdapter(
            name="Carbon_Footprint_Calculator",
            handler=carbon_tool._run,
            description="Provides estimates of carbon footprint for various activities and cities. Use this when asked about carbon footprint of activities like driving, flying, or specific cities."
        ))
        print("Created adapter for Carbon_Footprint_Calculator")
    except Exception as e:
        print(f"Failed to create Carbon_Footprint_Calculator adapter: {str(e)}")
    
    # Sustainability tips tool
    try:
        tips_tool = SustainabilityTipsTool()
        adapters.append(ToolAdapter(
            name="Sustainability_Tips",
            handler=tips_tool._run,
            description="Provides practical, everyday tips for living more sustainably. Use this when asked for eco-friendly tips, sustainable living advice, or green lifestyle suggestions."
        ))
        print("Created adapter for Sustainability_Tips")
    except Exception as e:
        print(f"Failed to create Sustainability_Tips adapter: {str(e)}")
    
    print(f"Total adapters created: {len(adapters)}")
    return adapters