import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the document translation application."""
    
    # Azure Translator settings
    AZURE_TRANSLATOR_ENDPOINT: str = os.getenv("AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com/")
    AZURE_TRANSLATOR_KEY: str = os.getenv("AZURE_TRANSLATOR_KEY", "")  # REMOVED hardcoded key
    AZURE_TRANSLATOR_REGION: str = os.getenv("AZURE_TRANSLATOR_REGION", "japaneast")
    
    # Azure Computer Vision settings (for OCR)
    AZURE_VISION_ENDPOINT: str = os.getenv("AZURE_VISION_ENDPOINT", "")
    AZURE_VISION_KEY: str = os.getenv("AZURE_VISION_KEY", "")
    
    # OpenRouter settings
    OPENROUTER_API_URL: str = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")  # REMOVED hardcoded key
    
    # Application settings
    APP_NAME: str = "Document Translation App"
    APP_VERSION: str = "1.0.0"
    
    # File upload settings
    UPLOAD_FOLDER: Path = Path("uploads")
    OUTPUT_FOLDER: Path = Path("outputs")
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100 MB
    ALLOWED_EXTENSIONS: set = {'.pptx'}
    
    # Translation settings
    SUPPORTED_LANGUAGES: list = ["en", "id", "ja", "fr", "de", "es", "zh", "ko"]
    DEFAULT_LLM_MODEL: str = "anthropic/claude-3.5-sonnet"
    USE_LLM_ENHANCEMENT: bool = os.getenv("USE_LLM_ENHANCEMENT", "true").lower() == "true"
    TRANSLATE_IMAGES: bool = os.getenv("TRANSLATE_IMAGES", "true").lower() == "true"  # Enable/disable image translation
    TRANSLATION_RETRY_ATTEMPTS: int = int(os.getenv("TRANSLATION_RETRY_ATTEMPTS", "3"))  # Number of retry attempts for failed translations
    TRANSLATION_RETRY_DELAY: float = float(os.getenv("TRANSLATION_RETRY_DELAY", "1.0"))  # Initial retry delay in seconds
    
    # Available LLM models for translation
    AVAILABLE_LLM_MODELS: dict = {
        "anthropic/claude-3.5-sonnet": "Claude 3.5 Sonnet (Best Quality)",
        "openai/gpt-4-turbo": "GPT-4 Turbo (Fast & Accurate)",
        "google/gemini-pro-1.5": "Gemini Pro 1.5 (Balanced)",
        "meta-llama/llama-3.1-70b-instruct": "Llama 3.1 70B (Open Source)"
    }
    
    # CORS settings - will be updated with actual frontend URL in production
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://document-translation-app-db8x.vercel.app"
    ]
    
    # Add frontend URL from environment if provided
    if os.getenv("FRONTEND_URL"):
        CORS_ORIGINS.append(os.getenv("FRONTEND_URL"))

    @staticmethod
    def get_supported_languages():
        return Config.SUPPORTED_LANGUAGES
    
    @staticmethod
    def ensure_directories():
        """Ensure upload and output directories exist."""
        Config.UPLOAD_FOLDER.mkdir(exist_ok=True)
        Config.OUTPUT_FOLDER.mkdir(exist_ok=True)

# Create a settings instance
settings = Config()