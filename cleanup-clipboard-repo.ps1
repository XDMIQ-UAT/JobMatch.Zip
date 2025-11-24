# ============================================================================
# Cleanup Script for clipboard-to-pieces Repository
# ============================================================================
# This script removes log files from git history that were accidentally committed
# 
# WARNING: This rewrites git history. Anyone who has cloned the repo will need
# to re-clone after this is run.
# ============================================================================

$ErrorActionPreference = "Stop"

# Configuration
$REPO_URL = "https://github.com/XDM-ZSBW/clipboard-to-pieces.git"
$WORK_DIR = "$env:TEMP\clipboard-cleanup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$REPO_NAME = "clipboard-to-pieces"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Git History Cleanup for $REPO_NAME" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check prerequisites
Write-Host "Step 1: Checking prerequisites..." -ForegroundColor Yellow

# Check if git-filter-repo is available
$filterRepoAvailable = $null -ne (Get-Command git-filter-repo -ErrorAction SilentlyContinue)

if (-not $filterRepoAvailable) {
    Write-Host "❌ git-filter-repo not found. Installing..." -ForegroundColor Red
    Write-Host "Installing git-filter-repo via pip..." -ForegroundColor Yellow
    
    # Check if Python is available
    $pythonAvailable = $null -ne (Get-Command python -ErrorAction SilentlyContinue)
    if (-not $pythonAvailable) {
        Write-Host "❌ Python is not installed. Please install Python first." -ForegroundColor Red
        Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
    
    python -m pip install git-filter-repo
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install git-filter-repo" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Prerequisites met" -ForegroundColor Green
Write-Host ""

# Step 2: Create working directory
Write-Host "Step 2: Setting up workspace..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $WORK_DIR | Out-Null
Set-Location $WORK_DIR
Write-Host "✅ Workspace created: $WORK_DIR" -ForegroundColor Green
Write-Host ""

# Step 3: Clone repository
Write-Host "Step 3: Cloning repository..." -ForegroundColor Yellow
git clone $REPO_URL
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to clone repository" -ForegroundColor Red
    exit 1
}
Set-Location $REPO_NAME
Write-Host "✅ Repository cloned" -ForegroundColor Green
Write-Host ""

# Step 4: Show what will be removed
Write-Host "Step 4: Files to be removed from history:" -ForegroundColor Yellow
$filesToRemove = @(
    "clipboard_service.log",
    "enhanced_clipboard_monitor.log",
    "pieces_mcp_bridge.log",
    "simple_clipboard_monitor.log",
    "processing_state.json",
    "vault/src/server.log",
    "vault/src/server_error.log",
    "vault/src/server_error_new.log",
    "vault/src/server_new.log",
    "vault_clipboard_service.log"
)

foreach ($file in $filesToRemove) {
    $exists = Test-Path $file
    $status = if ($exists) { "🔴 EXISTS" } else { "✅ REMOVED" }
    Write-Host "  $status : $file" -ForegroundColor $(if ($exists) { "Red" } else { "Green" })
}
Write-Host ""

# Step 5: Confirm action
Write-Host "⚠️  WARNING: This will rewrite git history!" -ForegroundColor Red
Write-Host "   Anyone who has cloned this repo will need to re-clone it." -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Continue? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "❌ Aborted by user" -ForegroundColor Yellow
    exit 0
}
Write-Host ""

# Step 6: Remove files from history
Write-Host "Step 6: Removing files from git history..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray

foreach ($file in $filesToRemove) {
    Write-Host "  Removing: $file" -ForegroundColor Gray
    git filter-repo --path $file --invert-paths --force
}

Write-Host "✅ Files removed from history" -ForegroundColor Green
Write-Host ""

# Step 7: Update .gitignore
Write-Host "Step 7: Updating .gitignore..." -ForegroundColor Yellow

$gitignorePath = ".gitignore"
$gitignoreContent = Get-Content $gitignorePath -Raw

# Patterns to add
$patternsToAdd = @"

# ============================================================================
# Runtime files (added by security cleanup)
# ============================================================================
# All log files
*.log

# State files
*_state.json
processing_state.json

# Vault runtime data
vault/data/
vault/logs/
vault/src/*.log
"@

# Check if patterns already exist
if ($gitignoreContent -notmatch "\*\.log") {
    Add-Content $gitignorePath $patternsToAdd
    Write-Host "✅ .gitignore updated" -ForegroundColor Green
} else {
    Write-Host "✅ .gitignore already contains necessary patterns" -ForegroundColor Green
}

# Commit .gitignore changes
git add .gitignore
git commit -m "security: update .gitignore to prevent log file commits" -m "- Add *.log to prevent any log files from being committed" -m "- Add *_state.json to prevent state files" -m "- Add vault runtime directories" -m "" -m "Refs: Security audit cleanup"

Write-Host ""

# Step 8: Verify cleanup
Write-Host "Step 8: Verifying cleanup..." -ForegroundColor Yellow
$remainingFiles = git log --all --full-history --name-only --format="" | Select-String -Pattern "\.log$|_state\.json$" | Select-Object -Unique

if ($remainingFiles) {
    Write-Host "⚠️  Some files may still be in history:" -ForegroundColor Yellow
    $remainingFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
} else {
    Write-Host "✅ All log files successfully removed from history" -ForegroundColor Green
}
Write-Host ""

# Step 9: Show repository size change
Write-Host "Step 9: Repository size change:" -ForegroundColor Yellow
$repoSize = (Get-ChildItem -Recurse .git | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "  Current size: $($repoSize.ToString('F2')) MB" -ForegroundColor Cyan
Write-Host ""

# Step 10: Final instructions
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Review the changes in: $WORK_DIR\$REPO_NAME" -ForegroundColor White
Write-Host "2. Test that the repository works correctly" -ForegroundColor White
Write-Host "3. Force push to GitHub:" -ForegroundColor White
Write-Host "   cd `"$WORK_DIR\$REPO_NAME`"" -ForegroundColor Gray
Write-Host "   git push --force origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Notify collaborators to re-clone the repository" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  IMPORTANT: " -ForegroundColor Red
Write-Host "   - This rewrites history. All clones need to be refreshed." -ForegroundColor Yellow
Write-Host "   - Anyone with the old repo should delete and re-clone." -ForegroundColor Yellow
Write-Host ""

# Open the directory in explorer
explorer.exe $WORK_DIR
