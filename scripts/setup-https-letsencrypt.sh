#!/bin/bash
# Setup HTTPS for jobmatch.zip using Let's Encrypt (free SSL certificates)

set -e

VM_NAME="${VM_NAME:-jobmatch-vm}"
ZONE="${GCP_ZONE:-us-central1-a}"
DOMAIN="${DOMAIN:-jobmatch.zip}"

echo "🔒 Setting up HTTPS for $DOMAIN using Let's Encrypt..."
echo ""

# Get VM IP
VM_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
echo "✅ VM IP: $VM_IP"
echo ""

# Install certbot and configure nginx
echo "📦 Installing certbot and configuring SSL..."
gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    set -e
    
    # Install certbot
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
    
    # Stop nginx temporarily for certbot
    sudo systemctl stop nginx || true
    
    # Get certificate
    sudo certbot certonly --standalone \
        --non-interactive \
        --agree-tos \
        --email bcherrman@gmail.com \
        -d $DOMAIN \
        -d www.$DOMAIN \
        --preferred-challenges http
    
    # Configure nginx with SSL
    sudo cat > /etc/nginx/sites-available/jobmatch <<'NGINXEOF'
server {
    listen 80;
    server_name jobmatch.zip www.jobmatch.zip;

    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name jobmatch.zip www.jobmatch.zip;

    # Let's Encrypt certificates
    ssl_certificate /etc/letsencrypt/live/jobmatch.zip/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jobmatch.zip/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;
    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header X-Content-Type-Options \"nosniff\" always;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
NGINXEOF

    sudo ln -sf /etc/nginx/sites-available/jobmatch /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload nginx
    sudo nginx -t
    sudo systemctl start nginx
    sudo systemctl reload nginx
    
    # Set up auto-renewal
    echo '0 0,12 * * * root certbot renew --quiet --post-hook \"systemctl reload nginx\"' | sudo tee -a /etc/cron.d/certbot-renew
"

echo ""
echo "✅ HTTPS setup complete!"
echo ""
echo "🌐 Your application is now available at:"
echo "   https://$DOMAIN"
echo "   https://www.$DOMAIN"
echo ""
echo "🔄 Certificate auto-renewal is configured"
echo "   Certificates will renew automatically every 12 hours"

