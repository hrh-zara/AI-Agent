"""
Translation inference module for English-Hausa translation.
"""

import os
import logging
import torch
from typing import List, Dict, Any, Optional
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from ..utils import clean_text, is_hausa_text, validate_languages


class HausaTranslator:
    """English-Hausa bidirectional translator."""
    
    def __init__(self, model_path: str, config: Dict[str, Any] = None):
        self.model_path = model_path
        self.config = config or {}
        self.model_config = self.config.get('model', {})
        self.logger = logging.getLogger(__name__)
        
        # Model components
        self.tokenizer = None
        self.model = None
        
        # Setup device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.logger.info(f"Using device: {self.device}")
        
        # Load model
        self.load_model()
    
    def load_model(self):
        """Load the trained model and tokenizer."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        
        self.logger.info(f"Loading model from {self.model_path}")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            
            # Load model
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path)
            
            # Move to device
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            self.logger.info("Model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            raise
    
    def translate(
        self, 
        text: str, 
        source_lang: str = "en", 
        target_lang: str = "ha",
        max_length: int = None,
        num_beams: int = None
    ) -> str:
        """
        Translate text from source language to target language.
        
        Args:
            text: Input text to translate
            source_lang: Source language code ('en' or 'ha')
            target_lang: Target language code ('en' or 'ha')  
            max_length: Maximum length of output
            num_beams: Number of beams for beam search
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return ""
        
        # Validate languages
        validate_languages(source_lang, target_lang)
        
        # Clean input text
        cleaned_text = clean_text(text)
        if not cleaned_text:
            return ""
        
        # Auto-detect language if not specified correctly
        if source_lang == "en" and is_hausa_text(cleaned_text):
            source_lang, target_lang = target_lang, source_lang
            self.logger.info("Auto-detected Hausa input, switching translation direction")
        
        # Set parameters
        if max_length is None:
            max_length = self.model_config.get('max_length', 512)
        if num_beams is None:
            num_beams = self.model_config.get('beam_size', 5)
        
        try:
            # Prepare input
            if source_lang == "en":
                # English to Hausa
                input_text = f"translate English to Hausa: {cleaned_text}"
            else:
                # Hausa to English
                input_text = f"translate Hausa to English: {cleaned_text}"
            
            # Tokenize
            inputs = self.tokenizer.encode(
                input_text,
                return_tensors="pt",
                max_length=max_length,
                truncation=True
            ).to(self.device)
            
            # Generate translation
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=max_length,
                    num_beams=num_beams,
                    length_penalty=0.6,
                    early_stopping=True,
                    do_sample=False
                )
            
            # Decode output
            translation = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            ).strip()
            
            return translation
            
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            return f"Error: Unable to translate text"
    
    def translate_batch(
        self,
        texts: List[str],
        source_lang: str = "en",
        target_lang: str = "ha",
        max_length: int = None,
        num_beams: int = None
    ) -> List[str]:
        """
        Translate a batch of texts.
        
        Args:
            texts: List of input texts
            source_lang: Source language code
            target_lang: Target language code
            max_length: Maximum length of output
            num_beams: Number of beams for beam search
            
        Returns:
            List of translated texts
        """
        if not texts:
            return []
        
        translations = []
        
        for text in texts:
            translation = self.translate(
                text, source_lang, target_lang, max_length, num_beams
            )
            translations.append(translation)
        
        return translations
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if not self.model:
            return {"error": "No model loaded"}
        
        return {
            "model_path": self.model_path,
            "device": str(self.device),
            "model_type": self.model.__class__.__name__,
            "vocab_size": len(self.tokenizer) if self.tokenizer else None,
            "supported_languages": ["en", "ha"],
            "max_length": self.model_config.get('max_length', 512),
            "beam_size": self.model_config.get('beam_size', 5)
        }