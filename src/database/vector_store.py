# src/database/vector_store.py
import os
import sys
import pickle
import hashlib
from pathlib import Path
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from pypdf import PdfReader

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

class VectorStoreManager:
    def __init__(self):
        """Initialize the vector store manager with embeddings and caching"""
        print("Initializing VectorStoreManager...")
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            google_api_key=Config.GEMINI_API_KEY
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Setup cache directory
        self.cache_dir = Path("./embedding_cache")
        self.cache_dir.mkdir(exist_ok=True)
        print(f"Embedding cache directory: {self.cache_dir}")
        print("VectorStoreManager initialized")
    
    def _get_content_hash(self, content: str) -> str:
        """Generate a hash of content for cache key"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _get_cached_embedding(self, content_hash: str):
        """Retrieve cached embedding if exists"""
        cache_file = self.cache_dir / f"{content_hash}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading cache: {e}")
        return None
    
    def _cache_embedding(self, content_hash: str, embedding):
        """Save embedding to cache"""
        cache_file = self.cache_dir / f"{content_hash}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)
        except Exception as e:
            print(f"Error saving to cache: {e}")
    
    def embed_with_cache(self, texts):
        """Embed texts with caching to avoid API quota issues"""
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache for each text
        for i, text in enumerate(texts):
            content_hash = self._get_content_hash(text)
            cached = self._get_cached_embedding(content_hash)
            if cached is not None:
                embeddings.append((i, cached))
            else:
                uncached_texts.append(text)
                uncached_indices.append((i, content_hash))
        
        print(f"Cache hit: {len(embeddings)} texts, Cache miss: {len(uncached_texts)} texts")
        
        # Embed uncached texts in batches to minimize API calls
        if uncached_texts:
            try:
                # Embed in batches of 10 to stay within rate limits
                batch_size = 10
                for j in range(0, len(uncached_texts), batch_size):
                    batch = uncached_texts[j:j+batch_size]
                    batch_indices = uncached_indices[j:j+batch_size]
                    
                    print(f"Embedding batch {j//batch_size + 1} ({len(batch)} texts)...")
                    batch_embeddings = self.embeddings.embed_documents(batch)
                    
                    # Cache results
                    for (idx, content_hash), emb in zip(batch_indices, batch_embeddings):
                        self._cache_embedding(content_hash, emb)
                        embeddings.append((idx, emb))
                        
            except Exception as e:
                print(f"Error during embedding: {e}")
                # If we hit quota limits, try to use any cached embeddings we have
                if "quota" in str(e).lower():
                    print("Quota limit reached! Using only cached embeddings.")
                    # Return only what we have from cache
                    return [emb for _, emb in sorted(embeddings)]
                raise e
        
        # Return in original order
        return [emb for _, emb in sorted(embeddings)]
    
    def read_text_file(self, file_path):
        """Read a text file and return its content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return text
        except Exception as e:
            print(f"Error reading text file {file_path}: {str(e)}")
            return None
    
    def read_pdf_file(self, file_path):
        """Read a PDF file and return its content"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        except Exception as e:
            print(f"Error reading PDF file {file_path}: {str(e)}")
            return None
    
    def load_documents_from_directory(self, directory_path):
        """Load all text and PDF files from a directory manually"""
        documents = []
        
        if not os.path.exists(directory_path):
            print(f"Directory not found: {directory_path}")
            return documents
        
        # Walk through all files in directory
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Handle text files
                if file.endswith('.txt'):
                    print(f"Reading text file: {file}")
                    content = self.read_text_file(file_path)
                    if content:
                        doc = Document(
                            page_content=content,
                            metadata={"source": file_path, "filename": file, "type": "text"}
                        )
                        documents.append(doc)
                
                # Handle PDF files
                elif file.endswith('.pdf'):
                    print(f"Reading PDF file: {file}")
                    content = self.read_pdf_file(file_path)
                    if content:
                        doc = Document(
                            page_content=content,
                            metadata={"source": file_path, "filename": file, "type": "pdf"}
                        )
                        documents.append(doc)
        
        return documents
    
    def create_vector_store(self, directory_path, store_name):
        """Create vector store from documents in directory with caching"""
        print(f"Creating vector store from {directory_path}...")
        
        # Load documents
        documents = self.load_documents_from_directory(directory_path)
        print(f"Loaded {len(documents)} documents")
        
        if not documents:
            print("No documents found")
            return None
        
        # Split documents
        splits = self.text_splitter.split_documents(documents)
        print(f"Created {len(splits)} text chunks")
        
        # Extract texts for embedding
        texts = [doc.page_content for doc in splits]
        metadatas = [doc.metadata for doc in splits]
        
        # Use cached embedding method
        print("Generating embeddings with caching...")
        embeddings = self.embed_with_cache(texts)
        
        # Create vector store
        vector_store = FAISS.from_embeddings(
            text_embeddings=list(zip(texts, embeddings)),
            embedding=self.embeddings,
            metadatas=metadatas
        )
        print("Vector store created successfully")
        
        return vector_store
    
    def load_or_create_store(self, store_path, data_path):
        """Load existing vector store or create new one"""
        print(f"\nChecking for vector store at: {store_path}")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(store_path), exist_ok=True)
        
        # Try to load existing store
        if os.path.exists(store_path):
            try:
                print("Found existing vector store. Loading...")
                # Try with allow_dangerous_deserialization for newer FAISS versions
                try:
                    vector_store = FAISS.load_local(store_path, self.embeddings, allow_dangerous_deserialization=True)
                except TypeError:
                    # If that fails, try without it for older FAISS versions
                    vector_store = FAISS.load_local(store_path, self.embeddings)
                print("Vector store loaded successfully")
                return vector_store
            except Exception as e:
                print(f"Error loading existing store: {str(e)}")
                print("Will create new store instead...")
        
        # Create new store with caching
        print("Creating new vector store...")
        vector_store = self.create_vector_store(data_path, store_path)
        
        if vector_store:
            # Save the store
            print(f"Saving vector store to {store_path}...")
            vector_store.save_local(store_path)
            print("Vector store saved")
        
        return vector_store
    
    def get_retriever(self, vector_store, k=3):
        """Get a retriever from vector store"""
        if vector_store:
            return vector_store.as_retriever(
                search_kwargs={"k": k}
            )
        return None