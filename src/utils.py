"""
Utility functions for the English-Hausa translator.
"""

import yaml
import os
import logging
from typing import Dict, Any


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing configuration file: {e}")


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def create_directories(config: Dict[str, Any]) -> None:
    """Create necessary directories based on configuration."""
    paths = config.get('paths', {})
    
    for path_name, path_value in paths.items():
        if path_value and not os.path.exists(path_value):
            os.makedirs(path_value, exist_ok=True)
            print(f"Created directory: {path_value}")


def validate_languages(source_lang: str, target_lang: str) -> bool:
    """Validate source and target languages."""
    supported_languages = ['en', 'ha']  # English and Hausa
    
    if source_lang not in supported_languages:
        raise ValueError(f"Unsupported source language: {source_lang}")
    
    if target_lang not in supported_languages:
        raise ValueError(f"Unsupported target language: {target_lang}")
    
    return True


def clean_text(text: str, remove_special_chars: bool = False) -> str:
    """Clean and normalize text for translation."""
    if not text:
        return ""
    
    # Basic cleaning
    text = text.strip()
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Remove special characters if specified (be careful with Hausa diacritics)
    if remove_special_chars:
        # Keep basic punctuation and Hausa-specific characters
        import re
        text = re.sub(r'[^\w\s.,!?;:\'"ƙɗƴƙʼ-]', '', text)
    
    return text


def is_hausa_text(text: str) -> bool:
    """Simple heuristic to detect if text might be Hausa."""
    # Common Hausa characters and words
    hausa_chars = set('ƙɗƴʼ')
    hausa_words = {'da', 'na', 'ya', 'ta', 'su', 'mu', 'ku', 'shi', 'ita'}
    
    # Check for Hausa-specific characters
    if any(char in hausa_chars for char in text.lower()):
        return True
    
    # Check for common Hausa words
    words = text.lower().split()
    hausa_word_count = sum(1 for word in words if word in hausa_words)
    
    # If more than 20% of words are common Hausa words
    if len(words) > 0 and hausa_word_count / len(words) > 0.2:
        return True
    
    return False