from typing import Any, Dict, Optional
import requests
import logging

logger = logging.getLogger(__name__)

class OpenRouterService:
    """Service to interact with OpenRouter for LLM-enhanced translation capabilities."""
    
    def __init__(self, api_key: str, api_url: str = "https://openrouter.ai/api/v1/chat/completions"):
        """
        Initialize the OpenRouter service.
        
        Args:
            api_key: API key for authenticating with OpenRouter.
            api_url: API URL for the OpenRouter chat completions endpoint.
        """
        self.api_key = api_key
        self.api_url = api_url
        logger.info("OpenRouter service initialized")

    def translate_with_context(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        context: Optional[str] = None,
        model: str = "anthropic/claude-3.5-sonnet"
    ) -> Dict[str, Any]:
        """
        Translate text using LLM with context awareness for better quality.
        
        Args:
            text: Text to be translated.
            target_language: Target language code (e.g., 'en', 'id', 'ja').
            source_language: Source language code (optional).
            context: Additional context for better translation.
            model: LLM model to use for translation.
        
        Returns:
            Dictionary with translation result.
        """
        # Build prompt
        lang_names = {
            'en': 'English',
            'id': 'Indonesian',
            'ja': 'Japanese',
            'fr': 'French',
            'de': 'German',
            'es': 'Spanish',
            'zh': 'Chinese',
            'ko': 'Korean'
        }
        
        target_lang_name = lang_names.get(target_language, target_language)
        source_info = f" from {lang_names.get(source_language, source_language)}" if source_language else ""
        
        prompt = f"""Translate the following text{source_info} to {target_lang_name}.

Instructions:
- Preserve proper nouns, brand names, and company names
- Keep technical terms accurate
- Maintain the original formatting and structure
- Preserve URLs, emails, and numbers
- Use natural, fluent language in the target language
"""
        
        if context:
            prompt += f"\nContext: {context}\n"
        
        prompt += f"\nText to translate:\n{text}\n\nProvide only the translated text without explanations."
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://document-translation-app.com',
            'X-Title': 'Document Translation App'
        }
        
        payload = {
            'model': model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.3,
            'max_tokens': 2000
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract translation
            if 'choices' in result and len(result['choices']) > 0:
                translation = result['choices'][0]['message']['content'].strip()
                
                return {
                    'success': True,
                    'translation': translation,
                    'model': model,
                    'target_language': target_language
                }
            
            return {
                'success': False,
                'error': 'No translation returned',
                'translation': None
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'translation': None
            }

    def improve_translation(
        self,
        original_text: str,
        translated_text: str,
        target_language: str,
        feedback: Optional[str] = None,
        model: str = "anthropic/claude-3.5-sonnet"
    ) -> Dict[str, Any]:
        """
        Improve or refine an existing translation based on feedback.
        
        Args:
            original_text: Original source text.
            translated_text: Current translation to improve.
            target_language: Target language code.
            feedback: Specific feedback or instructions for improvement.
            model: LLM model to use.
        
        Returns:
            Dictionary with improved translation.
        """
        lang_names = {
            'en': 'English',
            'id': 'Indonesian',
            'ja': 'Japanese',
            'fr': 'French',
            'de': 'German',
            'es': 'Spanish',
            'zh': 'Chinese',
            'ko': 'Korean'
        }
        
        target_lang_name = lang_names.get(target_language, target_language)
        
        prompt = f"""Review and improve the following {target_lang_name} translation.

Original text:
{original_text}

Current translation:
{translated_text}
"""
        
        if feedback:
            prompt += f"\nFeedback/Instructions:\n{feedback}\n"
        
        prompt += "\nProvide only the improved translation without explanations."
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://document-translation-app.com',
            'X-Title': 'Document Translation App'
        }
        
        payload = {
            'model': model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.3,
            'max_tokens': 2000
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                improved_translation = result['choices'][0]['message']['content'].strip()
                
                return {
                    'success': True,
                    'translation': improved_translation,
                    'model': model
                }
            
            return {
                'success': False,
                'error': 'No improved translation returned',
                'translation': None
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'translation': None
            }