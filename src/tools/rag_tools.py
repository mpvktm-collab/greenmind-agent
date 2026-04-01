# src/tools/rag_tools.py
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from src.database.vector_store import VectorStoreManager


class PoliciesRAGTool:

    def __init__(self):

        manager = VectorStoreManager(
            data_path="src/data/policies",
            store_path="vector_store/policies_store"
        )

        vector_store = manager.load_or_create()

        retriever = vector_store.as_retriever()

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.2
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever
        )

    def run(self, query):

        return self.qa_chain.run(query)


class EffectsRAGTool:

    def __init__(self):

        manager = VectorStoreManager(
            data_path="src/data/effects",
            store_path="vector_store/effects_store"
        )

        vector_store = manager.load_or_create()

        retriever = vector_store.as_retriever()

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.2
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever
        )

    def run(self, query):

        return self.qa_chain.run(query)