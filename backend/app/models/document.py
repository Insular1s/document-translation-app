from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    success: bool = Field(..., description="Whether upload was successful")
    filename: str = Field(..., description="Uploaded filename")
    file_path: str = Field(..., description="Path where file is stored")
    file_size: int = Field(..., description="File size in bytes")
    error: Optional[str] = Field(None, description="Error message if upload failed")


class DocumentTranslationRequest(BaseModel):
    """Request model for document translation."""
    filename: str = Field(..., description="Filename of uploaded document")
    target_language: str = Field(..., description="Target language code")
    source_language: Optional[str] = Field(None, description="Source language code")
    use_llm: bool = Field(False, description="Use LLM enhancement for translation")
    preserve_formatting: bool = Field(True, description="Preserve document formatting")


class DocumentTranslationResponse(BaseModel):
    """Response model for document translation."""
    success: bool = Field(..., description="Whether translation was successful")
    output_filename: str = Field(..., description="Translated document filename")
    output_path: str = Field(..., description="Path to translated document")
    slides_translated: int = Field(..., description="Number of slides translated")
    text_frames_translated: int = Field(..., description="Number of text frames translated")
    target_language: str = Field(..., description="Target language used")
    error: Optional[str] = Field(None, description="Error message if translation failed")


class DocumentInfo(BaseModel):
    """Information about a document."""
    filename: str = Field(..., description="Document filename")
    file_path: str = Field(..., description="File path")
    file_size: int = Field(..., description="File size in bytes")
    upload_time: datetime = Field(..., description="When the file was uploaded")
    status: str = Field(..., description="Document status (uploaded/translating/completed/failed)")