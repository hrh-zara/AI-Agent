# Setup Guide - English-Hausa AI Translator

This guide will help you set up and run the English-Hausa AI translator for NGOs.

## 🔧 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: At least 8GB RAM (16GB recommended)
- **Storage**: 5GB free space for models and data
- **GPU**: Optional but recommended for faster training (CUDA-compatible)

### Python Dependencies
All dependencies are listed in `requirements.txt`. The main libraries include:
- PyTorch and Transformers for ML
- FastAPI for the web API
- Streamlit for the web interface
- Datasets for data processing

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd english-hausa-translator
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\\Scripts\\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Sample Data and Train Model
```bash
# This will create sample data and train a basic model
python train_model_fixed.py --create-sample
```

### 5. Start the API Server
```bash
# In one terminal
python api/main.py
```

### 6. Launch Web Interface
```bash
# In another terminal
streamlit run web_app/app.py
```

### 7. Access the Application
- **Web Interface**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs

## 📊 Working with Your Own Data

### Data Format
The system supports multiple data formats:

#### JSON Format (Recommended)
```json
[
  {
    "english": "Hello, how are you?",
    "hausa": "Sannu, yaya kuke?"
  },
  {
    "english": "Thank you very much",
    "hausa": "Na gode sosai"
  }
]
```

#### CSV Format
```csv
english,hausa
"Hello, how are you?","Sannu, yaya kuke?"
"Thank you very much","Na gode sosai"
```

#### Text Format (Tab or Pipe separated)
```
Hello, how are you?	Sannu, yaya kuke?
Thank you very much	Na gode sosai
```

### Adding Your Data

1. **Place data files** in the `data/` directory
2. **Supported formats**: `.json`, `.csv`, `.txt`
3. **Re-train the model**:
   ```bash
   python train_model_fixed.py
   ```

## 🔧 Configuration

### Main Configuration File: `config.yaml`

#### Key Settings You Can Modify:

**Model Settings**
```yaml
model:
  name: "english-hausa-translator"
  architecture: "mT5"
  base_model: "google/mt5-small"  # or "google/mt5-base" for better quality
  max_length: 512
  beam_size: 5
```

**Training Settings**
```yaml
training:
  batch_size: 16  # Reduce if you get memory errors
  learning_rate: 5e-5
  num_epochs: 10  # Increase for better quality (longer training)
```

**API Settings**
```yaml
api:
  host: "0.0.0.0"
  port: 8000
```

## 🎯 Usage Examples

### Using the Web Interface
1. Open http://localhost:8501
2. Select translation direction (English→Hausa or Hausa→English)
3. Enter your text
4. Click "Translate"

### Using the API
```python
import requests

# Translate English to Hausa
response = requests.post("http://localhost:8000/translate", json={
    "text": "Hello, how are you?",
    "source_lang": "en",
    "target_lang": "ha"
})

result = response.json()
print(result["translation"])  # "Sannu, yaya kuke?"
```

### Using Python Code Directly
```python
from src.inference.translator import HausaTranslator

# Load your trained model
translator = HausaTranslator("models/english-hausa-translator")

# Translate
translation = translator.translate(
    "Hello, how are you?",
    source_lang="en",
    target_lang="ha"
)
print(translation)  # "Sannu, yaya kuke?"
```

## 🔍 Model Training Options

### Basic Training (Sample Data)
```bash
python train_model_fixed.py --create-sample
```

### Training with Your Data
```bash
# Place your data files in data/ directory first
python train_model_fixed.py
```

### Advanced Training Options
```bash
# Use different config file
python train_model_fixed.py --config my_config.yaml

# Override data directory
python train_model_fixed.py --data-dir /path/to/my/data

# Override output directory
python train_model_fixed.py --output-dir /path/to/save/model

# Enable debug logging
python train_model_fixed.py --debug
```

## 📈 Improving Translation Quality

### 1. Add More Training Data
- **Goal**: At least 10,000+ translation pairs
- **Quality**: Ensure translations are accurate and contextually appropriate
- **Diversity**: Include various domains (medical, educational, emergency, etc.)

### 2. Use a Larger Base Model
In `config.yaml`:
```yaml
model:
  base_model: "google/mt5-base"  # Instead of mt5-small
```

### 3. Increase Training Duration
```yaml
training:
  num_epochs: 20  # Instead of 10
```

### 4. Use GPU for Training
- Install CUDA and PyTorch with GPU support
- Training will be significantly faster

## 🚨 Troubleshooting

### Common Issues

**"CUDA out of memory" Error**
```yaml
# Reduce batch size in config.yaml
training:
  batch_size: 8  # or 4
```

**API Connection Errors**
- Ensure the API server is running: `python api/main.py`
- Check if port 8000 is available

**Web App Connection Issues**
- Ensure the API server is running before starting the web app
- Check that API_BASE_URL in web_app/app.py matches your API server

**Poor Translation Quality**
- Add more training data
- Use a larger base model (mt5-base instead of mt5-small)
- Train for more epochs

**Import Errors**
- Ensure you've activated the virtual environment
- Run `pip install -r requirements.txt` again

## 📊 Performance Expectations

### With Sample Data (15 pairs)
- **Quality**: Basic demonstration only
- **Training Time**: 5-10 minutes
- **Use Case**: Testing and development

### With 1,000+ Pairs
- **Quality**: Reasonable for basic translations
- **Training Time**: 30-60 minutes
- **Use Case**: Prototype deployment

### With 10,000+ Pairs
- **Quality**: Good for production use
- **Training Time**: 2-4 hours
- **Use Case**: NGO operations

## 🔐 Deployment Considerations

### Security
- Change API host to `127.0.0.1` in production if not serving externally
- Add authentication if exposing publicly
- Review CORS settings in `api/main.py`

### Performance
- Use GPU for faster inference
- Consider model quantization for smaller deployments
- Cache frequent translations

### Monitoring
- Check API logs regularly
- Monitor translation quality with feedback
- Track usage patterns

## 📞 Support

For technical issues:
1. Check the troubleshooting section above
2. Review log files for error details
3. Ensure all dependencies are correctly installed
4. Verify your data format matches the examples

---

**Next Steps**: After setup, see `docs/USER_GUIDE.md` for detailed usage instructions.