#!/bin/bash
# Submit Sitemap to Google Search Console

set -e

API_URL="${API_URL:-http://localhost:8000}"
SITEMAP_URL="${1:-https://jobmatch.zip/sitemap.xml}"

echo "Submitting sitemap: $SITEMAP_URL"

RESPONSE=$(curl -s -X POST "${API_URL}/api/seo/sitemap/submit" \
    -H "Content-Type: application/json" \
    -d "{\"sitemap_url\": \"${SITEMAP_URL}\"}")

echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"

