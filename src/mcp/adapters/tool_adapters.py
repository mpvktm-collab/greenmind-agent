# src/mcp/adapters/tool_adapters.py
from src.tools.rag_tools import PoliciesRAGTool, EffectsRAGTool
from src.tools.web_search import WebSearchTool, WikipediaTool
from src.tools.pollution_index import PollutionIndexTool
from src.tools.extra_tools import CarbonFootprintCalculator, SustainabilityTipsTool

class ToolAdapter:
    def __init__(self, name, handle, description=""):
        self.name = name
        self.handle = handle  # Changed from 'handler' to 'handle'
        self.description = description

def create_adapters():
    """Create all tool adapters for the MCP server"""
    adapters = []
    
    # Initialize RAG tools
    try:
        policies_tool = PoliciesRAGTool()
        adapters.append(ToolAdapter(
            name="Environmental_Policies_RAG",
            handle=policies_tool._run,  # Use _run method
            description="Retrieves information about environmental policies, regulations, and acts from various countries."
        ))
        print("Created adapter for Environmental_Policies_RAG")
    except Exception as e:
        print(f"Failed to create Environmental_Policies_RAG adapter: {str(e)}")
    
    try:
        effects_tool = EffectsRAGTool()
        adapters.append(ToolAdapter(
            name="Environmental_Effects_RAG",
            handle=effects_tool._run,  # Use _run method
            description="Provides information about environmental degradation, causes, and its effects on health and ecosystems."
        ))
        print("Created adapter for Environmental_Effects_RAG")
    except Exception as e:
        print(f"Failed to create Environmental_Effects_RAG adapter: {str(e)}")
    
    # Web tools
    try:
        web_tool = WebSearchTool()
        adapters.append(ToolAdapter(
            name="Web_Search",
            handle=web_tool._run,
            description="Searches the web for current environmental news and information."
        ))
        print("Created adapter for Web_Search")
    except Exception as e:
        print(f"Failed to create Web_Search adapter: {str(e)}")
    
    try:
        wiki_tool = WikipediaTool()
        adapters.append(ToolAdapter(
            name="Wikipedia_Knowledge",
            handle=wiki_tool._run,
            description="Searches Wikipedia for environmental topics."
        ))
        print("Created adapter for Wikipedia_Knowledge")
    except Exception as e:
        print(f"Failed to create Wikipedia_Knowledge adapter: {str(e)}")
    
    # Pollution tool
    try:
        pollution_tool = PollutionIndexTool()
        adapters.append(ToolAdapter(
            name="Pollution_Health_Index",
            handle=pollution_tool._run,
            description="Retrieves current pollution levels and environmental health indices for any location."
        ))
        print("Created adapter for Pollution_Health_Index")
    except Exception as e:
        print(f"Failed to create Pollution_Health_Index adapter: {str(e)}")
    
    # Carbon footprint tool
    try:
        carbon_tool = CarbonFootprintCalculator()
        adapters.append(ToolAdapter(
            name="Carbon_Footprint_Calculator",
            handle=carbon_tool._run,
            description="Provides estimates of carbon footprint for various activities and cities."
        ))
        print("Created adapter for Carbon_Footprint_Calculator")
    except Exception as e:
        print(f"Failed to create Carbon_Footprint_Calculator adapter: {str(e)}")
    
    # Sustainability tips tool
    try:
        tips_tool = SustainabilityTipsTool()
        adapters.append(ToolAdapter(
            name="Sustainability_Tips",
            handle=tips_tool._run,
            description="Provides practical, everyday tips for living more sustainably."
        ))
        print("Created adapter for Sustainability_Tips")
    except Exception as e:
        print(f"Failed to create Sustainability_Tips adapter: {str(e)}")
    
    print(f"Total adapters created: {len(adapters)}")
    return adapters