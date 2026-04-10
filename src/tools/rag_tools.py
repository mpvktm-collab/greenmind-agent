from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import BaseTool
from typing import Optional
from langchain.callbacks.manager import CallbackManagerForToolRun
import sys
import os

# Ensure root path is available
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import Config
from src.database.vector_store import VectorStoreManager


# =========================================================
# BASE CLASS (shared logic for both tools)
# =========================================================

class BaseRAGTool(BaseTool):
    return_direct: bool = True

    def __init__(self, store_name: str, data_path: str, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, "_qa_chain", None)
        object.__setattr__(self, "_store_name", store_name)
        object.__setattr__(self, "_data_path", data_path)

    def _initialize(self):
        """Initialize vector store + LLM safely"""
        try:
            print(f"Initializing {self.name}...")

            manager = VectorStoreManager()
            store_path = os.path.join(Config.VECTOR_STORE_PATH, self._store_name)

            # Load or create vector store
            vector_store = manager.load_or_create_store(store_path, self._data_path)

            if not vector_store:
                print(f"Warning: Vector store not available for {self.name}")
                return

            # Initialize LLM
            llm = ChatGoogleGenerativeAI(
                model=Config.MODEL_NAME,
                google_api_key=Config.GEMINI_API_KEY,
                temperature=0.1,
                convert_system_message_to_human=True
            )

            retriever = vector_store.as_retriever(search_kwargs={"k": 3})

            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                retriever=retriever,
                return_source_documents=False
            )

            object.__setattr__(self, "_qa_chain", qa_chain)
            print(f"{self.name} initialized successfully")

        except Exception as e:
            print(f"Error initializing {self.name}: {str(e)}")
            object.__setattr__(self, "_qa_chain", None)

    def _ensure_initialized(self):
        """Lazy initialization (critical for Render)"""
        if getattr(self, "_qa_chain", None) is None:
            self._initialize()

    def _run_query(self, query: str) -> str:
        """Shared query execution logic"""
        self._ensure_initialized()

        qa_chain = getattr(self, "_qa_chain", None)
        if not qa_chain:
            return f"{self.name} is still loading. Please try again shortly."

        try:
            result = qa_chain.invoke({"query": query})

            # Handle dict response
            if isinstance(result, dict) and "result" in result:
                output = result["result"]
            else:
                output = str(result)

            # Filter weak responses
            if len(output.strip()) < 50:
                return "No relevant information found. Please refine your query."

            return output

        except Exception as e:
            error_msg = str(e)

            if "429" in error_msg:
                return "API quota exceeded. Please try again in a few minutes."
            elif "404" in error_msg:
                return "Requested information not found. Try a different query."
            elif "connection" in error_msg.lower():
                return "Connection issue. Please try again."
            else:
                return f"Error processing request: {error_msg}"

    async def _arun(self, query: str) -> str:
        return self._run(query)


# =========================================================
# POLICIES TOOL
# =========================================================

class PoliciesRAGTool(BaseRAGTool):
    """Environmental policies, laws, and regulations"""

    name: str = "Environmental_Policies_RAG"
    description: str = (
        "Retrieves information about environmental policies, laws, and regulations. "
        "Use for queries about acts, treaties, regulations, and government initiatives."
    )

    def __init__(self, **kwargs):
        super().__init__(
            store_name="policies_store",
            data_path=Config.POLICIES_DIR,
            **kwargs
        )

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        return self._run_query(query)


# =========================================================
# EFFECTS TOOL
# =========================================================

class EffectsRAGTool(BaseRAGTool):
    """Environmental effects, climate change, health impacts"""

    name: str = "Environmental_Effects_RAG"
    description: str = (
        "Provides information about environmental impacts, climate change, "
        "pollution effects, and health consequences."
    )

    def __init__(self, **kwargs):
        super().__init__(
            store_name="effects_store",
            data_path=Config.EFFECTS_DIR,
            **kwargs
        )

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        return self._run_query(query)