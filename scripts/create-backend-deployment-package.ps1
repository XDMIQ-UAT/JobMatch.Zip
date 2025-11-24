# Create Backend Deployment Package
# Phase 1.2: Clean backend package for VM deployment
# Removes cache files and creates deployment-ready archive

$ErrorActionPreference = "Stop"

Write-Host "📦 Creating Backend Deployment Package..." -ForegroundColor Cyan
Write-Host ""

# Configuration
$backendSource = "E:\JobFinder\backend"
$tempDir = New-TemporaryFile | ForEach-Object { Remove-Item $_; New-Item -ItemType Directory -Path $_ }
$packageDir = Join-Path $tempDir "backend"
$outputZip = "E:\JobFinder\backend-deployment.zip"

Write-Host "🧹 Step 1: Cleaning and copying backend files..." -ForegroundColor Yellow

# Create package directory
New-Item -ItemType Directory -Path $packageDir -Force | Out-Null

# Copy backend files (exclude cache, compiled files, tests)
$excludePatterns = @(
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.pytest_cache',
    '*.log',
    'test_*.py',
    '*.backup.*',
    '.env',
    '*.ps1'  # Don't include PowerShell scripts
)

Get-ChildItem -Path $backendSource -Recurse | Where-Object {
    $item = $_
    $shouldExclude = $false
    
    foreach ($pattern in $excludePatterns) {
        if ($item.FullName -like "*$pattern*") {
            $shouldExclude = $true
            break
        }
    }
    
    -not $shouldExclude
} | ForEach-Object {
    $relativePath = $_.FullName.Substring($backendSource.Length + 1)
    $destPath = Join-Path $packageDir $relativePath
    $destDir = Split-Path $destPath -Parent
    
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    
    if (-not $_.PSIsContainer) {
        Copy-Item $_.FullName -Destination $destPath -Force
    }
}

Write-Host "✅ Files copied to staging area" -ForegroundColor Green
Write-Host ""

# Verify critical files exist
Write-Host "🔍 Step 2: Verifying package structure..." -ForegroundColor Yellow

$criticalFiles = @(
    "main.py",
    "config.py",
    "requirements.txt",
    "database\connection.py",
    "database\models.py",
    "auth\social_auth.py",
    "auth\email_provider.py",
    "auth\anonymous_identity.py",
    "api\auth.py",
    "api\social_auth.py"
)

$allPresent = $true
foreach ($file in $criticalFiles) {
    $fullPath = Join-Path $packageDir $file
    if (Test-Path $fullPath) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file MISSING!" -ForegroundColor Red
        $allPresent = $false
    }
}

if (-not $allPresent) {
    Write-Host ""
    Write-Host "❌ Package validation failed - missing critical files" -ForegroundColor Red
    Remove-Item $tempDir -Recurse -Force
    exit 1
}

Write-Host "✅ All critical files present" -ForegroundColor Green
Write-Host ""

# Create archive
Write-Host "📦 Step 3: Creating deployment archive..." -ForegroundColor Yellow

if (Test-Path $outputZip) {
    Remove-Item $outputZip -Force
}

Compress-Archive -Path $packageDir -DestinationPath $outputZip -CompressionLevel Optimal

$zipSize = (Get-Item $outputZip).Length / 1MB
Write-Host "✅ Package created: backend-deployment.zip ($([math]::Round($zipSize, 2)) MB)" -ForegroundColor Green
Write-Host ""

# Cleanup
Remove-Item $tempDir -Recurse -Force

# Summary
Write-Host "📋 Deployment Package Summary:" -ForegroundColor Cyan
Write-Host "  Location: $outputZip" -ForegroundColor White
Write-Host "  Size: $([math]::Round($zipSize, 2)) MB" -ForegroundColor White
Write-Host "  Ready for VM deployment" -ForegroundColor White
Write-Host ""
Write-Host "✅ Phase 1.2 Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review the package contents if needed" -ForegroundColor White
Write-Host "  2. Proceed to Phase 2: Backup VM and stop services" -ForegroundColor White
Write-Host "  3. Deploy using: .\scripts\deploy-backend-to-vm.ps1" -ForegroundColor White
