#!/usr/bin/env python3
"""
Main training script for English-Hausa translation model.

Usage:
    python train_model.py [--config config.yaml] [--data-dir data/] [--output-dir models/]

This script:
1. Loads the configuration
2. Prepares the dataset 
3. Initializes the trainer
4. Trains the model
5. Evaluates the results
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.append('src')

from src.utils import load_config, setup_logging, create_directories
from src.preprocessing.data_loader import DataLoader
from src.training.trainer_fixed import HausaTranslationTrainer


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Train English-Hausa translation model for NGOs"
    )
    
    parser.add_argument(
        '--config', 
        type=str, 
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        help='Override data directory from config'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str, 
        help='Override output directory from config'
    )
    
    parser.add_argument(
        '--create-sample',
        action='store_true',
        help='Create sample data for demonstration'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    return parser.parse_args()


def main():
    """Main training function."""
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    logger = setup_logging(log_level)
    
    logger.info("🚀 Starting English-Hausa Translation Model Training")
    logger.info("=" * 60)
    
    try:
        # Load configuration
        logger.info(f"📖 Loading configuration from {args.config}")
        config = load_config(args.config)
        
        # Override directories if specified
        if args.data_dir:
            config['paths']['data_dir'] = args.data_dir
        if args.output_dir:
            config['paths']['models_dir'] = args.output_dir
        
        # Create necessary directories
        logger.info("📁 Creating directories...")
        create_directories(config)
        
        # Initialize data loader
        logger.info("🔧 Initializing data loader...")
        data_loader = DataLoader(config)
        
        # Create sample data if requested or no data exists
        data_dir = config['paths']['data_dir']
        sample_data_path = os.path.join(data_dir, 'sample_data.json')
        
        if args.create_sample or not os.path.exists(sample_data_path):
            logger.info("📝 Creating sample English-Hausa dataset...")
            data_loader.save_sample_data(sample_data_path)
        
        # Load and preprocess data
        logger.info("📊 Loading training data...")
        
        # Look for data files in the data directory
        data_files = []
        for ext in ['*.json', '*.csv', '*.txt']:
            data_files.extend(Path(data_dir).glob(ext))
        
        if not data_files:
            logger.warning("⚠️  No data files found. Using sample data only.")
            data_files = [sample_data_path]
        
        # Load all data files
        all_pairs = data_loader.load_from_files([str(f) for f in data_files])
        logger.info(f"📈 Loaded {len(all_pairs)} translation pairs")
        \n        if len(all_pairs) < 10:\n            logger.warning(\"⚠️  Very small dataset. Consider adding more data for better results.\")\n        \n        # Preprocess data\n        logger.info(\"🔄 Preprocessing data...\")\n        processed_pairs = data_loader.preprocess_pairs(all_pairs)\n        logger.info(f\"✅ Preprocessed {len(processed_pairs)} valid pairs\")\n        \n        if len(processed_pairs) == 0:\n            logger.error(\"❌ No valid data pairs after preprocessing. Check your data.\")\n            return 1\n        \n        # Create HuggingFace dataset\n        logger.info(\"🏗️  Creating training dataset...\")\n        dataset = data_loader.create_huggingface_dataset(processed_pairs)\n        \n        # Log dataset info\n        for split, split_dataset in dataset.items():\n            logger.info(f\"   {split}: {len(split_dataset)} examples\")\n        \n        # Initialize trainer\n        logger.info(\"🏃 Initializing trainer...\")\n        trainer = HausaTranslationTrainer(config)\n        \n        # Initialize model\n        logger.info(\"🤖 Loading base model...\")\n        trainer.initialize_model()\n        \n        # Train the model\n        logger.info(\"🎯 Starting model training...\")\n        logger.info(\"This may take a while depending on your hardware and dataset size.\")\n        \n        final_trainer = trainer.train(dataset)\n        \n        logger.info(\"🎉 Training completed successfully!\")\n        \n        # Show final model location\n        model_path = os.path.join(\n            config['paths']['models_dir'],\n            config['model']['name']\n        )\n        logger.info(f\"💾 Model saved to: {model_path}\")\n        \n        logger.info(\"\" * 60)\n        logger.info(\"🚀 Next Steps:\")\n        logger.info(\"1. Start the API server: python api/main.py\")\n        logger.info(\"2. Launch the web app: streamlit run web_app/app.py\")\n        logger.info(\"3. Test translations with your NGO use cases\")\n        \n        return 0\n        \n    except KeyboardInterrupt:\n        logger.info(\"⏹️  Training interrupted by user\")\n        return 1\n        \n    except Exception as e:\n        logger.error(f\"💥 Training failed with error: {e}\")\n        if args.debug:\n            import traceback\n            logger.error(traceback.format_exc())\n        return 1\n\n\nif __name__ == \"__main__\":\n    sys.exit(main())