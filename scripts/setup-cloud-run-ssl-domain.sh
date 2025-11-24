#!/bin/bash
# Setup HTTPS domain mapping for jobmatch.zip to Cloud Run using SSL bundle from /secrets
# Destroys SSL bundle after use

set -e

DOMAIN="${DOMAIN:-jobmatch.zip}"
GCP_PROJECT_ID="${GCP_PROJECT_ID}"
REGION="${GCP_REGION:-us-central1}"
CLOUD_RUN_SERVICE="${CLOUD_RUN_SERVICE}"
SSL_BUNDLE_PATH="${SSL_BUNDLE_PATH:-secrets/jobmatch.zip-ssl-bundle.zip}"
TEMP_DIR="${TEMP_DIR:-secrets/ssl-temp}"

if [ -z "$GCP_PROJECT_ID" ]; then
    echo "❌ GCP_PROJECT_ID not set"
    exit 1
fi

if [ -z "$CLOUD_RUN_SERVICE" ]; then
    echo "⚠️  CLOUD_RUN_SERVICE not set, attempting to detect..."
    # Try to get the first Cloud Run service in the region
    CLOUD_RUN_SERVICE=$(gcloud run services list --region=$REGION --format="value(name)" --limit=1 --project=$GCP_PROJECT_ID 2>/dev/null | head -1)
    if [ -z "$CLOUD_RUN_SERVICE" ]; then
        echo "❌ Could not detect Cloud Run service. Please set CLOUD_RUN_SERVICE environment variable"
        exit 1
    fi
    echo "✅ Detected Cloud Run service: $CLOUD_RUN_SERVICE"
fi

if [ ! -f "$SSL_BUNDLE_PATH" ]; then
    echo "❌ SSL bundle not found: $SSL_BUNDLE_PATH"
    exit 1
fi

echo "🔒 Setting up HTTPS domain mapping for $DOMAIN to Cloud Run service: $CLOUD_RUN_SERVICE"
echo ""

# Step 1: Extract SSL bundle
echo "📦 Step 1: Extracting SSL bundle..."
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
unzip -q "$SSL_BUNDLE_PATH" -d "$TEMP_DIR"

# Find certificate and key files
CERT_FILE=$(find "$TEMP_DIR" -name "*.cert.pem" -o -name "cert.pem" -o -name "fullchain.pem" | head -1)
KEY_FILE=$(find "$TEMP_DIR" -name "private.key.pem" -o -name "privkey.pem" -o -name "*.key.pem" | head -1)

if [ -z "$CERT_FILE" ] || [ -z "$KEY_FILE" ]; then
    echo "❌ Could not find certificate or key files in SSL bundle"
    echo "   Found files:"
    find "$TEMP_DIR" -type f
    exit 1
fi

echo "✅ Found certificate: $CERT_FILE"
echo "✅ Found private key: $KEY_FILE"

# Step 2: Verify SSL certificate
echo ""
echo "🔐 Step 2: Verifying SSL certificate..."
# Verify certificate is valid
openssl x509 -in "$CERT_FILE" -text -noout > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Invalid certificate file"
    exit 1
fi

# Verify key matches certificate
CERT_HASH=$(openssl x509 -noout -modulus -in "$CERT_FILE" | openssl md5)
KEY_HASH=$(openssl rsa -noout -modulus -in "$KEY_FILE" | openssl md5)
if [ "$CERT_HASH" != "$KEY_HASH" ]; then
    echo "⚠️  Warning: Certificate and key may not match"
else
    echo "✅ Certificate and key verified"
fi

# Step 3: Get current Cloud Run service URL
echo ""
echo "🌐 Step 3: Getting Cloud Run service URL..."
SERVICE_URL=$(gcloud run services describe "$CLOUD_RUN_SERVICE" \
    --region="$REGION" \
    --format="value(status.url)" \
    --project="$GCP_PROJECT_ID")

if [ -z "$SERVICE_URL" ]; then
    echo "❌ Could not get Cloud Run service URL"
    exit 1
fi

echo "✅ Cloud Run service URL: $SERVICE_URL"

# Step 4: Create domain mapping (Cloud Run auto-provisions SSL)
echo ""
echo "🔗 Step 4: Creating domain mapping for $DOMAIN..."
# Check if domain mapping already exists
EXISTING_MAPPING=$(gcloud run domain-mappings describe "$DOMAIN" \
    --region="$REGION" \
    --format="value(name)" \
    --project="$GCP_PROJECT_ID" 2>/dev/null || echo "")

if [ -n "$EXISTING_MAPPING" ]; then
    echo "⚠️  Domain mapping already exists, updating..."
    gcloud run domain-mappings update "$DOMAIN" \
        --region="$REGION" \
        --service="$CLOUD_RUN_SERVICE" \
        --project="$GCP_PROJECT_ID" || {
        echo "❌ Failed to update domain mapping"
        exit 1
    }
else
    gcloud run domain-mappings create "$DOMAIN" \
        --service="$CLOUD_RUN_SERVICE" \
        --region="$REGION" \
        --project="$GCP_PROJECT_ID" || {
        echo "❌ Failed to create domain mapping"
        exit 1
    }
fi

echo "✅ Domain mapping created/updated"

# Step 5: Wait for domain mapping to be ready
echo ""
echo "⏳ Step 5: Waiting for domain mapping to be ready..."
sleep 5

# Get DNS records needed
DNS_RECORDS=$(gcloud run domain-mappings describe "$DOMAIN" \
    --region="$REGION" \
    --format="value(status.resourceRecords)" \
    --project="$GCP_PROJECT_ID")

if [ -n "$DNS_RECORDS" ]; then
    echo "📋 DNS records to configure:"
    echo "$DNS_RECORDS"
    echo ""
    echo "⚠️  Please configure these DNS records at your domain registrar"
fi

# Step 6: Clean up SSL bundle
echo ""
echo "🧹 Step 6: Cleaning up SSL bundle..."
rm -rf "$TEMP_DIR"
rm -f "$SSL_BUNDLE_PATH"

echo "✅ SSL bundle destroyed"

echo ""
echo "✅ Domain mapping setup complete!"
echo ""
echo "🌐 Domain: https://$DOMAIN"
echo "🔗 Cloud Run Service: $CLOUD_RUN_SERVICE"
echo "📍 Region: $REGION"
echo "🔐 SSL: Auto-provisioned by Google Cloud (managed certificate)"
echo ""
echo "📋 Next steps:"
echo "   1. Configure DNS records at your domain registrar"
echo "   2. Wait for DNS propagation (can take up to 48 hours)"
echo "   3. Verify HTTPS is working: curl -I https://$DOMAIN"
echo ""
echo "⚠️  Note: SSL bundle has been destroyed as requested"

