from src.tools.rag_tools import PoliciesRAGTool, EffectsRAGTool
from src.tools.web_search import WebSearchTool, WikipediaTool
from src.tools.pollution_index import PollutionIndexTool
from src.tools.extra_tools import CarbonFootprintCalculator, SustainabilityTipsTool

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
            handle=lambda query: policies_tool._run(query),
            description="Retrieves information about environmental policies"
        ))
        print("Created adapter for Environmental_Policies_RAG")
    except Exception as e:
        print(f"Failed to create Environmental_Policies_RAG: {str(e)}")
    
    try:
        effects_tool = EffectsRAGTool()
        adapters.append(ToolAdapter(
            name="Environmental_Effects_RAG",
            handle=lambda query: effects_tool._run(query),
            description="Provides information about environmental effects"
        ))
        print("Created adapter for Environmental_Effects_RAG")
    except Exception as e:
        print(f"Failed to create Environmental_Effects_RAG: {str(e)}")
    
    # Web tools
    try:
        web_tool = WebSearchTool()
        adapters.append(ToolAdapter(
            name="Web_Search",
            handle=lambda query: web_tool._run(query),
            description="Searches the web for current environmental news"
        ))
        print("Created adapter for Web_Search")
    except Exception as e:
        print(f"Failed to create Web_Search: {str(e)}")
    
    try:
        wiki_tool = WikipediaTool()
        adapters.append(ToolAdapter(
            name="Wikipedia_Knowledge",
            handle=lambda query: wiki_tool._run(query),
            description="Searches Wikipedia for environmental topics"
        ))
        print("Created adapter for Wikipedia_Knowledge")
    except Exception as e:
        print(f"Failed to create Wikipedia_Knowledge: {str(e)}")
    
    # Pollution tool
    try:
        pollution_tool = PollutionIndexTool()
        adapters.append(ToolAdapter(
            name="Pollution_Health_Index",
            handle=lambda query: pollution_tool._run(query),
            description="Retrieves current pollution levels for any location"
        ))
        print("Created adapter for Pollution_Health_Index")
    except Exception as e:
        print(f"Failed to create Pollution_Health_Index: {str(e)}")
    
    # Carbon footprint tool
    try:
        carbon_tool = CarbonFootprintCalculator()
        adapters.append(ToolAdapter(
            name="Carbon_Footprint_Calculator",
            handle=lambda query: carbon_tool._run(query),
            description="Provides estimates of carbon footprint for activities and cities"
        ))
        print("Created adapter for Carbon_Footprint_Calculator")
    except Exception as e:
        print(f"Failed to create Carbon_Footprint_Calculator: {str(e)}")
    
    # Sustainability tips tool
    try:
        tips_tool = SustainabilityTipsTool()
        adapters.append(ToolAdapter(
            name="Sustainability_Tips",
            handle=lambda query: tips_tool._run(query),
            description="Provides practical tips for sustainable living"
        ))
        print("Created adapter for Sustainability_Tips")
    except Exception as e:
        print(f"Failed to create Sustainability_Tips: {str(e)}")
    
    print(f"Total adapters created: {len(adapters)}")
    return adapters