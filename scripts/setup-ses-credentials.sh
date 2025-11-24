#!/bin/bash
# Setup Amazon SES credentials securely
# Prompts user for credentials and saves to .env file

ENV_FILE=".env"

echo "🔐 Amazon SES Credentials Setup"
echo ""

# Check if .env file exists
if [ -f "$ENV_FILE" ]; then
    echo "⚠️  .env file already exists at $ENV_FILE"
    read -p "Do you want to add/update SES credentials? (y/n) " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "Keeping existing .env file."
        exit 0
    fi
else
    echo "📝 Creating new .env file..."
fi

echo ""
echo "Enter your Amazon SES credentials:"
echo ""

# Get credentials from user
read -p "AWS Access Key ID: " AWS_ACCESS_KEY_ID
read -sp "AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
echo ""
read -p "AWS Region (default: us-west-2): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-west-2}

read -p "SES Region (default: $AWS_REGION): " SES_REGION
SES_REGION=${SES_REGION:-$AWS_REGION}

read -p "SES From Email (e.g., admin@futurelink.zip): " SES_FROM_EMAIL
read -p "Email Provider Mode (ses/smtp, default: ses): " EMAIL_PROVIDER_MODE
EMAIL_PROVIDER_MODE=${EMAIL_PROVIDER_MODE:-ses}

echo ""
echo "🔍 Validating credentials..."

# Try to validate credentials using Python/boto3 if available
if command -v python3 &> /dev/null; then
    VALIDATION_SCRIPT=$(cat <<EOF
import boto3
from botocore.exceptions import ClientError

try:
    ses = boto3.client(
        'ses',
        aws_access_key_id='$AWS_ACCESS_KEY_ID',
        aws_secret_access_key='$AWS_SECRET_ACCESS_KEY',
        region_name='$SES_REGION'
    )
    # Try to get send quota (doesn't send email, just validates credentials)
    response = ses.get_send_quota()
    print('SUCCESS')
except ClientError as e:
    print(f'ERROR: {e}')
except Exception as e:
    print(f'ERROR: {e}')
EOF
)
    RESULT=$(echo "$VALIDATION_SCRIPT" | python3 2>&1)
    
    if echo "$RESULT" | grep -q "SUCCESS"; then
        echo "✅ Credentials validated successfully"
    elif echo "$RESULT" | grep -q "ERROR"; then
        echo "⚠️  Credential validation failed: $RESULT"
        echo "Continuing anyway..."
    fi
else
    echo "⚠️  Python3 not found, skipping validation"
fi

echo ""
echo "💾 Saving credentials to $ENV_FILE..."

# Backup existing .env if it exists
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "${ENV_FILE}.backup"
fi

# Remove existing SES-related variables from .env if present
if [ -f "$ENV_FILE" ]; then
    grep -v "^AWS_ACCESS_KEY_ID=" "$ENV_FILE" | \
    grep -v "^AWS_SECRET_ACCESS_KEY=" | \
    grep -v "^AWS_REGION=" | \
    grep -v "^SES_REGION=" | \
    grep -v "^SES_FROM_EMAIL=" | \
    grep -v "^EMAIL_PROVIDER_MODE=" > "${ENV_FILE}.tmp" || true
    mv "${ENV_FILE}.tmp" "$ENV_FILE"
fi

# Append SES configuration
cat >> "$ENV_FILE" <<EOF

# Amazon SES Configuration
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
AWS_REGION=$AWS_REGION
SES_REGION=$SES_REGION
SES_FROM_EMAIL=$SES_FROM_EMAIL
EMAIL_PROVIDER_MODE=$EMAIL_PROVIDER_MODE
EOF

# Set secure permissions
chmod 600 "$ENV_FILE"

echo "✅ Credentials saved to $ENV_FILE"
echo ""
echo "📋 Configuration Summary:"
echo "   AWS Region: $AWS_REGION"
echo "   SES Region: $SES_REGION"
echo "   From Email: $SES_FROM_EMAIL"
echo "   Provider Mode: $EMAIL_PROVIDER_MODE"
echo ""
echo "⚠️  Remember to:"
echo "   1. Verify your sender email in AWS SES console"
echo "   2. Move out of SES sandbox if needed (for production)"
echo "   3. Never commit .env file to git"
echo ""

