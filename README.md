# English-Hausa AI Translator for NGOs

An AI-powered language translation system designed specifically for NGOs operating in Northern Nigeria, facilitating communication between English-speaking staff and Hausa-speaking communities.

## 🎯 Project Purpose

This translator aims to:
- Bridge language barriers for NGO staff working in Northern Nigeria
- Make educational materials accessible to Hausa speakers
- Enable efficient two-way communication (English ↔ Hausa)
- Support humanitarian and development work in the region

## 📋 Target Use Cases

- **Education**: Translate educational materials and resources
- **Community Outreach**: Enable direct communication with local communities
- **Documentation**: Convert reports and documentation between languages
- **Training**: Support staff training in local languages
- **Emergency Response**: Quick communication during humanitarian crises

## 🏗️ Project Structure

```
├── data/                    # Training and test datasets
├── models/                  # Trained models and model artifacts
├── src/                     # Source code
│   ├── preprocessing/       # Data preprocessing utilities
│   ├── training/           # Model training scripts
│   ├── inference/          # Model inference and API
│   └── evaluation/         # Model evaluation tools
├── web_app/                # Web interface
├── api/                    # REST API server
├── tests/                  # Unit and integration tests
├── docs/                   # Documentation
└── requirements.txt        # Python dependencies
```

## 🚀 Getting Started

### Quick Start (5 minutes)
```bash
# 1. Clone the repository
git clone <repository-url>
cd english-hausa-translator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train with sample data
python train_model_fixed.py --create-sample

# 4. Start the API (in one terminal)
python api/main.py

# 5. Launch web interface (in another terminal)
streamlit run web_app/app.py
```

Then visit:
- **Web App**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

### Detailed Setup
See [docs/SETUP.md](docs/SETUP.md) for complete installation and configuration instructions.

## 📊 Model Performance

### Current Status
- **Base Model**: mT5 (Multilingual T5)
- **Supported Languages**: English ↔ Hausa
- **Architecture**: Sequence-to-sequence transformer
- **Training**: Fine-tuned on NGO-specific vocabulary

### Performance Metrics
*Note: Metrics depend on training data quality and size*

| Dataset Size | Training Time | Quality | Use Case |
|--------------|---------------|---------|----------|
| Sample (15 pairs) | 5-10 min | Demo only | Development |
| 1,000+ pairs | 30-60 min | Basic | Prototype |
| 10,000+ pairs | 2-4 hours | Production | NGO Operations |

### Sample Translations
- "Hello, how are you?" → "Sannu, yaya kuke?"
- "We need clean water" → "Muna bukatan ruwa mai tsabta"
- "The clinic is open today" → "Asibitin yana bude yau"

## 🤝 Contributing

This project is designed to serve NGOs in Northern Nigeria. Contributions, especially from native Hausa speakers and those familiar with the local context, are welcome.

## 📄 License

*License to be determined*

---

*Built to empower communication and education in Northern Nigeria*