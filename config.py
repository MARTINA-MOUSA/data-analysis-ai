"""
Configuration module for the Data Analysis AI project
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class"""
    
    # Baseten API Configuration
    BASETEN_API_KEY = os.getenv("BASETEN_API_KEY", "")
    BASETEN_BASE_URL = os.getenv("BASETEN_BASE_URL", "https://inference.baseten.co/v1")
    BASETEN_MODEL = os.getenv("BASETEN_MODEL", "openai/gpt-oss-120b")
    
    # Streamlit Configuration
    STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "localhost")
    
    # LLM Configuration
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7
    TOP_P = 1.0
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if not cls.BASETEN_API_KEY:
            raise ValueError("BASETEN_API_KEY is not set in .env file")
        return True

