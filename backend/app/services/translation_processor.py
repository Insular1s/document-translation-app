from typing import Any, Dict, List, Optional
import logging
from .azure_translator import AzureTranslator
from .openrouter_service import OpenRouterService

logger = logging.getLogger(__name__)


class TranslationProcessor:
    """
    Processor that combines Azure Translator and OpenRouter for intelligent translation.
    Uses Azure for fast, standard translation and OpenRouter for context-aware enhancement.
    """
    
    def __init__(
        self,
        azure_translator: AzureTranslator,
        openrouter_service: Optional[OpenRouterService] = None,
        use_llm_enhancement: bool = False
    ):
        self.azure_translator = azure_translator
        self.openrouter_service = openrouter_service
        self.use_llm_enhancement = use_llm_enhancement and openrouter_service is not None
        logger.info(f"Translation processor initialized (LLM enhancement: {self.use_llm_enhancement})")

    def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        context: Optional[str] = None,
        force_llm: bool = False,
        llm_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Translate text using Azure Translator, optionally enhanced with LLM.
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (optional)
            context: Additional context for LLM translation
            force_llm: Force use of LLM even if enhancement is disabled
            llm_model: Specific LLM model to use (optional)
            
        Returns:
            Dictionary with translation results
        """
        if not text or not text.strip():
            return {
                'success': False,
                'error': 'Empty text provided',
                'translation': ''
            }
        
        # Always try Azure Translator first
        azure_result = self.azure_translator.translate_text(text, target_language, source_language)
        
        # If LLM enhancement is enabled or forced, use OpenRouter
        if (self.use_llm_enhancement or force_llm) and self.openrouter_service:
            detected_lang = azure_result.get('detected_language', source_language)
            llm_result = self.openrouter_service.translate_with_context(
                text=text,
                target_language=target_language,
                source_language=detected_lang,
                context=context,
                model=llm_model or self.default_llm_model
            )
            
            if llm_result.get('success'):
                return {
                    'success': True,
                    'translation': llm_result['translation'],
                    'source_language': detected_lang,
                    'target_language': target_language,
                    'method': 'llm',
                    'azure_translation': azure_result.get('translated_text')
                }
        
        # Return Azure translation
        return {
            'success': True,
            'translation': azure_result.get('translated_text', ''),
            'source_language': azure_result.get('detected_language'),
            'target_language': target_language,
            'method': 'azure'
        }

    def batch_translate(
        self,
        texts: List[str],
        target_language: str,
        source_language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Translate multiple texts efficiently.
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language code (optional)
            
        Returns:
            List of translation results
        """
        # Use Azure batch translation for efficiency
        azure_results = self.azure_translator.batch_translate(texts, target_language, source_language)
        
        translations = []
        for i, azure_result in enumerate(azure_results):
            translations.append({
                'success': True,
                'translation': azure_result.get('translated_text', ''),
                'source_language': azure_result.get('detected_language'),
                'target_language': target_language,
                'method': 'azure',
                'index': i
            })
        
        return translations

    def improve_translation(
        self,
        original_text: str,
        current_translation: str,
        target_language: str,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Improve an existing translation using LLM.
        
        Args:
            original_text: Original source text
            current_translation: Current translation to improve
            target_language: Target language code
            feedback: Specific improvement feedback
            
        Returns:
            Dictionary with improved translation
        """
        if not self.openrouter_service:
            return {
                'success': False,
                'error': 'LLM service not available',
                'translation': current_translation
            }
        
        result = self.openrouter_service.improve_translation(
            original_text=original_text,
            translated_text=current_translation,
            target_language=target_language,
            feedback=feedback
        )
        
        return result