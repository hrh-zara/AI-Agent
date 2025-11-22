"""
Training module for English-Hausa translation model.
"""

import os
import logging
from typing import Dict, Any, Optional
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    EarlyStoppingCallback
)
from datasets import DatasetDict
import numpy as np


class HausaTranslationTrainer:
    """Trainer for English-Hausa translation model."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_config = config.get('model', {})
        self.training_config = config.get('training', {})
        self.logger = logging.getLogger(__name__)
        
        # Initialize model and tokenizer
        self.tokenizer = None
        self.model = None
        self.data_collator = None
        
        # Setup device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.logger.info(f"Using device: {self.device}")
        
    def initialize_model(self):
        """Initialize the model and tokenizer."""
        base_model = self.model_config.get('base_model', 'google/mt5-small')
        
        self.logger.info(f"Loading model: {base_model}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(base_model)
        
        # Load model
        self.model = AutoModelForSeq2SeqLM.from_pretrained(base_model)
        
        # Setup data collator
        self.data_collator = DataCollatorForSeq2Seq(
            tokenizer=self.tokenizer,
            model=self.model
        )
        
        # Move model to device
        self.model.to(self.device)
        
        self.logger.info("Model initialized successfully")
        
    def preprocess_function(self, examples):
        """Preprocess examples for training."""
        source_lang = self.config.get('data', {}).get('source_lang', 'en')
        target_lang = self.config.get('data', {}).get('target_lang', 'ha')
        max_length = self.model_config.get('max_length', 512)
        
        inputs = [ex[source_lang] for ex in examples['translation']]
        targets = [ex[target_lang] for ex in examples['translation']]
        
        # Add task prefix for mT5
        if 'mt5' in self.model_config.get('base_model', '').lower():
            inputs = [f"translate English to Hausa: {text}" for text in inputs]
        
        model_inputs = self.tokenizer(
            inputs,
            max_length=max_length,
            truncation=True,
            padding=True
        )
        
        # Setup the tokenizer for targets
        with self.tokenizer.as_target_tokenizer():
            labels = self.tokenizer(
                targets,
                max_length=max_length,
                truncation=True,
                padding=True
            )
        
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs
    
    def prepare_dataset(self, dataset: DatasetDict) -> DatasetDict:
        """Prepare dataset for training."""
        self.logger.info("Preprocessing dataset...")
        
        tokenized_dataset = dataset.map(
            self.preprocess_function,
            batched=True,
            remove_columns=dataset["train"].column_names
        )
        
        self.logger.info("Dataset preprocessing complete")
        return tokenized_dataset
    
    def compute_metrics(self, eval_pred):
        """Compute metrics during evaluation."""
        predictions, labels = eval_pred
        
        # Decode predictions and labels
        decoded_preds = self.tokenizer.batch_decode(
            predictions, skip_special_tokens=True
        )
        
        # Replace -100 in the labels as we can't decode them
        labels = np.where(labels != -100, labels, self.tokenizer.pad_token_id)
        decoded_labels = self.tokenizer.batch_decode(
            labels, skip_special_tokens=True
        )
        
        # Simple length-based metric (can be improved with BLEU, etc.)
        prediction_lens = [len(pred.split()) for pred in decoded_preds]
        
        return {
            "avg_prediction_length": np.mean(prediction_lens)
        }
    
    def train(self, dataset: DatasetDict, output_dir: str = None) -> None:
        """Train the translation model."""
        if not self.model or not self.tokenizer:
            raise ValueError("Model not initialized. Call initialize_model() first.")
        
        # Set output directory
        if output_dir is None:
            output_dir = os.path.join(
                self.config.get('paths', {}).get('models_dir', './models'),
                self.model_config.get('name', 'english-hausa-translator')
            )
        
        # Create directories
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare dataset
        tokenized_dataset = self.prepare_dataset(dataset)
        
        # Setup training arguments
        training_args = Seq2SeqTrainingArguments(
            output_dir=output_dir,
            num_train_epochs=self.training_config.get('num_epochs', 10),
            per_device_train_batch_size=self.training_config.get('batch_size', 16),
            per_device_eval_batch_size=self.training_config.get('batch_size', 16),
            warmup_steps=self.training_config.get('warmup_steps', 1000),
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=self.training_config.get('logging_steps', 100),
            evaluation_strategy=self.training_config.get('evaluation_strategy', 'steps'),
            eval_steps=self.training_config.get('eval_steps', 500),
            save_strategy=self.training_config.get('save_strategy', 'epoch'),
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            predict_with_generate=True,
            fp16=torch.cuda.is_available(),  # Enable mixed precision if GPU available
            dataloader_pin_memory=False,
            gradient_checkpointing=True,
            learning_rate=self.training_config.get('learning_rate', 5e-5),
        )
        
        # Setup trainer
        trainer = Seq2SeqTrainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset["train"],
            eval_dataset=tokenized_dataset.get("validation"),
            tokenizer=self.tokenizer,
            data_collator=self.data_collator,
            compute_metrics=self.compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )
        
        # Start training
        self.logger.info("Starting training...")
        trainer.train()
        
        # Save the final model
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        self.logger.info(f"Training completed. Model saved to {output_dir}")
        
        # Evaluate on test set if available
        if "test" in tokenized_dataset:
            self.logger.info("Evaluating on test set...")
            test_results = trainer.evaluate(eval_dataset=tokenized_dataset["test"])
            self.logger.info(f"Test results: {test_results}")
        
        return trainer