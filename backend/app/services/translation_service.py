"""
Google Cloud Translation service for multi-language support.
"""
import logging
from typing import Optional
from google.cloud import translate_v2 as translate
from google.cloud import translate

from app.core.config import settings
from app.models.schemas import Language

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for Google Cloud Translation API."""
    
    def __init__(self):
        """Initialize translation service."""
        try:
            self.client = translate.TranslationServiceClient()
            self.client_v2 = translate.Client()
        except Exception as e:
            logger.error(f"Failed to initialize translation client: {str(e)}")
            self.client = None
            self.client_v2 = None
    
    async def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to detect language for
            
        Returns:
            Language code (e.g., 'en', 'hi') or None if detection fails
        """
        if not self.client_v2:
            logger.warning("Translation client not available")
            return None
            
        try:
            result = self.client_v2.detect_language(text)
            return result['language']
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return None
    
    async def translate_text(
        self, 
        text: str, 
        target_language: Language,
        source_language: Optional[str] = None
    ) -> Optional[str]:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_language: Target language
            source_language: Source language (auto-detect if None)
            
        Returns:
            Translated text or None if translation fails
        """
        if not self.client:
            logger.warning("Translation client not available")
            return None
            
        try:
            # Prepare the request
            parent = f"projects/{settings.google_cloud_project}/locations/global"
            
            # Set source language
            if source_language:
                source_language_code = source_language
            else:
                # Auto-detect source language
                detected = await self.detect_language(text)
                source_language_code = detected if detected else "en"
            
            # Create translation request
            request = translate.TranslateTextRequest(
                parent=parent,
                contents=[text],
                mime_type="text/plain",
                source_language_code=source_language_code,
                target_language_code=target_language.value
            )
            
            # Perform translation
            response = self.client.translate_text(request=request)
            
            # Extract translated text
            if response.translations:
                return response.translations[0].translated_text
            
            return None
            
        except Exception as e:
            logger.error(f"Error translating text: {str(e)}")
            return None
    
    async def translate_to_english(self, text: str, source_language: Optional[str] = None) -> Optional[str]:
        """
        Translate text to English.
        
        Args:
            text: Text to translate
            source_language: Source language (auto-detect if None)
            
        Returns:
            English translation or None if translation fails
        """
        return await self.translate_text(text, Language.ENGLISH, source_language)
    
    async def translate_to_hindi(self, text: str, source_language: Optional[str] = None) -> Optional[str]:
        """
        Translate text to Hindi.
        
        Args:
            text: Text to translate
            source_language: Source language (auto-detect if None)
            
        Returns:
            Hindi translation or None if translation fails
        """
        return await self.translate_text(text, Language.HINDI, source_language)
    
    async def get_supported_languages(self) -> list:
        """
        Get list of supported languages.
        
        Returns:
            List of supported language codes
        """
        if not self.client:
            logger.warning("Translation client not available")
            return []
            
        try:
            parent = f"projects/{settings.google_cloud_project}/locations/global"
            request = translate.GetSupportedLanguagesRequest(parent=parent)
            response = self.client.get_supported_languages(request=request)
            
            languages = []
            for language in response.languages:
                languages.append({
                    "code": language.language_code,
                    "name": language.display_name,
                    "support_source": language.support_source,
                    "support_target": language.support_target
                })
            
            return languages
            
        except Exception as e:
            logger.error(f"Error getting supported languages: {str(e)}")
            return []
    
    async def batch_translate(
        self, 
        texts: list[str], 
        target_language: Language,
        source_language: Optional[str] = None
    ) -> list[Optional[str]]:
        """
        Translate multiple texts in batch.
        
        Args:
            texts: List of texts to translate
            target_language: Target language
            source_language: Source language (auto-detect if None)
            
        Returns:
            List of translated texts (None for failed translations)
        """
        if not self.client:
            logger.warning("Translation client not available")
            return [None] * len(texts)
            
        try:
            # Prepare the request
            parent = f"projects/{settings.google_cloud_project}/locations/global"
            
            # Set source language
            if source_language:
                source_language_code = source_language
            else:
                # Auto-detect source language from first text
                detected = await self.detect_language(texts[0]) if texts else "en"
                source_language_code = detected if detected else "en"
            
            # Create batch translation request
            request = translate.BatchTranslateTextRequest(
                parent=parent,
                source_language_code=source_language_code,
                target_language_codes=[target_language.value],
                input_configs=[{
                    "mime_type": "text/plain",
                    "gcs_source": {
                        "input_uri": "gs://your-bucket/input.txt"  # This would need to be configured
                    }
                }],
                output_config={
                    "gcs_destination": {
                        "output_uri_prefix": "gs://your-bucket/output/"  # This would need to be configured
                    }
                }
            )
            
            # Note: Batch translation requires files in GCS
            # For now, we'll use individual translations
            results = []
            for text in texts:
                translated = await self.translate_text(text, target_language, source_language_code)
                results.append(translated)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch translation: {str(e)}")
            return [None] * len(texts)
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language is supported for translation.
        
        Args:
            language_code: Language code to check
            
        Returns:
            True if language is supported, False otherwise
        """
        supported_codes = ["en", "hi", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"]
        return language_code.lower() in supported_codes


# Global instance
translation_service = TranslationService()
