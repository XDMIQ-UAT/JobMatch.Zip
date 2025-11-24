#!/bin/bash
# SEO Optimization Script
# Automates Google Search Console operations

set -e

API_URL="${API_URL:-http://localhost:8000}"
SITE_URL="${SITE_URL:-https://jobmatch.zip}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== SEO Optimization Script ===${NC}"
echo ""

# Function to make API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ -z "$data" ]; then
        curl -s -X "$method" "${API_URL}${endpoint}" | jq '.' 2>/dev/null || curl -s -X "$method" "${API_URL}${endpoint}"
    else
        curl -s -X "$method" "${API_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "$data" | jq '.' 2>/dev/null || curl -s -X "$method" "${API_URL}${endpoint}" -H "Content-Type: application/json" -d "$data"
    fi
}

# Check SEO status
echo -e "${YELLOW}Checking SEO status...${NC}"
STATUS=$(api_call "GET" "/api/seo/status")
echo "$STATUS" | jq '.' 2>/dev/null || echo "$STATUS"
echo ""

# Submit sitemap
echo -e "${YELLOW}Submitting sitemap...${NC}"
SITEMAP_RESULT=$(api_call "POST" "/api/seo/sitemap/submit" "{\"sitemap_url\": \"${SITE_URL}/sitemap.xml\"}")
echo "$SITEMAP_RESULT" | jq '.' 2>/dev/null || echo "$SITEMAP_RESULT"
echo ""

# Get sitemaps
echo -e "${YELLOW}Listing submitted sitemaps...${NC}"
SITEMAPS=$(api_call "GET" "/api/seo/sitemaps")
echo "$SITEMAPS" | jq '.' 2>/dev/null || echo "$SITEMAPS"
echo ""

# Get search analytics (last 30 days)
echo -e "${YELLOW}Fetching search analytics (last 30 days)...${NC}"
START_DATE=$(date -d "30 days ago" +%Y-%m-%d 2>/dev/null || date -v-30d +%Y-%m-%d 2>/dev/null || echo "")
END_DATE=$(date +%Y-%m-%d)

if [ -n "$START_DATE" ]; then
    ANALYTICS=$(api_call "GET" "/api/seo/analytics/search?start_date=${START_DATE}&end_date=${END_DATE}&dimensions=query,page")
    echo "$ANALYTICS" | jq '.' 2>/dev/null || echo "$ANALYTICS"
else
    ANALYTICS=$(api_call "GET" "/api/seo/analytics/search")
    echo "$ANALYTICS" | jq '.' 2>/dev/null || echo "$ANALYTICS"
fi
echo ""

# Optimize keywords
echo -e "${YELLOW}Analyzing keyword optimization...${NC}"
KEYWORDS="longest first,longest job matches first,AI job matching,LLC job matching,capability-first matching"
OPTIMIZATION=$(api_call "GET" "/api/seo/keywords/optimize?keywords=${KEYWORDS}")
echo "$OPTIMIZATION" | jq '.' 2>/dev/null || echo "$OPTIMIZATION"
echo ""

# Get index status
echo -e "${YELLOW}Checking index status...${NC}"
INDEX_STATUS=$(api_call "GET" "/api/seo/index/status")
echo "$INDEX_STATUS" | jq '.' 2>/dev/null || echo "$INDEX_STATUS"
echo ""

echo -e "${GREEN}SEO optimization check complete!${NC}"

