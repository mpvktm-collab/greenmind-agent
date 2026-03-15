# src/tools/rag_tools.py
import os
import sys
from typing import Optional, Type, Any
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import Field

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.database.vector_store import VectorStoreManager
from config import Config

class PoliciesRAGTool(BaseTool):
    """Tool for retrieving information about environmental policies"""
    
    name: str = "Environmental_Policies_RAG"
    description: str = """
    Retrieves information about environmental policies from various countries. 
    Use this tool when asked about specific environmental regulations, acts, policy frameworks, 
    or government commitments related to climate change and environment.
    Input should be a specific question about environmental policies.
    """
    
    # Define fields with default values
    vs_manager: Any = None
    vector_store: Any = None
    retriever: Any = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("Initializing PoliciesRAGTool...")
        self.vs_manager = VectorStoreManager()
        policies_path = os.path.join(Config.DATA_DIRECTORY, "policies")
        store_path = os.path.join(Config.VECTOR_STORE_PATH, "policies_store")
        self.vector_store = self.vs_manager.load_or_create_store(store_path, policies_path)
        if self.vector_store:
            self.retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 3}
            )
            print("PoliciesRAGTool initialized successfully")
        else:
            print("Warning: Policies vector store not found")
            self.retriever = None
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Search for policy information"""
        if not self.retriever:
            return "Policy information is not available. Please add policy documents first."
        
        try:
            docs = self.retriever.get_relevant_documents(query)
            if not docs:
                return "No relevant policy information found for your query."
            
            response = "Here is information from environmental policy documents:\n\n"
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('filename', 'Unknown source')
                response += f"[Source: {source}]\n"
                response += f"{doc.page_content}\n\n"
                response += "-" * 50 + "\n\n"
            
            return response
            
        except Exception as e:
            return f"Error retrieving policy information: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version of the tool"""
        return self._run(query)


class EffectsRAGTool(BaseTool):
    """Tool for retrieving information about environmental effects"""
    
    name: str = "Environmental_Effects_RAG"
    description: str = """
    Retrieves information about environmental degradation, causes, and effects. 
    Use this tool when asked about environmental impacts, consequences, pollution effects, 
    climate change impacts, or ecological changes.
    Input should be a specific question about environmental effects or impacts.
    """
    
    # Define fields with default values
    vs_manager: Any = None
    vector_store: Any = None
    retriever: Any = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("Initializing EffectsRAGTool...")
        self.vs_manager = VectorStoreManager()
        effects_path = os.path.join(Config.DATA_DIRECTORY, "effects")
        store_path = os.path.join(Config.VECTOR_STORE_PATH, "effects_store")
        self.vector_store = self.vs_manager.load_or_create_store(store_path, effects_path)
        if self.vector_store:
            self.retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 3}
            )
            print("EffectsRAGTool initialized successfully")
        else:
            print("Warning: Effects vector store not found")
            self.retriever = None
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Search for environmental effects information"""
        if not self.retriever:
            return "Environmental effects information is not available. Please add effects documents first."
        
        try:
            docs = self.retriever.get_relevant_documents(query)
            if not docs:
                return "No relevant environmental effects information found for your query."
            
            response = "Here is information from environmental effects documents:\n\n"
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('filename', 'Unknown source')
                response += f"[Source: {source}]\n"
                response += f"{doc.page_content}\n\n"
                response += "-" * 50 + "\n\n"
            
            return response
            
        except Exception as e:
            return f"Error retrieving environmental effects information: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version of the tool"""
        return self._run(query)