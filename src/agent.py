# src/agent.py - Full Featured Version
import os
import sys
from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
            temperature=Config.TEMPERATURE
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
        
        # Create agent with personality
        print("\n5. Creating agent with GreenMind personality...")
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
                "system_message": Config.AGENT_PERSONALITY
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
            error_msg = f"Warning: Policies RAG Tool not loaded: {str(e)}"
            print(f"   {error_msg}")
            self.logger.log_error(error_msg, "PoliciesRAGTool")
        
        try:
            tools.append(EffectsRAGTool())
            print("   - Effects RAG Tool loaded")
        except Exception as e:
            error_msg = f"Warning: Effects RAG Tool not loaded: {str(e)}"
            print(f"   {error_msg}")
            self.logger.log_error(error_msg, "EffectsRAGTool")
        
        # Web Tools
        try:
            tools.append(WebSearchTool())
            print("   - Web Search Tool loaded")
        except Exception as e:
            error_msg = f"Warning: Web Search Tool not loaded: {str(e)}"
            print(f"   {error_msg}")
            self.logger.log_error(error_msg, "WebSearchTool")
        
        try:
            tools.append(WikipediaTool())
            print("   - Wikipedia Tool loaded")
        except Exception as e:
            error_msg = f"Warning: Wikipedia Tool not loaded: {str(e)}"
            print(f"   {error_msg}")
            self.logger.log_error(error_msg, "WikipediaTool")
        
        # Pollution Tool
        try:
            tools.append(PollutionIndexTool())
            print("   - Pollution Index Tool loaded")
        except Exception as e:
            error_msg = f"Warning: Pollution Index Tool not loaded: {str(e)}"
            print(f"   {error_msg}")
            self.logger.log_error(error_msg, "PollutionIndexTool")
        
        # Extra Tools
        try:
            tools.append(CarbonFootprintCalculator())
            print("   - Carbon Footprint Calculator loaded")
        except Exception as e:
            error_msg = f"Warning: Carbon Footprint Calculator not loaded: {str(e)}"
            print(f"   {error_msg}")
            self.logger.log_error(error_msg, "CarbonFootprintCalculator")
        
        try:
            tools.append(SustainabilityTipsTool())
            print("   - Sustainability Tips Tool loaded")
        except Exception as e:
            error_msg = f"Warning: Sustainability Tips Tool not loaded: {str(e)}"
            print(f"   {error_msg}")
            self.logger.log_error(error_msg, "SustainabilityTipsTool")
        
        return tools
    
    def process_query(self, user_query):
        """Process a user query and return response with logging using invoke()"""
        print(f"\n{'='*60}")
        print(f"Processing query: {user_query}")
        print(f"{'='*60}")
        
        # Track which tools are used (can be enhanced to parse from agent output)
        tools_used = []
        
        try:
            # Log the query
            self.logger.logger.info(f"USER QUERY: {user_query}")
            
            # Get response from agent using invoke() instead of run()
            response = self.agent.invoke({"input": user_query})
            
            # Extract the output from the response
            if isinstance(response, dict) and "output" in response:
                output_text = response["output"]
            else:
                output_text = str(response)
            
            # Log the response
            self.logger.log_agent_response(user_query, output_text, tools_used)
            
            return output_text
            
        except Exception as e:
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            print(f"Error: {str(e)}")
            self.logger.log_error(str(e))
            return error_msg
    
    def get_tool_names(self):
        """Return list of available tool names"""
        return [tool.name for tool in self.tools]
    
    def get_tool_count(self):
        """Return number of available tools"""
        return len(self.tools)