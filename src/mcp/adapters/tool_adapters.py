# src/mcp/adapters/tool_adapters.py
import asyncio
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class MCPToolAdapter:
    """Base adapter class for wrapping GreenMind tools for MCP"""
    
    def __init__(self, name: str, tool_instance, description: str = ""):
        self.name = name
        self.tool = tool_instance
        self.description = description
    
    async def handle(self, **params) -> str:
        """Handle tool calls - to be overridden by subclasses"""
        raise NotImplementedError
    
    def get_info(self) -> Dict[str, Any]:
        """Get tool information"""
        return {
            "name": self.name,
            "description": self.description
        }

class PoliciesRAGAdapter(MCPToolAdapter):
    """Adapter for PoliciesRAGTool"""
    
    def __init__(self, tool_instance):
        super().__init__(
            "Environmental_Policies_RAG", 
            tool_instance,
            "Retrieves information about environmental policies from various countries"
        )
    
    async def handle(self, **params) -> str:
        try:
            query = params.get("input", params.get("query", ""))
            if not query:
                return "Error: No query provided"
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.tool._run, query)
            return result
        except Exception as e:
            logger.error(f"Error in PoliciesRAGAdapter: {str(e)}")
            return f"Error: {str(e)}"

class EffectsRAGAdapter(MCPToolAdapter):
    """Adapter for EffectsRAGTool"""
    
    def __init__(self, tool_instance):
        super().__init__(
            "Environmental_Effects_RAG", 
            tool_instance,
            "Retrieves information about environmental degradation, causes, and effects"
        )
    
    async def handle(self, **params) -> str:
        try:
            query = params.get("input", params.get("query", ""))
            if not query:
                return "Error: No query provided"
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.tool._run, query)
            return result
        except Exception as e:
            logger.error(f"Error in EffectsRAGAdapter: {str(e)}")
            return f"Error: {str(e)}"

class WebSearchAdapter(MCPToolAdapter):
    """Adapter for WebSearchTool"""
    
    def __init__(self, tool_instance):
        super().__init__(
            "Web_Search", 
            tool_instance,
            "Searches the web for current environmental news and information"
        )
    
    async def handle(self, **params) -> str:
        try:
            query = params.get("input", params.get("query", ""))
            if not query:
                return "Error: No query provided"
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.tool._run, query)
            return result
        except Exception as e:
            logger.error(f"Error in WebSearchAdapter: {str(e)}")
            return f"Error: {str(e)}"

class WikipediaAdapter(MCPToolAdapter):
    """Adapter for WikipediaTool"""
    
    def __init__(self, tool_instance):
        super().__init__(
            "Wikipedia_Knowledge", 
            tool_instance,
            "Searches Wikipedia for environmental topics, policies, and scientific concepts"
        )
    
    async def handle(self, **params) -> str:
        try:
            query = params.get("input", params.get("query", ""))
            if not query:
                return "Error: No query provided"
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.tool._run, query)
            return result
        except Exception as e:
            logger.error(f"Error in WikipediaAdapter: {str(e)}")
            return f"Error: {str(e)}"

class PollutionIndexAdapter(MCPToolAdapter):
    """Adapter for PollutionIndexTool"""
    
    def __init__(self, tool_instance):
        super().__init__(
            "Pollution_Health_Index", 
            tool_instance,
            "Retrieves current pollution levels and environmental health indices for any location"
        )
    
    async def handle(self, **params) -> str:
        try:
            location = params.get("input", params.get("location", ""))
            if not location:
                return "Error: No location provided"
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.tool._run, location)
            return result
        except Exception as e:
            logger.error(f"Error in PollutionIndexAdapter: {str(e)}")
            return f"Error: {str(e)}"

