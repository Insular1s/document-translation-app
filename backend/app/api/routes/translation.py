"""Translation API routes."""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from app.services.translation_processor import TranslationProcessor
from app.api.dependencies import get_translation_processor
from app.models.translation import (
    TranslationRequest,
    TranslationResponse,
    BatchTranslationRequest,
    BatchTranslationResponse,
    ImproveTranslationRequest,
    ImproveTranslationResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    processor: TranslationProcessor = Depends(get_translation_processor)
):
    """
    Translate text using Azure Translator with optional LLM enhancement.
    """
    try:
        result = processor.translate_text(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language,
            context=request.context,
            force_llm=request.use_llm
        )
        
        return TranslationResponse(**result)
    
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.post("/batch-translate", response_model=BatchTranslationResponse)
async def batch_translate_texts(
    request: BatchTranslationRequest,
    processor: TranslationProcessor = Depends(get_translation_processor)
):
    """
    Translate multiple texts in batch.
    """
    try:
        results = processor.batch_translate(
            texts=request.texts,
            target_language=request.target_language,
            source_language=request.source_language
        )
        
        translations = [TranslationResponse(**result) for result in results]
        
        return BatchTranslationResponse(
            success=True,
            translations=translations,
            total=len(translations)
        )
    
    except Exception as e:
        logger.error(f"Batch translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch translation failed: {str(e)}")


@router.post("/improve", response_model=ImproveTranslationResponse)
async def improve_translation(
    request: ImproveTranslationRequest,
    processor: TranslationProcessor = Depends(get_translation_processor)
):
    """
    Improve an existing translation using LLM.
    """
    try:
        result = processor.improve_translation(
            original_text=request.original_text,
            current_translation=request.current_translation,
            target_language=request.target_language,
            feedback=request.feedback
        )
        
        return ImproveTranslationResponse(**result)
    
    except Exception as e:
        logger.error(f"Translation improvement error: {e}")
        raise HTTPException(status_code=500, detail=f"Improvement failed: {str(e)}")