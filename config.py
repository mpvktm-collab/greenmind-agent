import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in .env file. Please add it.")
    
    # Model names - UPDATED with correct embedding model
    MODEL_NAME = "gemini-1.5-flash"
    EMBEDDING_MODEL = "models/gemini-embedding-001"  # Changed from text-embedding-004
    TEMPERATURE = 0.7
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    VECTOR_STORE_PATH = os.path.join(BASE_DIR, "vector_store")
    LOG_DIRECTORY = os.path.join(BASE_DIR, "logs")
    DATA_DIRECTORY = os.path.join(BASE_DIR, "src", "data")
    
    # Add these missing lines
    POLICIES_DIR = os.path.join(DATA_DIRECTORY, "policies")
    EFFECTS_DIR = os.path.join(DATA_DIRECTORY, "effects")
    
    # Create directories if they don't exist
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    os.makedirs(LOG_DIRECTORY, exist_ok=True)
    os.makedirs(POLICIES_DIR, exist_ok=True)
    os.makedirs(EFFECTS_DIR, exist_ok=True)
    
    # Agent Character
    AGENT_PERSONALITY = """
    You are GreenMind, an enthusiastic and knowledgeable environmental sustainability advisor. 
    You're passionate about protecting our planet and always respond with hope and practical wisdom.
    You believe every small action counts towards a greener future.
    You incorporate environmental quotes and optimistic perspectives in your greetings.
    You only answer queries related to environmental policies, effects, pollution indices, and sustainability.
    If asked about unrelated topics, politely redirect the conversation to environmental topics.
    """