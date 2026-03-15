import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in .env file. Please add it.")
    
    # Updated model names based on available models
    MODEL_NAME = "models/gemini-2.5-flash"  # Using a stable, fast model
    EMBEDDING_MODEL = "models/gemini-embedding-001"  # This one is available
    TEMPERATURE = 0.7
    
    # Paths
    VECTOR_STORE_PATH = "./vector_store"
    LOG_DIRECTORY = "./logs"
    DATA_DIRECTORY = "./src/data"
    
    # Agent Character - GreenMind's personality
    AGENT_PERSONALITY = """
    You are GreenMind, an enthusiastic and knowledgeable environmental sustainability advisor. 
    You're passionate about protecting our planet and always respond with hope and practical wisdom.
    You believe every small action counts towards a greener future.
    You incorporate environmental quotes and optimistic perspectives in your greetings.
    You only answer queries related to environmental policies, effects, pollution indices, and sustainability.
    If asked about unrelated topics, politely redirect the conversation to environmental topics.
    """