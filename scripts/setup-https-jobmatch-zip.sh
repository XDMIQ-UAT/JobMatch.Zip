#!/bin/bash
# Setup HTTPS for jobmatch.zip domain on GCP VM
# Uses Porkbun API for SSL certificates

set -e

VM_NAME="${VM_NAME:-jobmatch-vm}"
ZONE="${GCP_ZONE:-us-central1-a}"
DOMAIN="${DOMAIN:-jobmatch.zip}"
CREDENTIALS_FILE="${CREDENTIALS_FILE:-.porkbun-credentials}"

echo "🔒 Setting up HTTPS for $DOMAIN using Porkbun..."

# Check if credentials file exists
if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo "❌ Porkbun credentials file not found: $CREDENTIALS_FILE"
    echo "   Run: ./scripts/setup-porkbun-credentials.sh first"
    exit 1
fi

# Get VM IP
VM_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
echo "VM IP: $VM_IP"

# Call Porkbun SSL setup script
echo "📦 Retrieving SSL certificates from Porkbun..."
./scripts/porkbun-ssl-setup.sh

echo ""
echo "✅ HTTPS setup complete!"
echo ""
echo "🌐 Your application is now available at:"
echo "   https://$DOMAIN"
echo "   https://www.$DOMAIN"

