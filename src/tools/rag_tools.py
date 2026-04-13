# -*- coding: utf-8 -*-
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import BaseTool
from typing import Optional
from langchain.callbacks.manager import CallbackManagerForToolRun
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config
from src.database.vector_store import VectorStoreManager


class PoliciesRAGTool(BaseTool):
    """Tool for querying environmental policies"""
    
    name: str = "Environmental_Policies_RAG"
    description: str = """
    Retrieves information about environmental policies, regulations, and acts from various countries.
    Use this when asked about environmental laws, policies, regulations, or government initiatives.
    """
    
    return_direct: bool = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, '_qa_chain', None)
        self._initialize()
    
    def _initialize(self):
        try:
            print("Initializing PoliciesRAGTool...")
            manager = VectorStoreManager()
            store_path = os.path.join(Config.VECTOR_STORE_PATH, "policies_store")
            data_path = Config.POLICIES_DIR
            
            print(f"Loading policies vector store from {store_path}")
            print(f"Data path: {data_path}")
            
            # List files in data directory for debugging
            if os.path.exists(data_path):
                files = os.listdir(data_path)
                print(f"Files in policies directory: {files}")
            else:
                print(f"Policies directory not found: {data_path}")
            
            vector_store = manager.load_or_create_store(store_path, data_path)
            
            if vector_store:
                llm = ChatGoogleGenerativeAI(
                    model=Config.MODEL_NAME,
                    google_api_key=Config.GEMINI_API_KEY,
                    temperature=0.2,
                    convert_system_message_to_human=True
                )
                retriever = vector_store.as_retriever(search_kwargs={"k": 3})
                object.__setattr__(self, '_qa_chain', RetrievalQA.from_chain_type(
                    llm=llm,
                    retriever=retriever,
                    return_source_documents=False
                ))
                print("PoliciesRAGTool initialized successfully")
            else:
                print("Warning: Policies vector store not available")
        except Exception as e:
            print(f"Error initializing PoliciesRAGTool: {str(e)}")
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        qa_chain = getattr(self, '_qa_chain', None)
        if not qa_chain:
            return "Environmental policies database is loading. Please try again in a moment."
        
        try:
            result = qa_chain.invoke({"query": query})
            if isinstance(result, dict) and "result" in result:
                output = result["result"]
                if len(output) > 50:
                    return output
                else:
                    return f"Found limited information. Please try a more specific question about EU policies.\n\nAvailable policy documents include: European Green Deal, Climate Law, Fit for 55 package, Circular Economy Action Plan, Biodiversity Strategy, Farm to Fork Strategy."
            return str(result)
        except Exception as e:
            print(f"Error in PoliciesRAGTool: {str(e)}")
            # Fallback to return known information from your documents
            if 'european union' in query.lower() or 'eu' in query.lower():
                return """Key Environmental Policies in the European Union:

1. European Green Deal (2019) - Aims to make EU climate neutral by 2050

2. European Climate Law - Makes climate neutrality legally binding

3. Fit for 55 Package - Aims to reduce EU emissions by at least 55% by 2030

4. Circular Economy Action Plan - Promotes sustainable product design

5. EU Biodiversity Strategy for 2030 - Protects nature and ecosystems

6. Farm to Fork Strategy - Promotes sustainable food systems

7. REACH Regulation - Regulates chemicals

8. Nature Restoration Law - Restores degraded ecosystems

For more details, ask specifically about any of these policies."""
            return f"Error retrieving policies: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class EffectsRAGTool(BaseTool):
    """Tool for querying environmental effects"""
    
    name: str = "Environmental_Effects_RAG"
    description: str = """
    Provides information about environmental degradation, causes, and its effects on health and ecosystems.
    Use this when asked about environmental impacts, climate change effects, pollution consequences, or health effects.
    """
    
    return_direct: bool = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, '_qa_chain', None)
        self._initialize()
    
    def _initialize(self):
        try:
            print("Initializing EffectsRAGTool...")
            manager = VectorStoreManager()
            store_path = os.path.join(Config.VECTOR_STORE_PATH, "effects_store")
            data_path = Config.EFFECTS_DIR
            
            print(f"Loading effects vector store from {store_path}")
            print(f"Data path: {data_path}")
            
            if os.path.exists(data_path):
                files = os.listdir(data_path)
                print(f"Files in effects directory: {files}")
            else:
                print(f"Effects directory not found: {data_path}")
            
            vector_store = manager.load_or_create_store(store_path, data_path)
            
            if vector_store:
                llm = ChatGoogleGenerativeAI(
                    model=Config.MODEL_NAME,
                    google_api_key=Config.GEMINI_API_KEY,
                    temperature=0.2,
                    convert_system_message_to_human=True
                )
                retriever = vector_store.as_retriever(search_kwargs={"k": 3})
                object.__setattr__(self, '_qa_chain', RetrievalQA.from_chain_type(
                    llm=llm,
                    retriever=retriever,
                    return_source_documents=False
                ))
                print("EffectsRAGTool initialized successfully")
            else:
                print("Warning: Effects vector store not available")
        except Exception as e:
            print(f"Error initializing EffectsRAGTool: {str(e)}")
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        qa_chain = getattr(self, '_qa_chain', None)
        if not qa_chain:
            return "Environmental effects database is loading. Please try again in a moment."
        
        try:
            result = qa_chain.invoke({"query": query})
            if isinstance(result, dict) and "result" in result:
                output = result["result"]
                if len(output) > 50:
                    return output
            return str(result)
        except Exception as e:
            print(f"Error in EffectsRAGTool: {str(e)}")
            return f"Error retrieving environmental effects: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)