"""
Configuration settings for FAdvisor
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # LiteLLM/OpenRouter settings
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "deepseek/deepseek-chat")
    
    # Google Cloud settings (optional)
    GOOGLE_CLOUD_PROJECT: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    # Financial API keys
    ALPHA_VANTAGE_API_KEY: Optional[str] = os.getenv("ALPHA_VANTAGE_API_KEY")
    FINNHUB_API_KEY: Optional[str] = os.getenv("FINNHUB_API_KEY")
    NEWS_API_KEY: Optional[str] = os.getenv("NEWS_API_KEY")
    
    # Application settings
    APP_NAME: str = os.getenv("APP_NAME", "fadvisor")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Agent settings
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "5"))
    CONCURRENT_REQUESTS: int = int(os.getenv("CONCURRENT_REQUESTS", "3"))
    
    # Financial analysis settings
    TECHNICAL_INDICATORS = [
        "RSI", "MACD", "BB", "EMA", "SMA", 
        "Volume", "ATR", "Stochastic"
    ]
    
    FUNDAMENTAL_METRICS = [
        "PE", "PB", "PS", "DividendYield", 
        "MarketCap", "Revenue", "EPS", "ROE"
    ]
    
    # Time periods for analysis
    ANALYSIS_PERIODS = {
        "short": 30,    # 30 days
        "medium": 90,   # 90 days
        "long": 365     # 1 year
    }
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is required in environment variables")
        return True

config = Config()