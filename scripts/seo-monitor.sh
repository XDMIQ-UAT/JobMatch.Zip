#!/bin/bash
# SEO Monitoring Script
# Monitors search performance and generates reports

set -e

API_URL="${API_URL:-http://localhost:8000}"
OUTPUT_DIR="${OUTPUT_DIR:-./seo-reports}"
DAYS="${DAYS:-30}"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="${OUTPUT_DIR}/seo_report_${TIMESTAMP}.json"

echo -e "${BLUE}=== SEO Monitoring Report ===${NC}"
echo "Generating report: $REPORT_FILE"
echo ""

# Calculate date range
START_DATE=$(date -d "${DAYS} days ago" +%Y-%m-%d 2>/dev/null || date -v-${DAYS}d +%Y-%m-%d 2>/dev/null || echo "")
END_DATE=$(date +%Y-%m-%d)

# Collect all data
REPORT_DATA=$(cat <<EOF
{
  "report_date": "$(date -Iseconds)",
  "site_url": "https://jobmatch.zip",
  "period": {
    "start": "${START_DATE:-30 days ago}",
    "end": "${END_DATE}"
  }
}
EOF
)

# Get SEO status
echo -e "${YELLOW}Fetching SEO status...${NC}"
STATUS=$(curl -s "${API_URL}/api/seo/status")
echo "$STATUS" | jq '.' > "${OUTPUT_DIR}/status_${TIMESTAMP}.json"

# Get search analytics
echo -e "${YELLOW}Fetching search analytics...${NC}"
if [ -n "$START_DATE" ]; then
    ANALYTICS=$(curl -s "${API_URL}/api/seo/analytics/search?start_date=${START_DATE}&end_date=${END_DATE}&dimensions=query,page,date")
else
    ANALYTICS=$(curl -s "${API_URL}/api/seo/analytics/search?dimensions=query,page,date")
fi
echo "$ANALYTICS" | jq '.' > "${OUTPUT_DIR}/analytics_${TIMESTAMP}.json"

# Get keyword optimization
echo -e "${YELLOW}Analyzing keywords...${NC}"
KEYWORDS="longest first,longest job matches first,AI job matching,LLC job matching,capability-first matching"
OPTIMIZATION=$(curl -s "${API_URL}/api/seo/keywords/optimize?keywords=${KEYWORDS}")
echo "$OPTIMIZATION" | jq '.' > "${OUTPUT_DIR}/keywords_${TIMESTAMP}.json"

# Get sitemaps
echo -e "${YELLOW}Checking sitemaps...${NC}"
SITEMAPS=$(curl -s "${API_URL}/api/seo/sitemaps")
echo "$SITEMAPS" | jq '.' > "${OUTPUT_DIR}/sitemaps_${TIMESTAMP}.json"

# Get index status
echo -e "${YELLOW}Checking index status...${NC}"
INDEX_STATUS=$(curl -s "${API_URL}/api/seo/index/status")
echo "$INDEX_STATUS" | jq '.' > "${OUTPUT_DIR}/index_${TIMESTAMP}.json"

# Combine into master report
COMBINED_REPORT=$(cat <<EOF
{
  "report_date": "$(date -Iseconds)",
  "site_url": "https://jobmatch.zip",
  "period": {
    "start": "${START_DATE:-30 days ago}",
    "end": "${END_DATE}"
  },
  "status": $(echo "$STATUS" | jq '.'),
  "analytics": $(echo "$ANALYTICS" | jq '.'),
  "keywords": $(echo "$OPTIMIZATION" | jq '.'),
  "sitemaps": $(echo "$SITEMAPS" | jq '.'),
  "index_status": $(echo "$INDEX_STATUS" | jq '.')
}
EOF
)

echo "$COMBINED_REPORT" | jq '.' > "$REPORT_FILE"

echo ""
echo -e "${GREEN}Report generated: $REPORT_FILE${NC}"
echo ""
echo "Summary:"
echo "  - Status: $(echo "$STATUS" | jq -r '.api_initialized // "unknown"')"
echo "  - Analytics rows: $(echo "$ANALYTICS" | jq -r '.data.rows | length // 0')"
echo "  - Sitemaps: $(echo "$SITEMAPS" | jq -r '.sitemaps | length // 0')"

