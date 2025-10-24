from typing import Any, Dict, List, Optional
import logging
import time
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
        use_llm_enhancement: bool = False,
        default_llm_model: Optional[str] = None
    ):
        self.azure_translator = azure_translator
        self.openrouter_service = openrouter_service
        self.use_llm_enhancement = use_llm_enhancement and openrouter_service is not None
        self.default_llm_model = default_llm_model or "anthropic/claude-3.5-sonnet"
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
        
        # Try translation with retry logic
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                # Always try Azure Translator first (also does language detection)
                azure_result = self.azure_translator.translate_text(text, target_language, source_language)
                
                # Check if source and target languages are the same
                detected_lang = azure_result.get('detected_language', source_language)
                if detected_lang and self._normalize_language_code(detected_lang) == self._normalize_language_code(target_language):
                    logger.debug(f"Skipping translation: text is already in target language '{target_language}'")
                    return {
                        'success': True,
                        'translation': text,  # Return original text unchanged
                        'source_language': detected_lang,
                        'target_language': target_language,
                        'method': 'skipped',
                        'skipped': True
                    }
                
                # If LLM enhancement is enabled or forced, use OpenRouter
                if (self.use_llm_enhancement or force_llm) and self.openrouter_service:
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
                
            except Exception as e:
                logger.warning(f"Translation attempt {attempt + 1}/{max_retries} failed: {e}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    sleep_time = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    # Final attempt failed
                    logger.error(f"Translation failed after {max_retries} attempts: {e}")
                    return {
                        'success': False,
                        'error': str(e),
                        'translation': text,  # Return original text as fallback
                        'source_language': source_language,
                        'target_language': target_language,
                        'method': 'failed'
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
    
    def _normalize_language_code(self, lang_code: str) -> str:
        """
        Normalize language code for comparison.
        
        Args:
            lang_code: Language code to normalize
            
        Returns:
            Normalized language code (lowercase, base language only)
        """
        if not lang_code:
            return ''
        
        # Convert to lowercase
        lang = lang_code.lower().strip()
        
        # Handle language variants (zh-Hans -> zh, pt-BR -> pt, etc.)
        if '-' in lang:
            lang = lang.split('-')[0]
        
        # Handle underscores (zh_Hans -> zh)
        if '_' in lang:
            lang = lang.split('_')[0]
        
        # Map common aliases
        lang_map = {
            'in': 'id',  # Indonesian: 'in' (old) -> 'id' (ISO 639-1)
            'iw': 'he',  # Hebrew: 'iw' (old) -> 'he'
            'ji': 'yi',  # Yiddish: 'ji' (old) -> 'yi'
        }
        
        return lang_map.get(lang, lang)