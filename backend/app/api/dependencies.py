"""Dependency injection for services."""
from functools import lru_cache
from app.config import settings
from app.services.azure_translator import AzureTranslator
from app.services.openrouter_service import OpenRouterService
from app.services.translation_processor import TranslationProcessor
from app.services.image_translator import ImageTranslator
from app.services.document_processor import DocumentProcessor


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


@lru_cache()
def get_image_translator() -> ImageTranslator:
    """Get Image Translator instance."""
    if not settings.AZURE_VISION_KEY or not settings.AZURE_VISION_ENDPOINT:
        return None
    return ImageTranslator(
        vision_endpoint=settings.AZURE_VISION_ENDPOINT,
        vision_key=settings.AZURE_VISION_KEY
    )


@lru_cache()
def get_document_processor() -> DocumentProcessor:
    """Get Document Processor instance."""
    image_translator = get_image_translator() if settings.TRANSLATE_IMAGES else None
    return DocumentProcessor(
        translation_processor=get_translation_processor(),
        image_translator=image_translator
    )