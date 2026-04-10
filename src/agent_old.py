# src/agent.py
'''
import os
import sys
from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.tools import BaseTool

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from src.tools.rag_tools import PoliciesRAGTool, EffectsRAGTool
from src.tools.web_search import WebSearchTool, WikipediaTool
from src.tools.pollution_index import PollutionIndexTool
from src.tools.extra_tools import CarbonFootprintCalculator, SustainabilityTipsTool
from src.utils.logger import GreenMindLogger

class GreenMindAgent:
    def __init__(self):
        """Initialize the GreenMind Agent with all tools"""
        print("=" * 60)
        print("GREENMIND AGENT - Initializing")
        print("=" * 60)
        
        # Initialize logger
        self.logger = GreenMindLogger()
        print("\n1. Logger initialized")
        
        # Initialize LLM
        print("\n2. Initializing Gemini LLM...")
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL_NAME,
            google_api_key=Config.GEMINI_API_KEY,
            temperature=Config.TEMPERATURE,
            convert_system_message_to_human=True
        )
        print("   LLM initialized")
        
        # Initialize tools
        print("\n3. Loading tools...")
        self.tools = self._load_tools()
        print(f"   Loaded {len(self.tools)} tools")
        
        # Initialize memory
        print("\n4. Initializing conversation memory...")
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        print("   Memory initialized")
        
        # Create agent
        print("\n5. Creating agent with personality...")
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            early_stopping_method="generate",
            agent_kwargs={
                "system_message": Config.AGENT_PERSONALITY,
                "human_message": "{input}\n\n{agent_scratchpad}"
            }
        )
        print("   Agent created successfully")
        print("\n" + "=" * 60)
        print("GREENMIND AGENT - Ready!")
        print("=" * 60)
    
    def _load_tools(self):
        """Load all available tools"""
        tools = []
        
        # RAG Tools
        try:
            tools.append(PoliciesRAGTool())
            print("   - Policies RAG Tool loaded")
        except Exception as e:
            print(f"   - Warning: Policies RAG Tool not loaded: {str(e)}")
        
        try:
            tools.append(EffectsRAGTool())
            print("   - Effects RAG Tool loaded")
        except Exception as e:
            print(f"   - Warning: Effects RAG Tool not loaded: {str(e)}")
        
        # Web Tools
        try:
            tools.append(WebSearchTool())
            print("   - Web Search Tool loaded")
        except Exception as e:
            print(f"   - Warning: Web Search Tool not loaded: {str(e)}")
        
        try:
            tools.append(WikipediaTool())
            print("   - Wikipedia Tool loaded")
        except Exception as e:
            print(f"   - Warning: Wikipedia Tool not loaded: {str(e)}")
        
        # Pollution Tool
        try:
            tools.append(PollutionIndexTool())
            print("   - Pollution Index Tool loaded")
        except Exception as e:
            print(f"   - Warning: Pollution Index Tool not loaded: {str(e)}")
        
        # Extra Tools
        try:
            tools.append(CarbonFootprintCalculator())
            print("   - Carbon Footprint Calculator loaded")
        except Exception as e:
            print(f"   - Warning: Carbon Footprint Calculator not loaded: {str(e)}")
        
        try:
            tools.append(SustainabilityTipsTool())
            print("   - Sustainability Tips Tool loaded")
        except Exception as e:
            print(f"   - Warning: Sustainability Tips Tool not loaded: {str(e)}")
        
        return tools
    
    def process_query(self, user_query):
        """Process a user query and return response"""
        print(f"\n{'='*60}")
        print(f"Processing query: {user_query}")
        print(f"{'='*60}")
        
        tools_used = []
        
        try:
            # Get response from agent
            response = self.agent.run(input=user_query)
            
            # Log the interaction
            self.logger.log_agent_response(user_query, response, tools_used)
            
            return response
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            print(f"Error: {str(e)}")
            self.logger.log_error(str(e))
            return error_msg
    
    def get_tool_names(self):
        """Return list of available tool names"""
        return [tool.name for tool in self.tools]
'''

# src/agent.py - Simplified version
import os
import sys
from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from src.tools.rag_tools import PoliciesRAGTool, EffectsRAGTool
from src.tools.web_search import WebSearchTool, WikipediaTool
from src.tools.pollution_index import PollutionIndexTool
from src.tools.extra_tools import CarbonFootprintCalculator, SustainabilityTipsTool
from src.utils.logger import GreenMindLogger

print("Loading GreenMindAgent class...")

class GreenMindAgent:
    def __init__(self):
        print("GreenMindAgent __init__ called")
        self.logger = GreenMindLogger()
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL_NAME,
            google_api_key=Config.GEMINI_API_KEY,
            temperature=Config.TEMPERATURE
        )
        self.tools = self._load_tools()
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True
        )
    
    def _load_tools(self):
        tools = []
        tools.append(PoliciesRAGTool())
        tools.append(EffectsRAGTool())
        tools.append(WebSearchTool())
        tools.append(WikipediaTool())
        tools.append(PollutionIndexTool())
        tools.append(CarbonFootprintCalculator())
        tools.append(SustainabilityTipsTool())
        return tools
    
    def process_query(self, user_query):
        try:
            response = self.agent.run(input=user_query)
            return response
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_tool_names(self):
        return [tool.name for tool in self.tools]

print("GreenMindAgent class loaded successfully")