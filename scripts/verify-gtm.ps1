# Verify Google Tag Manager Setup

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  GTM Setup Verification" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check .env.local files
Write-Host "Checking environment files..." -ForegroundColor Yellow

$envFiles = @(".env.local", "frontend\.env.local")
foreach ($file in $envFiles) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        if ($content -match "NEXT_PUBLIC_GTM_ID=GTM-[A-Z0-9]+") {
            $gtmId = ($content -match "NEXT_PUBLIC_GTM_ID=(GTM-[A-Z0-9]+)") | Out-Null
            $gtmId = $matches[1]
            Write-Host "  ✅ $file - Found GTM ID: $gtmId" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  $file - GTM ID not found or invalid format" -ForegroundColor Yellow
            $allGood = $false
        }
    } else {
        Write-Host "  ⚠️  $file - File not found" -ForegroundColor Yellow
        $allGood = $false
    }
}

Write-Host ""

# Check layout.tsx for GTM code
Write-Host "Checking GTM code in layout.tsx..." -ForegroundColor Yellow

$layoutFile = "frontend\app\layout.tsx"
if (Test-Path $layoutFile) {
    $content = Get-Content $layoutFile -Raw
    
    $checks = @(
        @{ Name = "GTM script in <head>"; Pattern = "googletagmanager.com/gtm.js"; Pass = $false },
        @{ Name = "GTM noscript in <body>"; Pattern = "googletagmanager.com/ns.html"; Pass = $false },
        @{ Name = "Environment variable check"; Pattern = "NEXT_PUBLIC_GTM_ID"; Pass = $false },
        @{ Name = "dataLayer initialization"; Pattern = "dataLayer"; Pass = $false }
    )
    
    foreach ($check in $checks) {
        if ($content -match $check.Pattern) {
            Write-Host "  ✅ $($check.Name)" -ForegroundColor Green
            $check.Pass = $true
        } else {
            Write-Host "  ❌ $($check.Name) - Not found" -ForegroundColor Red
            $allGood = $false
        }
    }
} else {
    Write-Host "  ❌ layout.tsx not found at $layoutFile" -ForegroundColor Red
    $allGood = $false
}

Write-Host ""

# Summary
Write-Host "================================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "  ✅ GTM Setup Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Restart Next.js dev server:" -ForegroundColor White
    Write-Host "     cd frontend" -ForegroundColor Gray
    Write-Host "     npm run dev" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Verify in browser:" -ForegroundColor White
    Write-Host "     - Open https://jobmatch.zip" -ForegroundColor Gray
    Write-Host "     - Open DevTools (F12) → Console" -ForegroundColor Gray
    Write-Host "     - Look for: 'Google Tag Manager initialized'" -ForegroundColor Gray
    Write-Host "     - Check Network tab for gtm.js requests" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  3. Test with GTM Preview:" -ForegroundColor White
    Write-Host "     - Go to https://tagmanager.google.com/" -ForegroundColor Gray
    Write-Host "     - Click 'Preview' button" -ForegroundColor Gray
    Write-Host "     - Enter: https://jobmatch.zip" -ForegroundColor Gray
} else {
    Write-Host "  ⚠️  GTM Setup Incomplete" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please fix the issues above and run this script again." -ForegroundColor White
}

Write-Host "================================================" -ForegroundColor Cyan

