"""
Configuration module for the Data Analysis AI project
"""
import os
from dotenv import load_dotenv
from back.exceptions import ConfigurationError

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class"""
    
    # Environment
    ENV = os.getenv("ENV", "development")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Baseten API Configuration
    BASETEN_API_KEY = os.getenv("BASETEN_API_KEY", "")
    BASETEN_BASE_URL = os.getenv("BASETEN_BASE_URL", "https://inference.baseten.co/v1")
    BASETEN_MODEL = os.getenv("BASETEN_MODEL", "openai/gpt-oss-120b")
    BASETEN_TIMEOUT = int(os.getenv("BASETEN_TIMEOUT", "60"))
    BASETEN_MAX_RETRIES = int(os.getenv("BASETEN_MAX_RETRIES", "3"))
    
    # Streamlit Configuration
    STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")
    STREAMLIT_SERVER_MAX_UPLOAD_SIZE = int(os.getenv("STREAMLIT_MAX_UPLOAD_SIZE", "200"))  # MB
    
    # LLM Configuration
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    TOP_P = float(os.getenv("TOP_P", "1.0"))
    
    # Data Processing Configuration
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
    MAX_ROWS_PREVIEW = int(os.getenv("MAX_ROWS_PREVIEW", "10000"))
    
    # Security
    ALLOWED_FILE_EXTENSIONS = ['.csv']
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    
    # Performance
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # seconds
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "True").lower() == "true"
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if not cls.BASETEN_API_KEY:
            raise ConfigurationError("BASETEN_API_KEY is not set in .env file")
        if cls.ENV == "production" and cls.DEBUG:
            raise ConfigurationError("DEBUG cannot be True in production environment")
        return True
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production"""
        return cls.ENV == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development"""
        return cls.ENV == "development"