class CarbonFootprintAdapter(MCPToolAdapter):
    """Adapter for CarbonFootprintCalculator"""
    
    def __init__(self, tool_instance):
        super().__init__(
            "Carbon_Footprint_Calculator", 
            tool_instance,
            "Provides estimates of carbon footprint for various activities and suggests reduction strategies"
        )
    
    async def handle(self, **params) -> str:
        try:
            activity = params.get("input", params.get("activity", ""))
            if not activity:
                return "Error: No activity provided"
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.tool._run, activity)
            return result
        except Exception as e:
            logger.error(f"Error in CarbonFootprintAdapter: {str(e)}")
            return f"Error: {str(e)}"

class SustainabilityTipsAdapter(MCPToolAdapter):
    """Adapter for SustainabilityTipsTool"""
    
    def __init__(self, tool_instance):
        super().__init__(
            "Sustainability_Tips", 
            tool_instance,
            "Provides practical, everyday tips for living more sustainably"
        )
    
    async def handle(self, **params) -> str:
        try:
            category = params.get("input", params.get("category", "general"))
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.tool._run, category)
            return result
        except Exception as e:
            logger.error(f"Error in SustainabilityTipsAdapter: {str(e)}")
            return f"Error: {str(e)}"

def create_adapters() -> List[MCPToolAdapter]:
    """Create and return all tool adapters with their tool instances"""
    adapters = []
    
    try:
        # Import tools
        from src.tools.rag_tools import PoliciesRAGTool, EffectsRAGTool
        from src.tools.web_search import WebSearchTool, WikipediaTool
        from src.tools.pollution_index import PollutionIndexTool
        from src.tools.extra_tools import CarbonFootprintCalculator, SustainabilityTipsTool
        
        # Create tool instances
        print("  Initializing tools...")
        
        # Policies RAG
        try:
            policies_tool = PoliciesRAGTool()
            adapters.append(PoliciesRAGAdapter(policies_tool))
            print("  ✓ Policies RAG adapter created")
        except Exception as e:
            print(f"  ✗ Failed to create Policies RAG adapter: {str(e)}")
        
        # Effects RAG
        try:
            effects_tool = EffectsRAGTool()
            adapters.append(EffectsRAGAdapter(effects_tool))
            print("  ✓ Effects RAG adapter created")
        except Exception as e:
            print(f"  ✗ Failed to create Effects RAG adapter: {str(e)}")
        
        # Web Search
        try:
            web_tool = WebSearchTool()
            adapters.append(WebSearchAdapter(web_tool))
            print("  ✓ Web Search adapter created")
        except Exception as e:
            print(f"  ✗ Failed to create Web Search adapter: {str(e)}")
        
        # Wikipedia
        try:
            wiki_tool = WikipediaTool()
            adapters.append(WikipediaAdapter(wiki_tool))
            print("  ✓ Wikipedia adapter created")
        except Exception as e:
            print(f"  ✗ Failed to create Wikipedia adapter: {str(e)}")
        
        # Pollution Index
        try:
            pollution_tool = PollutionIndexTool()
            adapters.append(PollutionIndexAdapter(pollution_tool))
            print("  ✓ Pollution Index adapter created")
        except Exception as e:
            print(f"  ✗ Failed to create Pollution Index adapter: {str(e)}")
        
        # Carbon Footprint
        try:
            carbon_tool = CarbonFootprintCalculator()
            adapters.append(CarbonFootprintAdapter(carbon_tool))
            print("  ✓ Carbon Footprint adapter created")
        except Exception as e:
            print(f"  ✗ Failed to create Carbon Footprint adapter: {str(e)}")
        
        # Sustainability Tips
        try:
            tips_tool = SustainabilityTipsTool()
            adapters.append(SustainabilityTipsAdapter(tips_tool))
            print("  ✓ Sustainability Tips adapter created")
        except Exception as e:
            print(f"  ✗ Failed to create Sustainability Tips adapter: {str(e)}")
        
    except ImportError as e:
        print(f"  ✗ Import error: {str(e)}")
        print("  Make sure all tool modules exist in src/tools/")
    except Exception as e:
        print(f"  ✗ Error creating adapters: {str(e)}")
    
    return adapters