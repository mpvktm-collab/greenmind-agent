import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Validate ONLY when explicitly called (not at import time)
    @staticmethod
    def validate():
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found. Set it in environment variables.")

    # Model config
    #MODEL_NAME = "gemini-1.5-pro" 
    MODEL_NAME = "gemini-2.5-flash"
    EMBEDDING_MODEL = "models/gemini-embedding-001"
    TEMPERATURE = 0.7

    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    VECTOR_STORE_PATH = os.path.join(BASE_DIR, "vector_store")
    LOG_DIRECTORY = os.path.join(BASE_DIR, "logs")
    DATA_DIRECTORY = os.path.join(BASE_DIR, "src", "data")
    POLICIES_DIR = os.path.join(DATA_DIRECTORY, "policies")
    EFFECTS_DIR = os.path.join(DATA_DIRECTORY, "effects")

    # Safe directory setup (call this manually)
    @staticmethod
    def setup_directories():
        os.makedirs(Config.VECTOR_STORE_PATH, exist_ok=True)
        os.makedirs(Config.LOG_DIRECTORY, exist_ok=True)
        os.makedirs(Config.POLICIES_DIR, exist_ok=True)
        os.makedirs(Config.EFFECTS_DIR, exist_ok=True)