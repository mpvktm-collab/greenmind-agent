import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found")
    
    # CORRECTED MODEL NAMES
    MODEL_NAME = "gemini-1.5-pro"  # Changed from gemini-1.5-flash
    EMBEDDING_MODEL = "models/gemini-embedding-001"
    TEMPERATURE = 0.7
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    VECTOR_STORE_PATH = os.path.join(BASE_DIR, "vector_store")
    LOG_DIRECTORY = os.path.join(BASE_DIR, "logs")
    DATA_DIRECTORY = os.path.join(BASE_DIR, "src", "data")
    POLICIES_DIR = os.path.join(DATA_DIRECTORY, "policies")
    EFFECTS_DIR = os.path.join(DATA_DIRECTORY, "effects")
    
    # Create directories
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    os.makedirs(LOG_DIRECTORY, exist_ok=True)
    os.makedirs(POLICIES_DIR, exist_ok=True)
    os.makedirs(EFFECTS_DIR, exist_ok=True)
    
    AGENT_PERSONALITY = """
    You are GreenMind, an enthusiastic and knowledgeable environmental sustainability advisor.
    """