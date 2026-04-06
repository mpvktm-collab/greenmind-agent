from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import BaseTool
from typing import Optional
from langchain.callbacks.manager import CallbackManagerForToolRun
import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from src.database.vector_store import VectorStoreManager


class PoliciesRAGTool(BaseTool):
    """Tool for querying environmental policies"""
    
    name: str = "Environmental_Policies_RAG"
    description: str = """
    Retrieves information about environmental policies, regulations, and acts from various countries.
    Use this when asked about environmental laws, policies, regulations, or government initiatives.
    Input should be a specific question about environmental policies.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, '_qa_chain', None)
        object.__setattr__(self, '_llm', None)
        self._initialize()
    
    def _initialize(self):
        try:
            print("Initializing PoliciesRAGTool...")
            manager = VectorStoreManager()
            store_path = os.path.join(Config.VECTOR_STORE_PATH, "policies_store")
            data_path = Config.POLICIES_DIR
            
            print(f"Loading policies vector store from {store_path}")
            vector_store = manager.load_or_create_store(store_path, data_path)
            
            if vector_store:
                object.__setattr__(self, '_llm', ChatGoogleGenerativeAI(
                    model=Config.MODEL_NAME,
                    google_api_key=Config.GEMINI_API_KEY,
                    temperature=0.2,
                    convert_system_message_to_human=True,
                    request_timeout=30  # Add timeout
                ))
                object.__setattr__(self, '_qa_chain', RetrievalQA.from_chain_type(
                    llm=self._llm,
                    retriever=vector_store.as_retriever(search_kwargs={"k": 3})
                ))
                print("PoliciesRAGTool initialized successfully")
            else:
                print("Warning: Policies vector store not available")
        except Exception as e:
            print(f"Error initializing PoliciesRAGTool: {str(e)}")
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        qa_chain = getattr(self, '_qa_chain', None)
        if not qa_chain:
            return "Environmental policies database is being loaded. Please try again in a moment."
        
        try:
            # Run with a timeout
            result = qa_chain.run(query)
            return result
        except Exception as e:
            if "timeout" in str(e).lower():
                return "The request timed out. Please try a simpler question."
            return f"Error retrieving policies: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class EffectsRAGTool(BaseTool):
    """Tool for querying environmental effects"""
    
    name: str = "Environmental_Effects_RAG"
    description: str = """
    Provides information about environmental degradation, causes, and its effects on health and ecosystems.
    Use this when asked about environmental impacts, climate change effects, pollution consequences, or health effects.
    Input should be a specific question about environmental effects.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, '_qa_chain', None)
        object.__setattr__(self, '_llm', None)
        self._initialize()
    
    def _initialize(self):
        try:
            print("Initializing EffectsRAGTool...")
            manager = VectorStoreManager()
            store_path = os.path.join(Config.VECTOR_STORE_PATH, "effects_store")
            data_path = Config.EFFECTS_DIR
            
            print(f"Loading effects vector store from {store_path}")
            vector_store = manager.load_or_create_store(store_path, data_path)
            
            if vector_store:
                object.__setattr__(self, '_llm', ChatGoogleGenerativeAI(
                    model=Config.MODEL_NAME,
                    google_api_key=Config.GEMINI_API_KEY,
                    temperature=0.2,
                    convert_system_message_to_human=True,
                    request_timeout=30  # Add timeout
                ))
                object.__setattr__(self, '_qa_chain', RetrievalQA.from_chain_type(
                    llm=self._llm,
                    retriever=vector_store.as_retriever(search_kwargs={"k": 3})
                ))
                print("EffectsRAGTool initialized successfully")
            else:
                print("Warning: Effects vector store not available")
        except Exception as e:
            print(f"Error initializing EffectsRAGTool: {str(e)}")
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        qa_chain = getattr(self, '_qa_chain', None)
        if not qa_chain:
            return "Environmental effects database is being loaded. Please try again in a moment."
        
        try:
            result = qa_chain.run(query)
            return result
        except Exception as e:
            if "timeout" in str(e).lower():
                return "The request timed out. Please try a simpler question."
            return f"Error retrieving environmental effects: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)