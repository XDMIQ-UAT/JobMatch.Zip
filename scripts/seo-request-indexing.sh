#!/bin/bash
# Request Indexing for a URL

set -e

API_URL="${API_URL:-http://localhost:8000}"
URL="${1}"

if [ -z "$URL" ]; then
    echo "Usage: $0 <url>"
    echo "Example: $0 https://jobmatch.zip/matching"
    exit 1
fi

echo "Requesting indexing for: $URL"

RESPONSE=$(curl -s -X POST "${API_URL}/api/seo/index/request" \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"${URL}\"}")

echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"

