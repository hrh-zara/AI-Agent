#!/usr/bin/env python3
"""
Basic test script to validate the English-Hausa translator system components.
"""

import sys
import os

# Add src to path
sys.path.append('src')

def test_configuration():
    """Test configuration loading."""
    print("Testing configuration loading...")
    
    try:
        from src.utils import load_config, setup_logging
        config = load_config('config.yaml')
        
        # Check key components
        assert 'model' in config
        assert 'training' in config
        assert 'data' in config
        assert 'paths' in config
        
        print("SUCCESS: Configuration loaded successfully")
        print("   Model: {}".format(config['model']['name']))
        print("   Base model: {}".format(config['model']['base_model']))
        return True
        
    except Exception as e:
        print("FAILED: Configuration test failed: {}".format(e))
        return False


def test_utilities():
    """Test utility functions."""
    print("\nTesting utility functions...")
    
    try:
        from src.utils import clean_text, is_hausa_text, validate_languages
        
        # Test text cleaning
        dirty_text = "  Hello,   how are you?  "
        clean = clean_text(dirty_text)
        assert clean == "Hello, how are you?"
        
        # Test language validation
        validate_languages("en", "ha")  # Should not raise error
        
        print("SUCCESS: Utility functions working correctly")
        return True
        
    except Exception as e:
        print("FAILED: Utility test failed: {}".format(e))
        return False


def main():
    """Run all tests."""
    print("English-Hausa Translator System Test")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_utilities,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print("Test Results: {}/{} tests passed".format(passed, total))
    
    if passed == total:
        print("SUCCESS: All basic tests passed!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Train model: python train_model_fixed.py --create-sample")
        print("3. Start API: python api/main.py")
        print("4. Launch web app: streamlit run web_app/app.py")
        return 0
    else:
        print("FAILED: {} tests failed. Please check the errors above.".format(total - passed))
        return 1


if __name__ == "__main__":
    sys.exit(main())