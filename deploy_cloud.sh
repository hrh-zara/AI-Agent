#!/bin/bash
# Cloud deployment script for English-Hausa Translator
# For Ubuntu/Debian servers

echo "🚀 Deploying English-Hausa Translator to Cloud Server"
echo "=================================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and required system packages
echo "🐍 Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv git nginx

# Create application user
echo "👤 Creating application user..."
sudo useradd -m -s /bin/bash translator
sudo usermod -aG sudo translator

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /opt/translator
sudo chown translator:translator /opt/translator

# Switch to translator user for application setup
sudo -u translator bash << 'EOF'
cd /opt/translator

# Clone your repository (replace with your actual repo URL)
echo "📥 Cloning application repository..."
# git clone https://github.com/your-org/english-hausa-translator.git .

# For now, we'll assume files are copied manually
echo "📋 Please ensure your application files are in /opt/translator"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies (when requirements.txt is available)
echo "📦 Installing Python dependencies..."
# pip install -r requirements.txt

# Create sample data and train model
echo "🤖 Setting up model..."
# python train_model_fixed.py --create-sample

echo "✅ Application setup complete"
EOF

# Create systemd service files
echo "⚙️ Creating system services..."

# API Service
sudo tee /etc/systemd/system/translator-api.service > /dev/null << 'EOF'
[Unit]
Description=English-Hausa Translator API
After=network.target

[Service]
Type=simple
User=translator
WorkingDirectory=/opt/translator
Environment=PATH=/opt/translator/venv/bin
ExecStart=/opt/translator/venv/bin/python api/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Web App Service  
sudo tee /etc/systemd/system/translator-web.service > /dev/null << 'EOF'
[Unit]
Description=English-Hausa Translator Web App
After=network.target

[Service]
Type=simple
User=translator
WorkingDirectory=/opt/translator
Environment=PATH=/opt/translator/venv/bin
ExecStart=/opt/translator/venv/bin/streamlit run web_app/app.py --server.address 0.0.0.0 --server.port 8501
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx reverse proxy
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/translator > /dev/null << 'EOF'
server {
    listen 80;
    server_name your_domain.com;  # Replace with your domain or IP

    # Web App (main interface)
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }

    # API endpoints
    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/translator /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Enable and start services
echo "🔄 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable translator-api translator-web nginx
sudo systemctl start translator-api translator-web nginx

# Configure firewall
echo "🔒 Configuring firewall..."
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS (for future SSL)
sudo ufw --force enable

echo "✅ Deployment complete!"
echo ""
echo "🌐 Your translator is now accessible at:"
echo "   http://your_server_ip"
echo "   http://your_server_ip/api/docs (API documentation)"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status translator-api"
echo "   sudo systemctl status translator-web"  
echo "   sudo systemctl restart translator-api"
echo "   sudo journalctl -u translator-api -f"
echo ""
echo "📝 Next steps:"
echo "1. Replace 'your_domain.com' in /etc/nginx/sites-available/translator"
echo "2. Set up SSL certificate with Let's Encrypt"
echo "3. Add your training data and retrain the model"
echo "4. Configure monitoring and backups"