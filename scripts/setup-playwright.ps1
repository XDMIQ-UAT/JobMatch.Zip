#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Setup Playwright for JobFinder E2E Testing

.DESCRIPTION
    This script installs Playwright, browsers, and sets up the testing environment.

.EXAMPLE
    .\scripts\setup-playwright.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Playwright Setup for JobFinder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the project root
if (-not (Test-Path "package.json")) {
    Write-Error "Please run this script from the project root (E:\JobFinder)"
    exit 1
}

# Step 1: Install Playwright
Write-Host "[1/5] Installing Playwright..." -ForegroundColor Yellow
npm install -D @playwright/test

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install Playwright"
    exit 1
}

Write-Host "✓ Playwright installed successfully" -ForegroundColor Green
Write-Host ""

# Step 2: Install Browsers
Write-Host "[2/5] Installing Playwright browsers (this may take a few minutes)..." -ForegroundColor Yellow
npx playwright install

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install browsers"
    exit 1
}

Write-Host "✓ Browsers installed successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Create test directories
Write-Host "[3/5] Creating test directories..." -ForegroundColor Yellow
$directories = @(
    "tests\e2e",
    "test-results",
    "test-results\screenshots",
    "playwright-report"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Gray
    }
}

Write-Host "✓ Test directories created" -ForegroundColor Green
Write-Host ""

# Step 4: Setup environment variables
Write-Host "[4/5] Setting up environment variables..." -ForegroundColor Yellow

if (-not (Test-Path ".env.test")) {
    if (Test-Path ".env.test.example") {
        Copy-Item ".env.test.example" ".env.test"
        Write-Host "  Created .env.test from .env.test.example" -ForegroundColor Gray
        Write-Host "  ⚠ Please update .env.test with your test credentials" -ForegroundColor Yellow
    } else {
        Write-Host "  ⚠ .env.test.example not found, skipping" -ForegroundColor Yellow
    }
} else {
    Write-Host "  .env.test already exists" -ForegroundColor Gray
}

Write-Host "✓ Environment setup complete" -ForegroundColor Green
Write-Host ""

# Step 5: Verify installation
Write-Host "[5/5] Verifying installation..." -ForegroundColor Yellow

# Check if Playwright is installed
$playwrightVersion = npm list @playwright/test --depth=0 2>$null | Select-String "@playwright/test@"
if ($playwrightVersion) {
    Write-Host "  Playwright version: $($playwrightVersion)" -ForegroundColor Gray
} else {
    Write-Warning "  Could not verify Playwright installation"
}

Write-Host "✓ Verification complete" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete! 🎉" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Update .env.test with your test credentials" -ForegroundColor White
Write-Host "  2. Run tests: npm run test:e2e" -ForegroundColor White
Write-Host "  3. Run tests in UI mode: npm run test:e2e:ui" -ForegroundColor White
Write-Host "  4. View documentation: docs\PLAYWRIGHT_MCP_SETUP.md" -ForegroundColor White
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Yellow
Write-Host "  npm run test:e2e          - Run all E2E tests" -ForegroundColor White
Write-Host "  npm run test:e2e:ui       - Run tests in interactive UI mode" -ForegroundColor White
Write-Host "  npm run test:e2e:headed   - Run tests with visible browser" -ForegroundColor White
Write-Host "  npm run test:e2e:debug    - Run tests in debug mode" -ForegroundColor White
Write-Host "  npm run test:e2e:report   - View test report" -ForegroundColor White
Write-Host ""
Write-Host "MCP Integration:" -ForegroundColor Yellow
Write-Host "  You can now use Playwright browser tools directly through Warp AI!" -ForegroundColor White
Write-Host "  Try: 'Navigate to localhost:3000 and take a screenshot'" -ForegroundColor Gray
Write-Host ""
