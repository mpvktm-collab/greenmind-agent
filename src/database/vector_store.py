import os
import sys
from langchain_google_genai import GoogleGenerativeAIEmbeddings
#from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS#
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from pypdf import PdfReader

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

class VectorStoreManager:
    def __init__(self):
        """Initialize the vector store manager with embeddings"""
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
        print("VectorStoreManager initialized")
    
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
        """Create vector store from documents in directory"""
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
        
        # Create vector store
        vector_store = FAISS.from_documents(splits, self.embeddings)
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
        
        # Create new store
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