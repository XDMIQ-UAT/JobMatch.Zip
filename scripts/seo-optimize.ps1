# SEO Optimization Script (PowerShell)
# Automates Google Search Console operations

$ErrorActionPreference = "Stop"

$API_URL = if ($env:API_URL) { $env:API_URL } else { "http://localhost:8000" }
$SITE_URL = if ($env:SITE_URL) { $env:SITE_URL } else { "https://jobmatch.zip" }

Write-Host "=== SEO Optimization Script ===" -ForegroundColor Cyan
Write-Host ""

# Function to make API calls
function Invoke-ApiCall {
    param(
        [string]$Method,
        [string]$Endpoint,
        [string]$Data = $null
    )
    
    $headers = @{
        "Content-Type" = "application/json"
    }
    
    try {
        if ($Data) {
            $response = Invoke-RestMethod -Uri "${API_URL}${Endpoint}" -Method $Method -Headers $headers -Body $Data
        } else {
            $response = Invoke-RestMethod -Uri "${API_URL}${Endpoint}" -Method $Method -Headers $headers
        }
        return $response | ConvertTo-Json -Depth 10
    } catch {
        Write-Host "Error: $_" -ForegroundColor Red
        return $null
    }
}

# Check SEO status
Write-Host "Checking SEO status..." -ForegroundColor Yellow
$status = Invoke-ApiCall -Method "GET" -Endpoint "/api/seo/status"
if ($status) {
    Write-Host $status
}
Write-Host ""

# Submit sitemap
Write-Host "Submitting sitemap..." -ForegroundColor Yellow
$sitemapData = @{
    sitemap_url = "${SITE_URL}/sitemap.xml"
} | ConvertTo-Json
$sitemapResult = Invoke-ApiCall -Method "POST" -Endpoint "/api/seo/sitemap/submit" -Data $sitemapData
if ($sitemapResult) {
    Write-Host $sitemapResult
}
Write-Host ""

# Get sitemaps
Write-Host "Listing submitted sitemaps..." -ForegroundColor Yellow
$sitemaps = Invoke-ApiCall -Method "GET" -Endpoint "/api/seo/sitemaps"
if ($sitemaps) {
    Write-Host $sitemaps
}
Write-Host ""

# Get search analytics (last 30 days)
Write-Host "Fetching search analytics (last 30 days)..." -ForegroundColor Yellow
$startDate = (Get-Date).AddDays(-30).ToString("yyyy-MM-dd")
$endDate = (Get-Date).ToString("yyyy-MM-dd")
$analytics = Invoke-ApiCall -Method "GET" -Endpoint "/api/seo/analytics/search?start_date=${startDate}&end_date=${endDate}&dimensions=query,page"
if ($analytics) {
    Write-Host $analytics
}
Write-Host ""

# Optimize keywords
Write-Host "Analyzing keyword optimization..." -ForegroundColor Yellow
$keywords = "longest first,longest job matches first,AI job matching,LLC job matching,capability-first matching"
$optimization = Invoke-ApiCall -Method "GET" -Endpoint "/api/seo/keywords/optimize?keywords=${keywords}"
if ($optimization) {
    Write-Host $optimization
}
Write-Host ""

# Get index status
Write-Host "Checking index status..." -ForegroundColor Yellow
$indexStatus = Invoke-ApiCall -Method "GET" -Endpoint "/api/seo/index/status"
if ($indexStatus) {
    Write-Host $indexStatus
}
Write-Host ""

Write-Host "SEO optimization check complete!" -ForegroundColor Green

