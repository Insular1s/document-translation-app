from typing import List, Dict, Any, Optional
import requests
import logging

logger = logging.getLogger(__name__)

class AzureTranslator:
    """Class to interact with Azure Translator service for document translation."""

    def __init__(self, subscription_key: str, endpoint: str, region: str = "eastus"):
        """
        Initialize the Azure Translator service.

        Args:
            subscription_key: Azure Translator subscription key.
            endpoint: Azure Translator endpoint URL.
            region: Azure region for the translator service.
        """
        self.subscription_key = subscription_key
        self.endpoint = endpoint.rstrip('/')
        self.region = region
        logger.info(f"Azure Translator initialized for region: {region}")

    def translate_text(self, text: str, target_language: str, source_language: Optional[str] = None) -> Dict[str, Any]:
        """
        Translate text using Azure Translator.

        Args:
            text: Text to be translated.
            target_language: Target language code (e.g., 'en', 'fr').
            source_language: Source language code (optional, auto-detect if None).

        Returns:
            Dictionary containing translated text and detected language.
        """
        path = '/translate'
        params = {
            'api-version': '3.0',
            'to': target_language
        }
        
        if source_language:
            params['from'] = source_language
            
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Ocp-Apim-Subscription-Region': self.region,
            'Content-type': 'application/json'
        }
        body = [{
            'text': text
        }]

        response = requests.post(self.endpoint + path, params=params, headers=headers, json=body)
        response.raise_for_status()
        translations = response.json()

        if translations and 'translations' in translations[0]:
            translated_text = translations[0]['translations'][0]['text']
            detected_language = translations[0]['detectedLanguage']['language']
            return {
                'translated_text': translated_text,
                'detected_language': detected_language
            }
        else:
            logger.error("No translations found in response")
            return {}

    def batch_translate(self, texts: List[str], target_language: str, source_language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Translate a batch of texts using Azure Translator.

        Args:
            texts: List of texts to be translated.
            target_language: Target language code.
            source_language: Source language code (optional, auto-detect if None).

        Returns:
            List of dictionaries containing translated texts and detected languages.
        """
        path = '/translate'
        params = {
            'api-version': '3.0',
            'to': target_language
        }
        
        if source_language:
            params['from'] = source_language
            
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Ocp-Apim-Subscription-Region': self.region,
            'Content-type': 'application/json'
        }
        body = [{'text': text} for text in texts]

        response = requests.post(self.endpoint + path, params=params, headers=headers, json=body)
        response.raise_for_status()
        translations = response.json()

        results = []
        for translation in translations:
            if 'translations' in translation:
                translated_text = translation['translations'][0]['text']
                detected_language = translation['detectedLanguage']['language']
                results.append({
                    'translated_text': translated_text,
                    'detected_language': detected_language
                })
            else:
                logger.error("No translations found in response for one of the texts")
                results.append({})

        return results
