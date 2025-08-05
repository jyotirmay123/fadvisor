"""
LiteLLM wrapper for Google ADK with OpenRouter support
"""
import os
from typing import Optional, Dict, Any
from google.adk.models.lite_llm import LiteLlm
from litellm import completion
import litellm
from app.config import config

class OpenRouterLLM:
    """Wrapper for LiteLLM with OpenRouter configuration"""
    
    def __init__(
        self, 
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None
    ):
        self.model = model or config.DEFAULT_MODEL
        self.api_key = api_key or config.OPENROUTER_API_KEY
        
        # Set up OpenRouter configuration
        os.environ["OPENROUTER_API_KEY"] = self.api_key
        os.environ["OPENROUTER_API_BASE"] = "https://openrouter.ai/api/v1"
        
        # Configure custom headers for OpenRouter
        self.custom_headers = custom_headers or {
            "HTTP-Referer": "https://github.com/fadvisor",
            "X-Title": "FAdvisor - AI Financial Assistant"
        }
        
        # Enable debug logging in development
        if config.ENVIRONMENT == "development":
            litellm.set_verbose = True
    
    def get_adk_model(self) -> LiteLlm:
        """Get LiteLLM instance configured for Google ADK"""
        # For OpenRouter, we need to prefix the model with "openrouter/"
        model_name = self.model
        if not model_name.startswith("openrouter/"):
            model_name = f"openrouter/{model_name}"
        
        return LiteLlm(
            model=model_name,
            api_key=self.api_key,
            api_base="https://openrouter.ai/api/v1",
            custom_llm_provider="openrouter",
            extra_headers=self.custom_headers
        )
    
    def test_connection(self) -> bool:
        """Test the connection to OpenRouter"""
        try:
            response = completion(
                model=f"openrouter/{self.model}",
                messages=[{"role": "user", "content": "Hello"}],
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1",
                custom_headers=self.custom_headers,
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

# Available free models on OpenRouter
FREE_MODELS = {
    "deepseek": "deepseek/deepseek-chat",
    "mistral": "mistralai/mistral-7b-instruct",
    "llama": "meta-llama/llama-3.2-1b-instruct",
    "gemma": "google/gemma-2-9b-it",
    "phi": "microsoft/phi-3-mini-128k-instruct"
}