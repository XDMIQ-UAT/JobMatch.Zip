#!/bin/bash
# Retrieve SSL certificate bundle from Porkbun API and configure Nginx

set -e

VM_NAME="${VM_NAME:-jobmatch-vm}"
ZONE="${GCP_ZONE:-us-central1-a}"
DOMAIN="${DOMAIN:-jobmatch.zip}"
CREDENTIALS_FILE="${CREDENTIALS_FILE:-.porkbun-credentials}"

echo "🔒 Setting up SSL certificates from Porkbun for $DOMAIN..."

# Check if credentials file exists
if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo "❌ Credentials file not found: $CREDENTIALS_FILE"
    echo "   Run: ./scripts/setup-porkbun-credentials.sh first"
    exit 1
fi

# Read credentials
source "$CREDENTIALS_FILE"

if [ -z "$API_KEY" ] || [ -z "$SECRET_KEY" ]; then
    echo "❌ Invalid credentials file. Missing API_KEY or SECRET_KEY"
    exit 1
fi

# Get VM IP
VM_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
echo "VM IP: $VM_IP"

# Retrieve SSL certificate bundle from Porkbun
echo "📦 Retrieving SSL certificate bundle from Porkbun..."

# Porkbun API endpoint for retrieving SSL certificates
# Note: This assumes Porkbun provides an API endpoint for SSL certificate retrieval
# Adjust endpoint and payload based on actual Porkbun API documentation

CERT_RESPONSE=$(curl -s -X POST "https://porkbun.com/api/json/v3/ssl/retrieve/$DOMAIN" \
    -H "Content-Type: application/json" \
    -d "{
        \"apikey\": \"$API_KEY\",
        \"secretapikey\": \"$SECRET_KEY\"
    }" 2>/dev/null)

# Check if API call was successful
if echo "$CERT_RESPONSE" | grep -q '"status":"SUCCESS"'; then
    echo "✅ Certificate bundle retrieved successfully"
    
    # Extract certificate components (adjust based on actual Porkbun API response format)
    CERTIFICATE=$(echo "$CERT_RESPONSE" | grep -o '"certificate":"[^"]*' | cut -d'"' -f4 | sed 's/\\n/\n/g')
    PRIVATE_KEY=$(echo "$CERT_RESPONSE" | grep -o '"privatekey":"[^"]*' | cut -d'"' -f4 | sed 's/\\n/\n/g')
    CERTIFICATE_CHAIN=$(echo "$CERT_RESPONSE" | grep -o '"chain":"[^"]*' | cut -d'"' -f4 | sed 's/\\n/\n/g')
    
    # If API response format is different, use jq if available
    if command -v jq &> /dev/null; then
        CERTIFICATE=$(echo "$CERT_RESPONSE" | jq -r '.certificate // empty')
        PRIVATE_KEY=$(echo "$CERT_RESPONSE" | jq -r '.privatekey // empty')
        CERTIFICATE_CHAIN=$(echo "$CERT_RESPONSE" | jq -r '.chain // empty')
    fi
    
    if [ -z "$CERTIFICATE" ] || [ -z "$PRIVATE_KEY" ]; then
        echo "⚠️  Certificate data not found in API response"
        echo "API Response: $CERT_RESPONSE"
        echo ""
        echo "💡 Possible solutions:"
        echo "   1. Check Porkbun API documentation for correct endpoint format"
        echo "   2. Verify SSL certificate is issued for $DOMAIN in Porkbun dashboard"
        echo "   3. Try manual certificate download from Porkbun dashboard"
        echo "   4. Check if domain DNS is properly configured"
        echo ""
        echo "📚 Porkbun API Documentation: https://porkbun.com/api/json/v3/documentation"
        exit 1
    fi
else
    echo "❌ Failed to retrieve certificate bundle"
    echo "Response: $CERT_RESPONSE"
    echo ""
    echo "💡 Alternative: If Porkbun provides certificate download via web interface:"
    echo "   1. Log into Porkbun dashboard"
    echo "   2. Navigate to SSL certificates for $DOMAIN"
    echo "   3. Download certificate bundle"
    echo "   4. Upload to VM manually"
    exit 1
fi

# Upload certificates to VM and configure Nginx
echo "📤 Uploading certificates to VM..."

# Create temporary files for certificates
TEMP_DIR=$(mktemp -d)
echo "$CERTIFICATE" > "$TEMP_DIR/cert.pem"
echo "$PRIVATE_KEY" > "$TEMP_DIR/privkey.pem"
if [ -n "$CERTIFICATE_CHAIN" ]; then
    echo "$CERTIFICATE_CHAIN" > "$TEMP_DIR/chain.pem"
    FULLCHAIN="$CERTIFICATE\n$CERTIFICATE_CHAIN"
else
    FULLCHAIN="$CERTIFICATE"
fi
echo -e "$FULLCHAIN" > "$TEMP_DIR/fullchain.pem"

# Create SSL directory on VM and upload certificates
gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    sudo mkdir -p /etc/nginx/ssl/$DOMAIN
    sudo chmod 700 /etc/nginx/ssl/$DOMAIN
"

# Upload certificate files
gcloud compute scp "$TEMP_DIR/cert.pem" $VM_NAME:/tmp/cert.pem --zone=$ZONE
gcloud compute scp "$TEMP_DIR/privkey.pem" $VM_NAME:/tmp/privkey.pem --zone=$ZONE
gcloud compute scp "$TEMP_DIR/fullchain.pem" $VM_NAME:/tmp/fullchain.pem --zone=$ZONE

# Move certificates to proper location and set permissions
gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    sudo mv /tmp/cert.pem /etc/nginx/ssl/$DOMAIN/cert.pem
    sudo mv /tmp/privkey.pem /etc/nginx/ssl/$DOMAIN/privkey.pem
    sudo mv /tmp/fullchain.pem /etc/nginx/ssl/$DOMAIN/fullchain.pem
    sudo chmod 600 /etc/nginx/ssl/$DOMAIN/privkey.pem
    sudo chmod 644 /etc/nginx/ssl/$DOMAIN/cert.pem
    sudo chmod 644 /etc/nginx/ssl/$DOMAIN/fullchain.pem
    sudo chown root:root /etc/nginx/ssl/$DOMAIN/*
"

# Clean up temporary files
rm -rf "$TEMP_DIR"

# Update Nginx configuration
echo "🌐 Configuring Nginx with Porkbun SSL certificates..."
gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    sudo cat > /etc/nginx/sites-available/jobmatch <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Redirect HTTP to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # Porkbun SSL certificates
    ssl_certificate /etc/nginx/ssl/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/$DOMAIN/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

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
EOF

    sudo ln -sf /etc/nginx/sites-available/jobmatch /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
"

echo ""
echo "✅ SSL setup complete!"
echo ""
echo "🌐 Your application is now available at:"
echo "   https://$DOMAIN"
echo "   https://www.$DOMAIN"
echo ""
echo "📋 Certificate Details:"
echo "   Certificate: /etc/nginx/ssl/$DOMAIN/fullchain.pem"
echo "   Private Key: /etc/nginx/ssl/$DOMAIN/privkey.pem"
echo ""
echo "🔄 Certificate Renewal:"
echo "   Run this script again to renew certificates when needed"
echo "   Or set up automated renewal via cron/Warp workflow"

