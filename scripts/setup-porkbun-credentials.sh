#!/bin/bash
# Setup Porkbun API credentials securely
# Prompts user once for credentials and saves to gitignored file

set -e

CREDENTIALS_FILE=".porkbun-credentials"

echo "🔐 Porkbun API Credentials Setup"
echo ""

# Check if credentials already exist
if [ -f "$CREDENTIALS_FILE" ]; then
    echo "⚠️  Credentials file already exists at $CREDENTIALS_FILE"
    read -p "Do you want to update it? (y/N): " update_creds
    if [[ ! "$update_creds" =~ ^[Yy]$ ]]; then
        echo "Keeping existing credentials."
        exit 0
    fi
fi

# Prompt for API key
echo "Enter your Porkbun API credentials:"
read -sp "Porkbun API Key: " API_KEY
echo ""

if [ -z "$API_KEY" ]; then
    echo "❌ API Key cannot be empty"
    exit 1
fi

# Prompt for Secret Key
read -sp "Porkbun Secret Key: " SECRET_KEY
echo ""

if [ -z "$SECRET_KEY" ]; then
    echo "❌ Secret Key cannot be empty"
    exit 1
fi

# Validate credentials by making test API call
echo "🔍 Validating credentials..."
VALIDATION_RESPONSE=$(curl -s -X POST "https://porkbun.com/api/json/v3/ping" \
    -H "Content-Type: application/json" \
    -d "{
        \"apikey\": \"$API_KEY\",
        \"secretapikey\": \"$SECRET_KEY\"
    }" 2>/dev/null)

if echo "$VALIDATION_RESPONSE" | grep -q '"status":"SUCCESS"'; then
    echo "✅ Credentials validated successfully"
else
    echo "❌ Credential validation failed"
    echo "Response: $VALIDATION_RESPONSE"
    exit 1
fi

# Save credentials securely
cat > "$CREDENTIALS_FILE" <<EOF
# Porkbun API Credentials
# DO NOT COMMIT THIS FILE TO VERSION CONTROL
API_KEY=$API_KEY
SECRET_KEY=$SECRET_KEY
EOF

# Set restrictive permissions (600 = owner read/write only)
chmod 600 "$CREDENTIALS_FILE"

echo ""
echo "✅ Credentials saved to $CREDENTIALS_FILE"
echo "🔒 File permissions set to 600 (owner read/write only)"
echo ""
echo "📋 Next steps:"
echo "   Run: ./scripts/porkbun-ssl-setup.sh to retrieve SSL certificates"

