#!/bin/bash
# GCP CLI Wrapper for Platform Access
# Documented technical backdoor feature

set -e

API_URL="${API_URL:-http://localhost:8000}"
ENDPOINT="${ENDPOINT:-/api/gcp-cli}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI not found${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}Warning: GCP CLI not authenticated${NC}"
    echo "Run: gcloud auth login"
    exit 1
fi

# Verify access
echo -e "${GREEN}Verifying GCP CLI access...${NC}"
VERIFY_RESPONSE=$(curl -s "${API_URL}${ENDPOINT}/verify")
AUTHENTICATED=$(echo "$VERIFY_RESPONSE" | grep -o '"authenticated":true' || echo "")

if [ -z "$AUTHENTICATED" ]; then
    echo -e "${RED}GCP CLI not authenticated or not authorized${NC}"
    echo "$VERIFY_RESPONSE" | jq '.' 2>/dev/null || echo "$VERIFY_RESPONSE"
    exit 1
fi

echo -e "${GREEN}GCP CLI authenticated${NC}"

# Get access token
echo -e "${GREEN}Getting access token...${NC}"
TOKEN_RESPONSE=$(curl -s "${API_URL}${ENDPOINT}/access-token")
TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}Failed to get access token${NC}"
    echo "$TOKEN_RESPONSE" | jq '.' 2>/dev/null || echo "$TOKEN_RESPONSE"
    exit 1
fi

# Execute command
COMMAND="${1:-status}"

echo -e "${GREEN}Executing command: $COMMAND${NC}"
RESPONSE=$(curl -s -X POST "${API_URL}${ENDPOINT}/execute" \
    -H "X-GCP-CLI-Token: $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"command\": \"$COMMAND\"}")

echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"

