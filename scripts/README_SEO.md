# SEO Automation Scripts

Automated Google Search Console management and SEO optimization scripts.

## Quick Start

### 1. Set Up Credentials

Follow the guide in `docs/SEARCH_CONSOLE_SETUP.md` to configure Google Search Console API credentials.

### 2. Run Optimization

```bash
# Linux/Mac
./scripts/seo-optimize.sh

# Windows PowerShell
.\scripts\seo-optimize.ps1
```

## Available Scripts

### `seo-optimize.sh` / `seo-optimize.ps1`

Comprehensive SEO optimization check:
- ✅ Check SEO status
- ✅ Submit sitemap
- ✅ List sitemaps
- ✅ Fetch search analytics
- ✅ Analyze keyword optimization
- ✅ Check index status

**Usage:**
```bash
./scripts/seo-optimize.sh
# or
.\scripts\seo-optimize.ps1
```

### `seo-submit-sitemap.sh`

Submit sitemap to Google Search Console.

**Usage:**
```bash
./scripts/seo-submit-sitemap.sh [sitemap_url]
# Default: https://jobmatch.zip/sitemap.xml
```

**Example:**
```bash
./scripts/seo-submit-sitemap.sh https://jobmatch.zip/sitemap.xml
```

### `seo-request-indexing.sh`

Request indexing for a specific URL.

**Usage:**
```bash
./scripts/seo-request-indexing.sh <url>
```

**Example:**
```bash
./scripts/seo-request-indexing.sh https://jobmatch.zip/matching
```

### `seo-monitor.sh`

Generate comprehensive SEO monitoring report.

**Usage:**
```bash
./scripts/seo-monitor.sh [days]
# Default: 30 days
```

**Output:**
- Reports saved to `./seo-reports/`
- Includes: status, analytics, keywords, sitemaps, index status

**Example:**
```bash
# Generate 7-day report
./scripts/seo-monitor.sh 7
```

## API Endpoints

All scripts use the backend API at `/api/seo/`. You can also call these directly:

### Check Status
```bash
curl http://localhost:8000/api/seo/status
```

### Submit Sitemap
```bash
curl -X POST http://localhost:8000/api/seo/sitemap/submit \
  -H "Content-Type: application/json" \
  -d '{"sitemap_url": "https://jobmatch.zip/sitemap.xml"}'
```

### Request Indexing
```bash
curl -X POST http://localhost:8000/api/seo/index/request \
  -H "Content-Type: application/json" \
  -d '{"url": "https://jobmatch.zip/matching"}'
```

### Get Analytics
```bash
curl "http://localhost:8000/api/seo/analytics/search?start_date=2024-01-01&end_date=2024-01-31&dimensions=query,page"
```

### Optimize Keywords
```bash
curl "http://localhost:8000/api/seo/keywords/optimize?keywords=longest first,AI job matching"
```

## Automation

### Linux/Mac (Cron)

Add to crontab for daily optimization:
```bash
# Edit crontab
crontab -e

# Add daily optimization at 2 AM
0 2 * * * /path/to/JobFinder/scripts/seo-optimize.sh >> /var/log/seo-optimize.log 2>&1

# Add weekly monitoring on Mondays at 3 AM
0 3 * * 1 /path/to/JobFinder/scripts/seo-monitor.sh >> /var/log/seo-monitor.log 2>&1
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 2:00 AM
4. Set action: Start a program
5. Program: `powershell.exe`
6. Arguments: `-File "E:\JobFinder\scripts\seo-optimize.ps1"`
7. Save task

### Docker/Container

Add to your deployment:
```yaml
# docker-compose.yml
services:
  seo-cron:
    image: your-backend-image
    command: >
      sh -c "
        while true; do
          /app/scripts/seo-optimize.sh
          sleep 86400
        done
      "
    environment:
      - API_URL=http://backend:8000
```

## Environment Variables

- `API_URL`: Backend API URL (default: `http://localhost:8000`)
- `SITE_URL`: Site URL (default: `https://jobmatch.zip`)
- `OUTPUT_DIR`: Output directory for reports (default: `./seo-reports`)

## Monitoring

### Check Logs

```bash
# View optimization logs
tail -f /var/log/seo-optimize.log

# View monitoring reports
ls -lh ./seo-reports/
```

### Generate Report

```bash
# Generate report for last 7 days
./scripts/seo-monitor.sh 7

# View report
cat ./seo-reports/seo_report_*.json | jq '.'
```

## Troubleshooting

### Script fails with "API not initialized"

1. Check credentials are set in `.env`:
   ```bash
   GOOGLE_SEARCH_CONSOLE_CREDENTIALS='{"type":"service_account",...}'
   ```

2. Verify API is accessible:
   ```bash
   curl http://localhost:8000/api/seo/status
   ```

3. Check backend logs for errors

### Script fails with "Permission denied"

1. Verify service account has Search Console access
2. Check service account email matches Search Console user list
3. Ensure service account has "Full" permission

### No data in analytics

- Search Console data takes 2-3 days to appear
- Ensure site is verified in Search Console
- Check date range (data available up to 16 months)

## Best Practices

1. **Run daily optimization** - Keep sitemap fresh
2. **Monitor weekly** - Track performance trends
3. **Request indexing** - For new/updated pages
4. **Review reports** - Identify optimization opportunities
5. **Track keywords** - Monitor target keyword performance

## Next Steps

1. ✅ Set up credentials (`docs/SEARCH_CONSOLE_SETUP.md`)
2. ✅ Test scripts manually
3. ⏳ Schedule daily optimization
4. ⏳ Set up weekly monitoring
5. ⏳ Review reports and optimize

## Support

- Full setup guide: `docs/SEARCH_CONSOLE_SETUP.md`
- SEO strategy: `docs/SEO_STRATEGY.md`
- Quick start: `docs/SEO_QUICK_START.md`

