"""
FastAPI server for English-Hausa translation API.
"""

import os
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils import load_config, setup_logging
# Importing the translator can trigger heavy imports (transformers).
# Import it lazily during startup to avoid slowing down test imports.



# Pydantic models for API
class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Text to translate")
    source_lang: str = Field(default="en", description="Source language (en or ha)")
    target_lang: str = Field(default="ha", description="Target language (en or ha)")
    max_length: int = Field(default=512, ge=50, le=1024, description="Maximum output length")
    num_beams: int = Field(default=5, ge=1, le=10, description="Number of beams for search")


class BatchTranslationRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=50, description="List of texts to translate")
    source_lang: str = Field(default="en", description="Source language (en or ha)")
    target_lang: str = Field(default="ha", description="Target language (en or ha)")
    max_length: int = Field(default=512, ge=50, le=1024, description="Maximum output length")
    num_beams: int = Field(default=5, ge=1, le=10, description="Number of beams for search")


class TranslationResponse(BaseModel):
    translation: str
    translated_text: Optional[str] = None
    source_lang: str
    target_lang: str
    original_text: str


class BatchTranslationResponse(BaseModel):
    translations: List[TranslationResponse]
    count: int


class ModelInfoResponse(BaseModel):
    model_info: Dict[str, Any]
    status: str


# Initialize FastAPI app
app = FastAPI(
    title="English-Hausa Translator API",
    description="AI-powered translation API for NGOs working in Northern Nigeria",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
translator = None
config = None
logger = None


@app.on_event("startup")
async def startup_event():
    """Initialize the translator on startup."""
    global translator, config, logger
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting English-Hausa Translator API...")
    
    try:
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
        config = load_config(config_path)
        # Get model path
        model_path = os.path.join(
            config.get('paths', {}).get('models_dir', './models'),
            config.get('model', {}).get('name', 'english-hausa-translator')
        )

        # Try lazy import of HausaTranslator to avoid heavy imports at module import time
        try:
            from src.inference.translator import HausaTranslator  # type: ignore
        except Exception as ie:
            logger.warning(f"Could not import HausaTranslator: {ie}")
            HausaTranslator = None

        # Check if model exists, if not use a fallback or demo mode
        if os.path.exists(model_path) and HausaTranslator is not None:
            try:
                translator = HausaTranslator(model_path, config)
                logger.info("Model loaded successfully")
            except Exception as le:
                logger.error(f"Failed to initialize HausaTranslator: {le}")
                translator = None
        else:
            logger.warning(f"Model not found at {model_path} or HausaTranslator unavailable. API will run in demo mode.")
            translator = None
            
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        translator = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "English-Hausa Translator API for NGOs",
        "version": "1.0.0",
        "status": "online",
        "model_loaded": translator is not None,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": translator is not None,
        "timestamp": "2024-10-03T23:50:00Z"
    }


@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate a single text from source language to target language.
    """
    if translator is None:
        # Demo mode - return mock translation
        demo_translations = {
            ("Hello, how are you?", "en", "ha"): "Sannu, yaya kuke?",
            ("Good morning", "en", "ha"): "Barka da safe",
            ("Thank you", "en", "ha"): "Na gode",
            ("Sannu, yaya kuke?", "ha", "en"): "Hello, how are you?",
            ("Barka da safe", "ha", "en"): "Good morning",
            ("Na gode", "ha", "en"): "Thank you"
        }
        
        # Try to find a demo translation
        key = (request.text.strip(), request.source_lang, request.target_lang)
        translation = demo_translations.get(key, f"[DEMO] Translated: {request.text}")
        
        return TranslationResponse(
            translation=translation,
            translated_text=translation,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            original_text=request.text
        )
    
    try:
        # Actual translation
        translation = translator.translate(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            max_length=request.max_length,
            num_beams=request.num_beams
        )
        
        return TranslationResponse(
            translation=translation,
            translated_text=translation,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            original_text=request.text
        )
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.post("/translate/batch", response_model=BatchTranslationResponse)
async def translate_batch(request: BatchTranslationRequest):
    """
    Translate multiple texts in batch.
    """
    if translator is None:
        # Demo mode
        translations = [
            TranslationResponse(
                translation=f"[DEMO] Translated: {text}",
                translated_text=f"[DEMO] Translated: {text}",
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                original_text=text
            )
            for text in request.texts
        ]
        
        return BatchTranslationResponse(
            translations=translations,
            count=len(translations)
        )
    
    try:
        # Actual batch translation
        translated_texts = translator.translate_batch(
            texts=request.texts,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            max_length=request.max_length,
            num_beams=request.num_beams
        )
        
        translations = [
            TranslationResponse(
                translation=translation,
                translated_text=translation,
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                original_text=original_text
            )
            for translation, original_text in zip(translated_texts, request.texts)
        ]
        
        return BatchTranslationResponse(
            translations=translations,
            count=len(translations)
        )
        
    except Exception as e:
        logger.error(f"Batch translation error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch translation failed: {str(e)}")


@app.get("/model/info", response_model=ModelInfoResponse)
async def get_model_info():
    """Get information about the loaded model."""
    if translator is None:
        return ModelInfoResponse(
            model_info={
                "status": "demo_mode",
                "message": "No trained model loaded. API running in demo mode.",
                "supported_languages": ["en", "ha"]
            },
            status="demo"
        )
    
    try:
        model_info = translator.get_model_info()
        return ModelInfoResponse(
            model_info=model_info,
            status="loaded"
        )
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve model information")


@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages."""
    return {
        "supported_languages": {
            "en": {
                "name": "English",
                "native_name": "English"
            },
            "ha": {
                "name": "Hausa", 
                "native_name": "Hausa"
            }
        },
        "translation_pairs": [
            {"source": "en", "target": "ha"},
            {"source": "ha", "target": "en"}
        ]
    }


# Run the app
if __name__ == "__main__":
    import uvicorn
    
    # Load config for port
    try:
        config = load_config("../config.yaml")
        host = config.get('api', {}).get('host', '0.0.0.0')
        port = config.get('api', {}).get('port', 8000)
    except:
        host = '0.0.0.0'
        port = 8000
    
    uvicorn.run(app, host=host, port=port)