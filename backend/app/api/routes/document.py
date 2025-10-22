"""Document upload and translation API routes."""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import FileResponse
from pathlib import Path
import logging
import shutil
from typing import Optional

from app.config import settings
from app.services.document_processor import DocumentProcessor
from app.services.translation_processor import TranslationProcessor
from app.api.dependencies import get_translation_processor
from app.models.document import (
    DocumentUploadResponse,
    DocumentTranslationRequest,
    DocumentTranslationResponse
)
from app.utils.file_handler import (
    is_supported_file_type,
    get_file_size,
    ensure_directory_exists,
    generate_unique_filename
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Ensure directories exist
settings.ensure_directories()


@router.get("/models")
async def get_available_models():
    """
    Get available LLM models for translation.
    
    Returns:
        Dictionary with available models
    """
    return {
        "models": settings.AVAILABLE_LLM_MODELS,
        "default": settings.DEFAULT_LLM_MODEL
    }


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PPTX document for translation.
    
    Args:
        file: PPTX file to upload
        
    Returns:
        Upload confirmation with file details
    """
    try:
        # Validate file extension
        if not file.filename.endswith('.pptx'):
            raise HTTPException(
                status_code=400,
                detail="Only PPTX files are supported"
            )
        
        # Check file size
        file_path = settings.UPLOAD_FOLDER / file.filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            
            # Check size
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
                )
            
            buffer.write(content)
        
        file_size = get_file_size(str(file_path))
        
        logger.info(f"File uploaded: {file.filename} ({file_size} bytes)")
        
        return DocumentUploadResponse(
            success=True,
            filename=file.filename,
            file_path=str(file_path),
            file_size=file_size
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/translate", response_model=DocumentTranslationResponse)
async def translate_document(
    file: UploadFile = File(...),
    target_language: str = Form(...),
    source_language: Optional[str] = Form(None),
    use_llm: bool = Form(False),
    llm_model: Optional[str] = Form(None),
    preserve_formatting: bool = Form(True),
    processor: TranslationProcessor = Depends(get_translation_processor)
):
    """
    Translate a PPTX document (upload and translate in one step).
    
    Args:
        file: PPTX file to translate
        target_language: Target language code
        source_language: Source language code (optional)
        use_llm: Whether to use LLM enhancement
        llm_model: LLM model to use (optional, defaults to Claude 3.5 Sonnet)
        preserve_formatting: Whether to preserve formatting
        processor: Translation processor instance
        
    Returns:
        Translation result with output file details
    """
    try:
        # Validate file extension
        if not file.filename.endswith('.pptx'):
            raise HTTPException(
                status_code=400,
                detail="Only PPTX files are supported"
            )
        
        # Save uploaded file
        input_path = settings.UPLOAD_FOLDER / file.filename
        with open(input_path, "wb") as buffer:
            content = await file.read()
            
            # Check size
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
                )
            
            buffer.write(content)
        
        logger.info(f"File uploaded for translation: {file.filename}")
        
        # Generate output filename
        output_filename = generate_unique_filename(file.filename, target_language)
        output_path = settings.OUTPUT_FOLDER / output_filename
        
        # Create document processor
        doc_processor = DocumentProcessor(processor)
        
        # Process document
        result = doc_processor.process_pptx(
            input_path=input_path,
            output_path=output_path,
            target_language=target_language,
            source_language=source_language,
            use_llm=use_llm,
            llm_model=llm_model,
            preserve_formatting=preserve_formatting
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Translation failed')
            )
        
        logger.info(f"Document translated: {file.filename} -> {output_filename}")
        
        return DocumentTranslationResponse(
            success=True,
            filename=file.filename,
            output_filename=output_filename,
            slides_translated=result.get('slides_processed', 0),
            text_frames_translated=result.get('text_frames_translated', 0),
            target_language=target_language,
            use_llm=use_llm,
            llm_model=llm_model
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@router.get("/download/{filename}")
async def download_document(filename: str):
    """
    Download a translated document.
    
    Args:
        filename: Name of the translated file
        
    Returns:
        File download response
    """
    try:
        file_path = settings.OUTPUT_FOLDER / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")