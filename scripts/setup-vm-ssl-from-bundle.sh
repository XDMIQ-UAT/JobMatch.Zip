#!/bin/bash
# Setup HTTPS for jobmatch.zip domain on GCP VM using SSL bundle from /secrets
# Destroys SSL bundle after use
# DNS should already point to VM IP address

set -e

VM_NAME="${VM_NAME:-jobmatch-vm}"
ZONE="${GCP_ZONE:-us-central1-a}"
DOMAIN="${DOMAIN:-jobmatch.zip}"
SSL_BUNDLE_PATH="${SSL_BUNDLE_PATH:-secrets/jobmatch.zip-ssl-bundle.zip}"
TEMP_DIR="${TEMP_DIR:-secrets/ssl-temp}"
GCP_PROJECT_ID="${GCP_PROJECT_ID}"

echo "🔒 Setting up HTTPS for $DOMAIN on VM using SSL bundle..."
echo ""

# Check if SSL bundle exists
if [ ! -f "$SSL_BUNDLE_PATH" ]; then
    echo "❌ SSL bundle not found: $SSL_BUNDLE_PATH"
    exit 1
fi

# Get VM IP
if [ -n "$GCP_PROJECT_ID" ]; then
    VM_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --project=$GCP_PROJECT_ID --format='get(networkInterfaces[0].accessConfigs[0].natIP)' 2>/dev/null || echo "")
else
    VM_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)' 2>/dev/null || echo "")
fi

if [ -z "$VM_IP" ]; then
    echo "⚠️  Could not get VM IP automatically"
    echo "   Please ensure VM exists and gcloud is configured"
else
    echo "✅ VM IP: $VM_IP"
fi
echo ""

# Step 1: Extract SSL bundle
echo "📦 Step 1: Extracting SSL bundle..."
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
unzip -q "$SSL_BUNDLE_PATH" -d "$TEMP_DIR"

# Find certificate and key files
CERT_FILE=$(find "$TEMP_DIR" -name "*.cert.pem" -o -name "cert.pem" -o -name "fullchain.pem" | head -1)
KEY_FILE=$(find "$TEMP_DIR" -name "private.key.pem" -o -name "privkey.pem" -o -name "*.key.pem" | head -1)
CHAIN_FILE=$(find "$TEMP_DIR" -name "chain.pem" -o -name "*.chain.pem" | head -1)

if [ -z "$CERT_FILE" ] || [ -z "$KEY_FILE" ]; then
    echo "❌ Could not find certificate or key files in SSL bundle"
    echo "   Found files:"
    find "$TEMP_DIR" -type f
    exit 1
fi

echo "✅ Found certificate: $CERT_FILE"
echo "✅ Found private key: $KEY_FILE"
if [ -n "$CHAIN_FILE" ]; then
    echo "✅ Found chain: $CHAIN_FILE"
fi

# Step 2: Verify certificate
echo ""
echo "🔐 Step 2: Verifying SSL certificate..."
if command -v openssl &> /dev/null; then
    # Verify certificate is valid
    openssl x509 -in "$CERT_FILE" -text -noout > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "⚠️  Warning: Certificate validation failed, but continuing..."
    else
        echo "✅ Certificate format verified"
    fi
    
    # Try to verify key matches certificate (if openssl supports it)
    CERT_HASH=$(openssl x509 -noout -modulus -in "$CERT_FILE" 2>/dev/null | openssl md5 2>/dev/null || echo "")
    KEY_HASH=$(openssl rsa -noout -modulus -in "$KEY_FILE" 2>/dev/null | openssl md5 2>/dev/null || echo "")
    if [ -n "$CERT_HASH" ] && [ -n "$KEY_HASH" ] && [ "$CERT_HASH" == "$KEY_HASH" ]; then
        echo "✅ Certificate and key match verified"
    fi
else
    echo "⚠️  openssl not found, skipping certificate verification"
fi

# Step 3: Create fullchain if chain exists
if [ -n "$CHAIN_FILE" ]; then
    echo ""
    echo "🔗 Step 3: Creating fullchain certificate..."
    cat "$CERT_FILE" "$CHAIN_FILE" > "$TEMP_DIR/fullchain.pem"
    FULLCHAIN_FILE="$TEMP_DIR/fullchain.pem"
else
    FULLCHAIN_FILE="$CERT_FILE"
fi

# Step 4: Upload certificates to VM
echo ""
echo "📤 Step 4: Uploading certificates to VM..."

# Create SSL directory on VM
gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    sudo mkdir -p /etc/nginx/ssl/$DOMAIN
    sudo chmod 700 /etc/nginx/ssl/$DOMAIN
