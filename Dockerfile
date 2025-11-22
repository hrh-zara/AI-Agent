# English-Hausa AI Translator - Docker Image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data models logs outputs

# Set environment variables
ENV PYTHONPATH=/app/src
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501

# Expose ports
EXPOSE 8000 8501

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting English-Hausa Translator Services"\n\
echo "============================================"\n\
\n\
# Create sample data if not exists\n\
if [ ! -f "data/sample_data.json" ]; then\n\
    echo "📝 Creating sample data..."\n\
    python train_model_fixed.py --create-sample\n\
fi\n\
\n\
# Start API server in background\n\
echo "🌐 Starting API server..."\n\
python api/main.py &\n\
API_PID=$!\n\
\n\
# Wait a moment for API to start\n\
sleep 5\n\
\n\
# Start Streamlit web app\n\
echo "🖥️ Starting web interface..."\n\
streamlit run web_app/app.py --server.address 0.0.0.0 --server.port 8501 &\n\
WEB_PID=$!\n\
\n\
echo "✅ Services started successfully!"\n\
echo "   Web Interface: http://localhost:8501"\n\
echo "   API Documentation: http://localhost:8000/docs"\n\
echo ""\n\
echo "🔧 Process IDs: API=$API_PID, Web=$WEB_PID"\n\
\n\
# Wait for both processes\n\
wait\n\
' > /app/start.sh && chmod +x /app/start.sh

# Default command
CMD ["/app/start.sh"]