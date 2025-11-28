# Quick script to add GTM Container ID to .env.local

param(
    [Parameter(Mandatory=$true)]
    [string]$GtmId
)

$ErrorActionPreference = "Continue"

# Validate GTM ID format
if ($GtmId -notmatch "^GTM-[A-Z0-9]+$") {
    Write-Host "❌ Invalid GTM Container ID format. Expected: GTM-XXXXXXX" -ForegroundColor Red
    exit 1
}

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Adding GTM Container ID" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env.local exists
$envFile = ".env.local"
$frontendEnvFile = "frontend\.env.local"

# Add to root .env.local
if (Test-Path $envFile) {
    $content = Get-Content $envFile -Raw
    
    if ($content -match "NEXT_PUBLIC_GTM_ID") {
        # Update existing
        $content = $content -replace "NEXT_PUBLIC_GTM_ID=.*", "NEXT_PUBLIC_GTM_ID=$GtmId"
        Set-Content $envFile $content
        Write-Host "✅ Updated ${envFile} with GTM ID: ${GtmId}" -ForegroundColor Green
    } else {
        # Add new
        Add-Content $envFile "`n# Google Tag Manager Container ID`nNEXT_PUBLIC_GTM_ID=$GtmId"
        Write-Host "✅ Added GTM ID to ${envFile}: ${GtmId}" -ForegroundColor Green
    }
} else {
    # Create new
    Set-Content $envFile "# Google Tag Manager Container ID`nNEXT_PUBLIC_GTM_ID=$GtmId"
        Write-Host "✅ Created ${envFile} with GTM ID: ${GtmId}" -ForegroundColor Green
}

# Add to frontend .env.local
if (Test-Path "frontend") {
    if (Test-Path $frontendEnvFile) {
        $content = Get-Content $frontendEnvFile -Raw
        
        if ($content -match "NEXT_PUBLIC_GTM_ID") {
            $content = $content -replace "NEXT_PUBLIC_GTM_ID=.*", "NEXT_PUBLIC_GTM_ID=$GtmId"
            Set-Content $frontendEnvFile $content
            Write-Host "✅ Updated ${frontendEnvFile} with GTM ID: ${GtmId}" -ForegroundColor Green
        } else {
            Add-Content $frontendEnvFile "`n# Google Tag Manager Container ID`nNEXT_PUBLIC_GTM_ID=$GtmId"
            Write-Host "✅ Added GTM ID to ${frontendEnvFile}: ${GtmId}" -ForegroundColor Green
        }
    } else {
        Set-Content $frontendEnvFile "# Google Tag Manager Container ID`nNEXT_PUBLIC_GTM_ID=$GtmId"
        Write-Host "✅ Created ${frontendEnvFile} with GTM ID: ${GtmId}" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Next Steps" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Restart Next.js dev server:" -ForegroundColor Yellow
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "2. Verify GTM is working:" -ForegroundColor Yellow
Write-Host "   - Open https://jobmatch.zip" -ForegroundColor White
Write-Host "   - Open DevTools (F12) → Console" -ForegroundColor White
Write-Host "   - Look for: 'Google Tag Manager initialized'" -ForegroundColor White
Write-Host ""
Write-Host "3. Test with GTM Preview mode:" -ForegroundColor Yellow
Write-Host "   - Go to https://tagmanager.google.com/" -ForegroundColor White
Write-Host "   - Click 'Preview' button" -ForegroundColor White
Write-Host "   - Enter: https://jobmatch.zip" -ForegroundColor White
Write-Host ""
Write-Host "✅ GTM Container ID configured: ${GtmId}" -ForegroundColor Green

