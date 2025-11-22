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
        
        if len(all_pairs) < 10:
            logger.warning("⚠️  Very small dataset. Consider adding more data for better results.")
        
        # Preprocess data
        logger.info("🔄 Preprocessing data...")
        processed_pairs = data_loader.preprocess_pairs(all_pairs)
        logger.info(f"✅ Preprocessed {len(processed_pairs)} valid pairs")
        
        if len(processed_pairs) == 0:
            logger.error("❌ No valid data pairs after preprocessing. Check your data.")
            return 1
        
        # Create HuggingFace dataset
        logger.info("🏗️  Creating training dataset...")
        dataset = data_loader.create_huggingface_dataset(processed_pairs)
        
        # Log dataset info
        for split, split_dataset in dataset.items():
            logger.info(f"   {split}: {len(split_dataset)} examples")
        
        # Initialize trainer
        logger.info("🏃 Initializing trainer...")
        trainer = HausaTranslationTrainer(config)
        
        # Initialize model
        logger.info("🤖 Loading base model...")
        trainer.initialize_model()
        
        # Train the model
        logger.info("🎯 Starting model training...")
        logger.info("This may take a while depending on your hardware and dataset size.")
        
        final_trainer = trainer.train(dataset)
        
        logger.info("🎉 Training completed successfully!")
        
        # Show final model location
        model_path = os.path.join(
            config['paths']['models_dir'],
            config['model']['name']
        )
        logger.info(f"💾 Model saved to: {model_path}")
        
        logger.info("=" * 60)
        logger.info("🚀 Next Steps:")
        logger.info("1. Start the API server: python api/main.py")
        logger.info("2. Launch the web app: streamlit run web_app/app.py")
        logger.info("3. Test translations with your NGO use cases")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("⏹️  Training interrupted by user")
        return 1
        
    except Exception as e:
        logger.error(f"💥 Training failed with error: {e}")
        if args.debug:
            import traceback
            logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())