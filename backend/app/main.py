from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Ensure directories exist
settings.ensure_directories()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Document Translation API with Azure Translator and OpenRouter integration"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routes
from app.api.routes import translation, document, editor

app.include_router(translation.router, prefix="/api/translation", tags=["translation"])
app.include_router(document.router, prefix="/api/document", tags=["document"])
app.include_router(editor.router, prefix="/api/editor", tags=["editor"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Document Translation API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": settings.SUPPORTED_LANGUAGES
    }