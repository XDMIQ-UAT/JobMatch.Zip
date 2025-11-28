# Git Idle Agent - Auto-commit and sync script
# This script runs in the background to monitor git changes

param(
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Continue"

Write-Host "Git Idle Agent started at $(Get-Date)" -ForegroundColor Green

# Check if we're in a git repository
$isGitRepo = Test-Path .git
if (-not $isGitRepo) {
    Write-Host "Not a git repository. Exiting." -ForegroundColor Yellow
    exit 0
}

# Check for unstaged changes
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "Git changes detected:" -ForegroundColor Cyan
    Write-Host $gitStatus
    
    if ($DryRun) {
        Write-Host "[DRY RUN] Would commit and push changes" -ForegroundColor Yellow
    } else {
        # This is a background agent - don't auto-commit without explicit configuration
        Write-Host "Auto-commit disabled. Use git commands manually." -ForegroundColor Yellow
    }
} else {
    Write-Host "No git changes detected." -ForegroundColor Green
}

Write-Host "Git Idle Agent completed at $(Get-Date)" -ForegroundColor Green
exit 0
