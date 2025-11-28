# Add GTM to Production Environment
# This script helps add NEXT_PUBLIC_GTM_ID to production deployment

param(
    [string]$GtmId = "GTM-KQV9THQ6"
)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Add GTM to Production" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "GTM Container ID: $GtmId" -ForegroundColor Yellow
Write-Host ""

# Check deployment method
Write-Host "Detecting deployment method..." -ForegroundColor Yellow

$deploymentMethods = @()

# Check for Docker Compose
if (Test-Path "docker-compose.prod.yml") {
    Write-Host "  ✅ Found: docker-compose.prod.yml" -ForegroundColor Green
    $deploymentMethods += "Docker Compose"
}

# Check for Vercel
if (Test-Path ".vercel") {
    Write-Host "  ✅ Found: Vercel deployment" -ForegroundColor Green
    $deploymentMethods += "Vercel"
}

# Check for Netlify
if (Test-Path "netlify.toml") {
    Write-Host "  ✅ Found: Netlify deployment" -ForegroundColor Green
    $deploymentMethods += "Netlify"
}

# Check for GitHub Actions
if (Test-Path ".github/workflows") {
    Write-Host "  ✅ Found: GitHub Actions workflows" -ForegroundColor Green
    $deploymentMethods += "GitHub Actions"
}

Write-Host ""

if ($deploymentMethods.Count -eq 0) {
    Write-Host "⚠️  No deployment configuration detected" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Manual steps:" -ForegroundColor Yellow
    Write-Host "  1. Add NEXT_PUBLIC_GTM_ID=$GtmId to your hosting platform" -ForegroundColor White
    Write-Host "  2. Rebuild and redeploy your site" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "Detected deployment methods: $($deploymentMethods -join ', ')" -ForegroundColor Cyan
    Write-Host ""
}

# Docker Compose instructions
if (Test-Path "docker-compose.prod.yml") {
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  Docker Compose Instructions" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Add to docker-compose.prod.yml frontend service:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  frontend:" -ForegroundColor White
    Write-Host "    environment:" -ForegroundColor White
    Write-Host "      - NEXT_PUBLIC_GTM_ID=$GtmId" -ForegroundColor Green
    Write-Host ""
    Write-Host "Or add to .env file on production server:" -ForegroundColor Yellow
    Write-Host "  NEXT_PUBLIC_GTM_ID=$GtmId" -ForegroundColor Green
    Write-Host ""
}

# Vercel instructions
if (Test-Path ".vercel") {
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  Vercel Instructions" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Via Vercel Dashboard:" -ForegroundColor Yellow
    Write-Host "  1. Go to: https://vercel.com/dashboard" -ForegroundColor White
    Write-Host "  2. Select your project" -ForegroundColor White
    Write-Host "  3. Settings → Environment Variables" -ForegroundColor White
    Write-Host "  4. Add:" -ForegroundColor White
    Write-Host "     Name: NEXT_PUBLIC_GTM_ID" -ForegroundColor Green
    Write-Host "     Value: $GtmId" -ForegroundColor Green
    Write-Host "     Environment: Production, Preview" -ForegroundColor Green
    Write-Host "  5. Save and redeploy" -ForegroundColor White
    Write-Host ""
    Write-Host "Via Vercel CLI:" -ForegroundColor Yellow
    Write-Host "  vercel env add NEXT_PUBLIC_GTM_ID production" -ForegroundColor White
    Write-Host "  # Enter value: $GtmId" -ForegroundColor White
    Write-Host "  vercel --prod" -ForegroundColor White
    Write-Host ""
}

# Netlify instructions
if (Test-Path "netlify.toml") {
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  Netlify Instructions" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Via Netlify Dashboard:" -ForegroundColor Yellow
    Write-Host "  1. Go to: https://app.netlify.com" -ForegroundColor White
    Write-Host "  2. Select your site" -ForegroundColor White
    Write-Host "  3. Site Settings → Environment Variables" -ForegroundColor White
    Write-Host "  4. Add:" -ForegroundColor White
    Write-Host "     Key: NEXT_PUBLIC_GTM_ID" -ForegroundColor Green
    Write-Host "     Value: $GtmId" -ForegroundColor Green
    Write-Host "  5. Save and redeploy" -ForegroundColor White
    Write-Host ""
}

# GitHub Actions instructions
if (Test-Path ".github/workflows") {
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host "  GitHub Actions Instructions" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Add to GitHub Secrets:" -ForegroundColor Yellow
    Write-Host "  1. Go to: Repository → Settings → Secrets" -ForegroundColor White
    Write-Host "  2. Add secret:" -ForegroundColor White
    Write-Host "     Name: NEXT_PUBLIC_GTM_ID" -ForegroundColor Green
    Write-Host "     Value: $GtmId" -ForegroundColor Green
    Write-Host "  3. Update workflow to use secret" -ForegroundColor White
    Write-Host ""
}

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  After Adding Environment Variable" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Rebuild and redeploy your site" -ForegroundColor Yellow
Write-Host "2. Verify GTM code in page source:" -ForegroundColor Yellow
Write-Host "   - Go to https://jobmatch.zip" -ForegroundColor White
Write-Host "   - View Page Source" -ForegroundColor White
Write-Host "   - Search for: 'googletagmanager.com/gtm.js'" -ForegroundColor White
Write-Host "   - Should see: 'gtm.js?id=$GtmId'" -ForegroundColor White
Write-Host ""
Write-Host "3. Publish GTM container:" -ForegroundColor Yellow
Write-Host "   - Go to https://tagmanager.google.com/" -ForegroundColor White
Write-Host "   - Select container: $GtmId" -ForegroundColor White
Write-Host "   - Click 'Submit' or 'Publish'" -ForegroundColor White
Write-Host ""
Write-Host "4. Wait 5-10 minutes, then retry detection test" -ForegroundColor Yellow
Write-Host ""