" 2>/dev/null || {
    echo "❌ Failed to connect to VM. Please check:"
    echo "   1. VM name: $VM_NAME"
    echo "   2. Zone: $ZONE"
    echo "   3. gcloud authentication"
    exit 1
}

# Upload certificate files
gcloud compute scp "$FULLCHAIN_FILE" $VM_NAME:/tmp/fullchain.pem --zone=$ZONE
gcloud compute scp "$KEY_FILE" $VM_NAME:/tmp/privkey.pem --zone=$ZONE
if [ -n "$CHAIN_FILE" ]; then
    gcloud compute scp "$CHAIN_FILE" $VM_NAME:/tmp/chain.pem --zone=$ZONE
fi

# Move certificates to proper location and set permissions
gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    sudo mv /tmp/fullchain.pem /etc/nginx/ssl/$DOMAIN/fullchain.pem
    sudo mv /tmp/privkey.pem /etc/nginx/ssl/$DOMAIN/privkey.pem
    if [ -f /tmp/chain.pem ]; then
        sudo mv /tmp/chain.pem /etc/nginx/ssl/$DOMAIN/chain.pem
    fi
    sudo chmod 600 /etc/nginx/ssl/$DOMAIN/privkey.pem
    sudo chmod 644 /etc/nginx/ssl/$DOMAIN/fullchain.pem
    if [ -f /etc/nginx/ssl/$DOMAIN/chain.pem ]; then
        sudo chmod 644 /etc/nginx/ssl/$DOMAIN/chain.pem
    fi
    sudo chown root:root /etc/nginx/ssl/$DOMAIN/*
"

echo "✅ Certificates uploaded to VM"

# Step 5: Configure Nginx
echo ""
echo "🌐 Step 5: Configuring Nginx with SSL certificates..."
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

    # SSL certificates from bundle
    ssl_certificate /etc/nginx/ssl/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/$DOMAIN/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header Strict-Transport-Security \"max-age=31536000; includeSubDomains\" always;
    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header X-Content-Type-Options \"nosniff\" always;
    add_header X-XSS-Protection \"1; mode=block\" always;

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
        access_log off;
    }
}
EOF

    sudo ln -sf /etc/nginx/sites-available/jobmatch /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t && sudo systemctl reload nginx
"

if [ $? -eq 0 ]; then
    echo "✅ Nginx configured and reloaded"
else
    echo "❌ Failed to configure Nginx"
    exit 1
fi

# Step 6: Optional - Verify DNS with Cloud DNS or Porkbun
echo ""
echo "🔍 Step 6: Verifying DNS configuration..."

# Check Cloud DNS if project is set
if [ -n "$GCP_PROJECT_ID" ]; then
    ZONE_NAME=$(gcloud dns managed-zones list --filter="dnsName:$DOMAIN" --format="value(name)" --project=$GCP_PROJECT_ID 2>/dev/null | head -1)
    if [ -n "$ZONE_NAME" ]; then
        echo "✅ Found Cloud DNS zone: $ZONE_NAME"
        DNS_RECORDS=$(gcloud dns record-sets list --zone=$ZONE_NAME --filter="name:$DOMAIN." --format="value(rrdatas)" --project=$GCP_PROJECT_ID 2>/dev/null)
        if [ -n "$DNS_RECORDS" ]; then
            echo "   DNS A record: $DNS_RECORDS"
            if [ -n "$VM_IP" ] && echo "$DNS_RECORDS" | grep -q "$VM_IP"; then
                echo "   ✅ DNS points to VM IP"
            else
                echo "   ⚠️  DNS may not point to VM IP ($VM_IP)"
            fi
        fi
    fi
fi

# Step 7: Clean up SSL bundle
echo ""
echo "🧹 Step 7: Cleaning up SSL bundle..."
rm -rf "$TEMP_DIR"
rm -f "$SSL_BUNDLE_PATH"

echo "✅ SSL bundle destroyed"

echo ""
echo "✅ SSL setup complete!"
echo ""
echo "🌐 Your application should now be available at:"
echo "   https://$DOMAIN"
echo "   https://www.$DOMAIN"
echo ""
echo "📋 Certificate Details:"
echo "   Certificate: /etc/nginx/ssl/$DOMAIN/fullchain.pem"
echo "   Private Key: /etc/nginx/ssl/$DOMAIN/privkey.pem"
echo ""
if [ -n "$VM_IP" ]; then
    echo "🔍 Test HTTPS:"
    echo "   curl -I https://$DOMAIN"
    echo "   curl -I https://$DOMAIN/health"
fi
echo ""
echo "⚠️  Note: SSL bundle has been destroyed as requested"

