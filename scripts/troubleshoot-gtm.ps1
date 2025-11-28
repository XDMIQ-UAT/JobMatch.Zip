# Troubleshoot GTM Detection Issues

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  GTM Troubleshooting" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check 1: Environment files
Write-Host "1. Checking environment files..." -ForegroundColor Yellow
$envFiles = @(".env.local", "frontend\.env.local")
foreach ($file in $envFiles) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        if ($content -match "NEXT_PUBLIC_GTM_ID=(GTM-[A-Z0-9]+)") {
            $gtmId = $matches[1]
            Write-Host "   ✅ $file - Found: $gtmId" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $file - GTM ID not found" -ForegroundColor Red
        }
    } else {
        Write-Host "   ⚠️  $file - File not found" -ForegroundColor Yellow
    }
}

Write-Host ""

# Check 2: GTM code in layout.tsx
Write-Host "2. Checking GTM code in layout.tsx..." -ForegroundColor Yellow
$layoutFile = "frontend\app\layout.tsx"
if (Test-Path $layoutFile) {
    $content = Get-Content $layoutFile -Raw
    
    if ($content -match "NEXT_PUBLIC_GTM_ID") {
        Write-Host "   ✅ Environment variable check found" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Environment variable check NOT found" -ForegroundColor Red
    }
    
    if ($content -match "googletagmanager.com/gtm.js") {
        Write-Host "   ✅ GTM script code found" -ForegroundColor Green
    } else {
        Write-Host "   ❌ GTM script code NOT found" -ForegroundColor Red
    }
    
    if ($content -match "googletagmanager.com/ns.html") {
        Write-Host "   ✅ GTM noscript code found" -ForegroundColor Green
    } else {
        Write-Host "   ❌ GTM noscript code NOT found" -ForegroundColor Red
    }
} else {
    Write-Host "   ❌ layout.tsx not found" -ForegroundColor Red
}

Write-Host ""

# Check 3: Common issues
Write-Host "3. Common issues to check:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   ⚠️  Is the site deployed/live?" -ForegroundColor Yellow
Write-Host "      - GTM detection works on LIVE sites, not localhost" -ForegroundColor White
Write-Host "      - If testing locally, use GTM Preview mode instead" -ForegroundColor White
Write-Host ""
Write-Host "   ⚠️  Is Next.js dev server running?" -ForegroundColor Yellow
Write-Host "      - Restart after adding .env.local" -ForegroundColor White
Write-Host "      - Check: cd frontend && npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "   ⚠️  Is the container published in GTM?" -ForegroundColor Yellow
Write-Host "      - Go to GTM Dashboard → Container → Submit/Publish" -ForegroundColor White
Write-Host "      - Unpublished containers won't be detected" -ForegroundColor White
Write-Host ""
Write-Host "   ⚠️  Is the site accessible?" -ForegroundColor Yellow
Write-Host "      - Check https://jobmatch.zip loads correctly" -ForegroundColor White
Write-Host "      - Check for SSL/HTTPS issues" -ForegroundColor White
Write-Host ""

# Check 4: Production build check
Write-Host "4. Production build considerations:" -ForegroundColor Yellow
Write-Host "   ⚠️  Environment variables must be set at BUILD time" -ForegroundColor White
Write-Host "   ⚠️  For production, set NEXT_PUBLIC_GTM_ID in:" -ForegroundColor White
Write-Host "      - Hosting platform environment variables" -ForegroundColor Gray
Write-Host "      - Vercel: Project Settings → Environment Variables" -ForegroundColor Gray
Write-Host "      - Netlify: Site Settings → Environment Variables" -ForegroundColor Gray
Write-Host "      - Other: Set in deployment environment" -ForegroundColor Gray
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Solutions" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "For LOCAL testing:" -ForegroundColor Yellow
Write-Host "  1. Use GTM Preview mode (not detection test)" -ForegroundColor White
Write-Host "  2. Go to GTM Dashboard → Preview" -ForegroundColor White
Write-Host "  3. Enter: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "For PRODUCTION (https://jobmatch.zip):" -ForegroundColor Yellow
Write-Host "  1. Ensure NEXT_PUBLIC_GTM_ID is set in hosting platform" -ForegroundColor White
Write-Host "  2. Rebuild and redeploy the site" -ForegroundColor White
Write-Host "  3. Publish container in GTM Dashboard" -ForegroundColor White
Write-Host "  4. Wait 5-10 minutes for detection to work" -ForegroundColor White
Write-Host "  5. Verify GTM code appears in page source (View Source)" -ForegroundColor White
Write-Host ""
Write-Host "Quick verification:" -ForegroundColor Yellow
Write-Host "  - View page source: https://jobmatch.zip" -ForegroundColor White
Write-Host "  - Search for: 'googletagmanager.com/gtm.js'" -ForegroundColor White
Write-Host "  - Should see: 'gtm.js?id=GTM-KQV9THQ6'" -ForegroundColor White
Write-Host ""

