from pydantic import BaseModel, Field
from typing import Optional, List


class TranslationRequest(BaseModel):
    """Request model for text translation."""
    text: str = Field(..., description="Text to translate")
    target_language: str = Field(..., description="Target language code (e.g., 'en', 'id', 'ja')")
    source_language: Optional[str] = Field(None, description="Source language code (auto-detect if not provided)")
    context: Optional[str] = Field(None, description="Additional context for better translation")
    use_llm: bool = Field(False, description="Force use of LLM for translation")


class TranslationResponse(BaseModel):
    """Response model for translation."""
    success: bool = Field(..., description="Whether translation was successful")
    translation: str = Field(..., description="Translated text")
    source_language: Optional[str] = Field(None, description="Detected or provided source language")
    target_language: str = Field(..., description="Target language")
    method: str = Field(..., description="Translation method used (azure/llm)")
    error: Optional[str] = Field(None, description="Error message if translation failed")


class BatchTranslationRequest(BaseModel):
    """Request model for batch translation."""
    texts: List[str] = Field(..., description="List of texts to translate")
    target_language: str = Field(..., description="Target language code")
    source_language: Optional[str] = Field(None, description="Source language code")


class BatchTranslationResponse(BaseModel):
    """Response model for batch translation."""
    success: bool = Field(..., description="Whether batch translation was successful")
    translations: List[TranslationResponse] = Field(..., description="List of translation results")
    total: int = Field(..., description="Total number of translations")


class ImproveTranslationRequest(BaseModel):
    """Request model for improving translations."""
    original_text: str = Field(..., description="Original source text")
    current_translation: str = Field(..., description="Current translation to improve")
    target_language: str = Field(..., description="Target language code")
    feedback: Optional[str] = Field(None, description="Specific feedback for improvement")


class ImproveTranslationResponse(BaseModel):
    """Response model for improved translation."""
    success: bool = Field(..., description="Whether improvement was successful")
    translation: str = Field(..., description="Improved translation")
    model: Optional[str] = Field(None, description="Model used for improvement")
    error: Optional[str] = Field(None, description="Error message if improvement failed")