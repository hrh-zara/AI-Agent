"""
Data loading and preprocessing for English-Hausa translation.
"""

import os
import pandas as pd
import json
from typing import List, Tuple, Dict, Any
from datasets import Dataset, DatasetDict
import logging

from ..utils import clean_text, is_hausa_text


class DataLoader:
    """Load and preprocess translation data."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data_config = config.get('data', {})
        self.preprocessing_config = config.get('preprocessing', {})
        self.logger = logging.getLogger(__name__)
        
    def load_from_files(self, file_paths: List[str]) -> List[Tuple[str, str]]:
        """Load translation pairs from various file formats."""
        all_pairs = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                self.logger.warning(f"File not found: {file_path}")
                continue
                
            file_extension = file_path.lower().split('.')[-1]
            
            try:
                if file_extension == 'csv':
                    pairs = self._load_from_csv(file_path)
                elif file_extension == 'json':
                    pairs = self._load_from_json(file_path)
                elif file_extension == 'txt':
                    pairs = self._load_from_txt(file_path)
                else:
                    self.logger.warning(f"Unsupported file format: {file_extension}")
                    continue
                    
                all_pairs.extend(pairs)
                self.logger.info(f"Loaded {len(pairs)} pairs from {file_path}")
                
            except Exception as e:
                self.logger.error(f"Error loading {file_path}: {e}")
                
        return all_pairs
    
    def _load_from_csv(self, file_path: str) -> List[Tuple[str, str]]:
        """Load from CSV file with 'english' and 'hausa' columns."""
        df = pd.read_csv(file_path)
        
        # Try different possible column names
        english_cols = ['english', 'en', 'source', 'English']
        hausa_cols = ['hausa', 'ha', 'target', 'Hausa']
        
        english_col = None
        hausa_col = None
        
        for col in english_cols:
            if col in df.columns:
                english_col = col
                break
                
        for col in hausa_cols:
            if col in df.columns:
                hausa_col = col
                break
        
        if not english_col or not hausa_col:
            raise ValueError(f"Could not find English and Hausa columns in {file_path}")
        
        pairs = []
        for _, row in df.iterrows():
            english = str(row[english_col]).strip()
            hausa = str(row[hausa_col]).strip()
            
            if english and hausa and english != 'nan' and hausa != 'nan':
                pairs.append((english, hausa))
        
        return pairs
    
    def _load_from_json(self, file_path: str) -> List[Tuple[str, str]]:
        """Load from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pairs = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    english = item.get('english', item.get('en', ''))
                    hausa = item.get('hausa', item.get('ha', ''))
                    
                    if english and hausa:
                        pairs.append((english.strip(), hausa.strip()))
        
        return pairs
    
    def _load_from_txt(self, file_path: str) -> List[Tuple[str, str]]:
        """Load from text file (assuming parallel format or tab-separated)."""
        pairs = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Try tab-separated format
                if '\\t' in line:
                    parts = line.split('\\t')
                    if len(parts) >= 2:
                        pairs.append((parts[0].strip(), parts[1].strip()))
                
                # Try pipe-separated format
                elif '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        pairs.append((parts[0].strip(), parts[1].strip()))
        
        return pairs
    
    def preprocess_pairs(self, pairs: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Preprocess translation pairs."""
        processed_pairs = []
        
        for english, hausa in pairs:
            # Clean text
            english_clean = clean_text(
                english, 
                self.preprocessing_config.get('remove_special_chars', False)
            )
            hausa_clean = clean_text(
                hausa, 
                self.preprocessing_config.get('remove_special_chars', False)
            )
            
            # Skip empty or very short texts
            min_length = self.preprocessing_config.get('min_length', 5)
            if len(english_clean) < min_length or len(hausa_clean) < min_length:
                continue
            
            # Skip very long texts
            max_length = self.preprocessing_config.get('max_length', 200)
            if len(english_clean) > max_length or len(hausa_clean) > max_length:
                continue
            
            processed_pairs.append((english_clean, hausa_clean))
        
        # Remove duplicates if specified
        if self.preprocessing_config.get('remove_duplicates', True):
            processed_pairs = list(set(processed_pairs))
        
        self.logger.info(f"Preprocessed {len(processed_pairs)} valid pairs")
        return processed_pairs
    
    def create_huggingface_dataset(self, pairs: List[Tuple[str, str]]) -> DatasetDict:
        """Create HuggingFace dataset from translation pairs."""
        
        # Prepare data
        data = {
            'translation': [
                {
                    self.data_config.get('source_lang', 'en'): english,
                    self.data_config.get('target_lang', 'ha'): hausa
                }
                for english, hausa in pairs
            ]
        }
        
        # Create dataset
        dataset = Dataset.from_dict(data)
        
        # Split dataset
        test_split = self.data_config.get('test_split', 0.1)
        validation_split = self.data_config.get('validation_split', 0.1)
        
        # First split: train + validation vs test
        train_val_test = dataset.train_test_split(test_size=test_split, seed=42)
        
        # Second split: train vs validation
        if validation_split > 0:
            train_val = train_val_test['train'].train_test_split(
                test_size=validation_split / (1 - test_split), seed=42
            )
            
            return DatasetDict({
                'train': train_val['train'],
                'validation': train_val['test'],
                'test': train_val_test['test']
            })
        else:
            return DatasetDict({
                'train': train_val_test['train'],
                'test': train_val_test['test']
            })
    
    def save_sample_data(self, output_path: str = "data/sample_data.json"):
        """Create sample English-Hausa data for demonstration."""
        
        sample_pairs = [
            ("Hello, how are you?", "Sannu, yaya kuke?"),
            ("Good morning", "Barka da safe"),
            ("Thank you very much", "Na gode sosai"),
            ("What is your name?", "Menene sunanka?"),
            ("I am fine", "Ina lafiya"),
            ("Welcome to our community", "Barka da zuwa ga al'ummarmu"),
            ("We need clean water", "Muna bukatan ruwa mai tsabta"),
            ("Education is very important", "Ilimi yana da muhimmanci sosai"),
            ("The clinic is open today", "Asibitin yana bude yau"),
            ("Please help us", "Don Allah ku taimake mu"),
            ("The meeting will start at 9 AM", "Taron zai fara da karfe 9 na safe"),
            ("Children need vaccination", "Yara suna bukatan allurar rigakafi"),
            ("Food distribution is tomorrow", "Rabon abinci zai kasance gobe"),
            ("The school needs books", "Makarantar tana bukatan littattafai"),
            ("Health care is a basic right", "Kiwon lafiya hakkki ne na asali"),
        ]
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Format as list of dictionaries
        data = [
            {"english": english, "hausa": hausa}
            for english, hausa in sample_pairs
        ]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Sample data saved to {output_path}")
        return sample_pairs