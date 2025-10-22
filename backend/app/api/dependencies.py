"""Dependency injection for services."""
from functools import lru_cache
from app.config import settings
from app.services.azure_translator import AzureTranslator
from app.services.openrouter_service import OpenRouterService
from app.services.translation_processor import TranslationProcessor


@lru_cache()
def get_azure_translator() -> AzureTranslator:
    """Get Azure Translator service instance."""
    return AzureTranslator(
        subscription_key=settings.AZURE_TRANSLATOR_KEY,
        endpoint=settings.AZURE_TRANSLATOR_ENDPOINT,
        region=settings.AZURE_TRANSLATOR_REGION
    )


@lru_cache()
def get_openrouter_service() -> OpenRouterService:
    """Get OpenRouter service instance."""
    if not settings.OPENROUTER_API_KEY:
        return None
    return OpenRouterService(
        api_key=settings.OPENROUTER_API_KEY,
        api_url=settings.OPENROUTER_API_URL
    )


@lru_cache()
def get_translation_processor() -> TranslationProcessor:
    """Get Translation Processor instance."""
    return TranslationProcessor(
        azure_translator=get_azure_translator(),
        openrouter_service=get_openrouter_service(),
        use_llm_enhancement=settings.USE_LLM_ENHANCEMENT,
        default_llm_model=settings.DEFAULT_LLM_MODEL
    )