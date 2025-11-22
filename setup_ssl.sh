#!/bin/bash
# SSL/HTTPS setup script for English-Hausa Translator
# Requires domain name pointed to your server

echo "🔒 Setting up SSL/HTTPS for English-Hausa Translator"
echo "=================================================="

# Check if domain is provided
if [ -z "$1" ]; then
    echo "❌ Error: Please provide your domain name"
    echo "Usage: ./setup_ssl.sh your-domain.com"
    exit 1
fi

DOMAIN=$1

echo "🌐 Setting up SSL for domain: $DOMAIN"

# Install Certbot
echo "📦 Installing Certbot..."
sudo apt update
sudo apt install -y snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot

# Create certbot command link
sudo ln -sf /snap/bin/certbot /usr/bin/certbot

# Update Nginx configuration with domain
echo "⚙️ Updating Nginx configuration..."
sudo sed -i "s/your_domain.com/$DOMAIN/g" /etc/nginx/sites-available/translator

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Obtain SSL certificate
echo "🔐 Obtaining SSL certificate from Let's Encrypt..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Set up automatic renewal
echo "🔄 Setting up automatic certificate renewal..."
sudo systemctl enable snap.certbot.renew.timer

# Test renewal process
sudo certbot renew --dry-run

echo "✅ SSL setup complete!"
echo ""
echo "🌐 Your translator is now accessible securely at:"
echo "   https://$DOMAIN"
echo "   https://$DOMAIN/api/docs"
echo ""
echo "🔒 SSL certificate will auto-renew every 90 days"
echo "📝 Certificate details:"
sudo certbot certificates