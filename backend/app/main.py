"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import translation, document, editor
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Fixed: was ALLOW_ORIGINS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(translation.router, prefix="/api/translation", tags=["translation"])
app.include_router(document.router, prefix="/api/document", tags=["document"])
app.include_router(editor.router, prefix="/api/editor", tags=["editor"])

# Ensure directories exist
settings.ensure_directories()

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Document Translation API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}